# data/raw

Downloads originais, imutáveis e fora do Git. Organização: `data/raw/<fonte>/<AAAA-MM-DD>/`.
Cada arquivo tem uma linha em `data/manifestos/` (URL, data de acesso, sha256) e a consulta que o
gerou tem uma linha em `data/base/buscas.csv`. Correções vão para `data/staging/`, nunca aqui.
