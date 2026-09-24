"""Infraestrutura comum dos coletores.

- `Cliente`: sessão HTTP com tempo limite, novas tentativas com espera exponencial (429 e 5xx,
  respeitando Retry-After) e pausa mínima entre requisições. HTTP 403 interrompe a coleta com
  `AcessoBloqueado`: bloqueios não são contornados (docs/decisoes_metodologicas.md, D-009).
- `Execucao`: grava cada resposta, sem alteração, em data/raw/<fonte>/<AAAA-MM-DD>/<arquivo>.jsonl
  (uma linha por requisição, com URL, parâmetros, status, horário e corpo) e, ao fechar, acrescenta
  uma linha por arquivo ao manifesto data/manifestos/<fonte>.csv (tamanho e sha256).
- `registrar_busca`: acrescenta a consulta lógica à tabela `buscas` (só cresce).
"""

import csv
import datetime as dt
import hashlib
import json
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.base import BASE, RAIZ, RegistroIds, acrescentar

USER_AGENT = "pesquisa-poder-institucional/0.1 (pesquisa documental com dados abertos)"
RAW = RAIZ / "data" / "raw"
MANIFESTOS = RAIZ / "data" / "manifestos"
LIMITE_ARQUIVO = 50 * 1024 * 1024


class AcessoBloqueado(RuntimeError):
    pass


class Cliente:
    def __init__(self, pausa: float = 0.25, tempo_limite: int = 60):
        self.pausa, self.tempo_limite = pausa, tempo_limite
        self.sessao = requests.Session()
        self.sessao.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
        tentativa = Retry(total=6, backoff_factor=2, status_forcelist=(429, 500, 502, 503, 504),
                          allowed_methods=("GET", "HEAD", "POST"), respect_retry_after_header=True)
        self.sessao.mount("https://", HTTPAdapter(max_retries=tentativa))
        self._ultima = 0.0
        self.n_requisicoes = 0

    def get(self, url: str, params: dict | None = None, headers: dict | None = None) -> requests.Response:
        return self._requisitar("GET", url, params=params, headers=headers)

    def post(self, url: str, json_corpo: dict, headers: dict | None = None) -> requests.Response:
        return self._requisitar("POST", url, json=json_corpo, headers=headers)

    def _requisitar(self, metodo: str, url: str, **kw) -> requests.Response:
        espera = self.pausa - (time.monotonic() - self._ultima)
        if espera > 0:
            time.sleep(espera)
        r = self.sessao.request(metodo, url, timeout=self.tempo_limite, **kw)
        self._ultima = time.monotonic()
        self.n_requisicoes += 1
        if r.status_code == 403:
            raise AcessoBloqueado(f"HTTP 403 em {r.url}: a fonte recusa cliente automatizado; coleta interrompida (D-009)")
        return r


def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


class Execucao:
    """Uma coleta de uma fonte em um dia. Os arquivos brutos nunca são sobrescritos."""

    def __init__(self, fonte: str, data: str | None = None, raiz_raw: Path = RAW, manifestos: Path = MANIFESTOS):
        self.fonte = fonte
        self.data = data or dt.date.today().isoformat()
        self.pasta = raiz_raw / fonte / self.data
        self.manifestos = manifestos
        self.arquivos: dict[str, dict] = {}
        self._abertos: dict[str, object] = {}

    def gravar(self, arquivo: str, url_base: str, resposta: requests.Response, params: dict | None = None) -> dict | list | None:
        if arquivo not in self._abertos:
            destino = self.pasta / arquivo
            if destino.exists():
                raise FileExistsError(f"{destino} já existe: data/raw é imutável; use outra data de coleta")
            self.pasta.mkdir(parents=True, exist_ok=True)
            self._abertos[arquivo] = destino.open("w", encoding="utf-8", newline="\n")
            self.arquivos[arquivo] = {"url_base": url_base, "n_requisicoes": 0}
        try:
            corpo = resposta.json()
        except ValueError:
            corpo = None
        linha = {"url": resposta.url, "params": params or {}, "status": resposta.status_code,
                 "obtido_em": dt.datetime.now().isoformat(timespec="seconds"), "corpo": corpo,
                 "texto": None if corpo is not None else resposta.text[:2000]}
        self._abertos[arquivo].write(json.dumps(linha, ensure_ascii=False) + "\n")
        self.arquivos[arquivo]["n_requisicoes"] += 1
        return corpo

    def baixar(self, cliente: "Cliente", url: str, arquivo: str) -> Path:
        """Baixa um arquivo inteiro (planilha, pacote de dados) sem alteração."""
        destino = self.pasta / arquivo
        if destino.exists():
            raise FileExistsError(f"{destino} já existe: data/raw é imutável; use outra data de coleta")
        r = cliente.get(url, headers={"Accept": "*/*"})  # arquivos (Word, PDF, ZIP): sem exigir JSON
        r.raise_for_status()
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(r.content)
        self.arquivos[arquivo] = {"url_base": url, "n_requisicoes": 1}
        return destino

    def fechar(self) -> list[dict]:
        for f in self._abertos.values():
            f.close()
        self._abertos.clear()
        self.manifestos.mkdir(parents=True, exist_ok=True)
        manifesto = self.manifestos / f"{self.fonte}.csv"
        novo = not manifesto.exists()
        registros = []
        with manifesto.open("a", encoding="utf-8", newline="") as m:
            w = csv.DictWriter(m, fieldnames=["data_acesso", "arquivo", "url_base", "n_requisicoes", "bytes", "sha256"], lineterminator="\n")
            if novo:
                w.writeheader()
            for nome, info in self.arquivos.items():
                caminho = self.pasta / nome
                reg = {"data_acesso": self.data, "arquivo": caminho.relative_to(RAIZ).as_posix(), "url_base": info["url_base"],
                       "n_requisicoes": info["n_requisicoes"], "bytes": caminho.stat().st_size, "sha256": sha256(caminho)}
                if reg["bytes"] > LIMITE_ARQUIVO:
                    print(f"AVISO: {nome} passou de 50 MB ({reg['bytes'] / 1e6:.0f} MB)")
                w.writerow(reg)
                registros.append(reg)
        return registros


def registrar_busca(fonte_dados: str, consulta: str, n_resultados: int, script: str, data: str,
                    parametros: dict | None = None, arquivo: dict | None = None,
                    ids: RegistroIds | None = None, base: Path = BASE) -> str:
    ids = ids or RegistroIds(base=base)
    chave = f"{script}|{data}|{consulta}"
    ident = ids.obter("buscas", chave)
    acrescentar("buscas", [{
        "id_busca": ident, "data": data, "fonte_dados": fonte_dados, "consulta": consulta,
        "parametros_json": json.dumps(parametros or {}, ensure_ascii=False, sort_keys=True),
        "n_resultados": str(n_resultados), "sha256_resposta": (arquivo or {}).get("sha256", ""),
        "caminho_raw": (arquivo or {}).get("arquivo", ""), "script": script,
    }], base)
    return ident
