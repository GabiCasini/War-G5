import pytest

from back.model.Jogador import Jogador
from back.model.Partida import Partida

# Mocks auxiliares
@pytest.fixture
def tupla_jogadores():
    jogadores = [["Alice", "red"], ["Bob", "blue"], ["Charlie", "green"]]
    return jogadores

@pytest.fixture
def partida(tupla_jogadores):
    return Partida(qtd_humanos=3, qtd_ai=0, duracao_turno=60, tupla_jogadores=tupla_jogadores)

def test_resolver_combate(partida: Partida):
    jogador_a: Jogador = partida.jogadores[0]
    jogador_b: Jogador = partida.jogadores[1]

    territorio_a = jogador_a.territorios[0]
    territorio_b = jogador_b.territorios[0]

    jogador_a.adicionar_exercitos_territorio(territorio_a, 5)
    jogador_b.adicionar_exercitos_territorio(territorio_b, 3)

    conquistado = partida.resolver_combate(jogador_a, jogador_b, territorio_a, territorio_b)

    assert isinstance(conquistado, bool)
    # assert ...
    # assert ...
