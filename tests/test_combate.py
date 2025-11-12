from back.model.Jogador import Jogador
from back.model.Partida import Partida
from back.model.Territorio import Territorio

def test_resolver_combate(partida: Partida):
    jogador_a: Jogador = partida.jogadores[0]
    jogador_b: Jogador = partida.jogadores[1]

    territorio_a: Territorio = jogador_a.territorios[0]
    territorio_b: Territorio = jogador_b.territorios[0]

    jogador_a.adicionar_exercitos_territorio(territorio_a, 5)
    jogador_b.adicionar_exercitos_territorio(territorio_b, 3)

    assert territorio_a.exercitos == 6
    assert territorio_b.exercitos == 4

    resp = partida.resolver_combate(jogador_a, jogador_b, territorio_a, territorio_b)
    assert isinstance(resp["territorio_conquistado"], bool)

    perdas_a = resp["perdas_ataque"]
    perdas_b = resp["perdas_defesa"]

    assert territorio_a.exercitos == 6 - perdas_a
    assert territorio_b.exercitos == 4 - perdas_b

def test_eliminacao(partida: Partida):
    jogador_a: Jogador = partida.jogadores[0]
    jogador_b: Jogador = partida.jogadores[1]

    # Forçar jogador_b a ter nenhum território 
    jogador_b.territorios = []
    eliminado = partida.verificar_eliminacao(jogador_a, jogador_b)

    assert eliminado
    assert jogador_b in partida.jogadores_eliminados
    assert jogador_b.eliminado_por == jogador_a.cor
