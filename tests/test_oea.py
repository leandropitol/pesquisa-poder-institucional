"""Leitura de votações nominais e notas de rodapé da OEA (bloco A3). Atas e notas fictícias."""

from src.normalizacao.oea_base import autor_nota, autores_das_notas
from src.normalizacao.oea_votos import (bloco_da_chamada, ler_votos, normalizar_voto, numeros, pais_no_rotulo,
                                        placar_confere_ancora, turnos)

ATA = (
    "El PRESIDENTE: " + "Explicação longa do procedimento de votação. " * 20 + "Comenzamos. "
    "El PRESIDENTE: Brasil. El JEFE DE LA DELEGACIÓN DEL BRASIL: Sim. "
    "El PRESIDENTE: Chile. La REPRESENTANTE DE CHILE: En contra. "
    "El SECRETARIO GENERAL ADJUNTO: The delegation of Canada, how do you vote? El REPRESENTANTE PERMANENTE DEL CANADÁ: Thank you, Mr. President. "
    "El SECRETARIO GENERAL ADJUNTO: Canada votes in favor. "
    "El PRESIDENTE: Uruguay, no está presente. Haití. El JEFE DE LA DELEGACIÓN DE HAITÍ: Haïti vote en faveur. "
    "El PRESIDENTE: San Vicente. El JEFE DE LA DELEGACIÓN DE SAN VICENTE Y LAS GRENADINAS: Abstain. "
    "El PRESIDENTE: El resultado de la votación es el siguiente: tres votos a favor; 1 en contra, y una abstención. "
)


def test_normalizar_voto_em_varias_linguas():
    assert normalizar_voto("Sim.") == "sim"
    assert normalizar_voto("Brasil vota a favor.") == "sim"
    assert normalizar_voto("In support") == "sim"
    assert normalizar_voto("Haïti vote en faveur") == "sim"
    assert normalizar_voto("Rotundamente en contra.") == "nao"
    assert normalizar_voto("Opposed.") == "nao"
    assert normalizar_voto("Abstenção.") == "abstencao"
    assert normalizar_voto("Thank you, Mr. President.") is None


def test_pais_no_rotulo_com_grafia_truncada():
    assert pais_no_rotulo("JEFE DE LA DELEGACIÓN DE SAINT KITTS AND ENEVIS") == "KNA"
    assert pais_no_rotulo("REPRESENTANTE PERMANENTE DE LOS ESTADOS UNIDOS MEXICANOS") == "MEX"
    assert pais_no_rotulo("REPRESENTANTE PERMANENTE DE LA REPÚBLICA DOMINICANA") == "DOM"
    assert pais_no_rotulo("PRESIDENTE") is None


def test_numeros_por_extenso_e_placar_conferido():
    assert {21, 4, 9} <= numeros("twenty-one in favor, four, no, and nine abstentions")
    assert {25, 1, 7} <= numeros("veinticinco votos a favor, uno en contra, y siete abstenciones")
    assert placar_confere_ancora({"sim": 3, "nao": 1, "abstencao": 1, "ausente": 0}, "tres votos a favor; 1 en contra, y una abstención") == []
    assert placar_confere_ancora({"sim": 4, "nao": 1, "abstencao": 1, "ausente": 0}, "tres votos a favor; 1 en contra, y una abstención") == ["sim"]


def test_chamada_le_respostas_e_repeticao_da_mesa_sem_tomar_ausencia_por_voto():
    pos = ATA.find("El resultado de la votación")
    votos, trechos = ler_votos(bloco_da_chamada(turnos(ATA), pos))
    assert votos == {"BRA": "sim", "CHL": "nao", "CAN": "sim", "HTI": "sim", "VCT": "abstencao"}
    assert "URY" not in votos  # "no está presente" é ausência
    assert trechos["BRA"] == "JEFE DE LA DELEGACIÓN DEL BRASIL: Sim."
    assert "repetição da mesa" in trechos["CAN"]


def test_bloco_da_chamada_para_na_fala_longa():
    pos = ATA.find("El resultado de la votación")
    bloco = bloco_da_chamada(turnos(ATA), pos)
    assert all(len(fala) <= 600 for _, _, _, fala in bloco)
    assert bloco[0][3] == "Brasil."


def test_autor_da_nota_e_notas_que_remetem_a_outras():
    assert autor_nota(". La Delegación de Brasil no apoya el párrafo 3.") == "BRA"
    assert autor_nota("Los Estados Unidos Mexicanos se apartan del consenso.") == "MEX"
    assert autor_nota("Creado de conformidad con la resolución AG/RES. 1.") is None
    notas = [(0, "1", "El Gobierno de Chile no acompaña."), (1, "2", "Ídem."), (2, "3", "Véase nota a pie de página 1."), (3, "4", "Texto sem país.")]
    assert autores_das_notas(notas) == {"1": "CHL", "2": "CHL", "3": "CHL", "4": None}
