from back.model.Partida import Partida
from back.model.Jogador import Jogador


def test_incrementar_valor_da_troca(partida: Partida):
    valores = []

    for _ in range(10):
        valores.append(partida.valor_da_troca)
        partida.incrementar_troca()

    assert valores == [4, 6, 8, 10, 12, 15, 20, 25, 30, 35]


def test_ganho_de_carta_e_atribuicao(partida: Partida):
    jogador: Jogador = partida.jogadores[0]
    partida.conquistou_algum_territorio = False
    partida.verifica_ganho_de_carta(jogador)

    assert len(jogador.cartas) == 0

    territorios_disponiveis_inicialmente = len(partida.manager_de_cartas.territorios_disponiveis)

    partida.conquistou_algum_territorio = True
    partida.verifica_ganho_de_carta(jogador)
    partida.verifica_ganho_de_carta(jogador)
    partida.verifica_ganho_de_carta(jogador)

    assert len(jogador.cartas) == 3

    partida.verifica_ganho_de_carta(jogador)
    partida.verifica_ganho_de_carta(jogador)
    partida.verifica_ganho_de_carta(jogador)

    assert len(jogador.cartas) == 5

    total = 0
    for c in jogador.cartas:
        if c[0] != "Coringa":
            total += 1

            assert c[1] in partida.manager_de_cartas.territorios_em_uso

    assert territorios_disponiveis_inicialmente == 42
    assert (territorios_disponiveis_inicialmente - total) == len(partida.manager_de_cartas.territorios_disponiveis)
    assert total == len(partida.manager_de_cartas.territorios_em_uso)


def test_realizar_passagem_de_cartas_apos_eliminacao(partida: Partida):
    jogador_a: Jogador = partida.jogadores[0]
    jogador_b: Jogador = partida.jogadores[1]

    assert jogador_a.cartas == []
    assert jogador_b.cartas == []

    partida.conquistou_algum_territorio = True
    partida.verifica_ganho_de_carta(jogador_a)
    partida.verifica_ganho_de_carta(jogador_a)
    partida.verifica_ganho_de_carta(jogador_a)

    partida.verifica_ganho_de_carta(jogador_b)
    partida.verifica_ganho_de_carta(jogador_b)
    partida.verifica_ganho_de_carta(jogador_b)
    partida.verifica_ganho_de_carta(jogador_b)
    partida.verifica_ganho_de_carta(jogador_b)

    jogador_b.territorios = []
    partida.verificar_eliminacao(jogador_a, jogador_b)

    assert len(jogador_a.cartas) == 5

    total = 0
    for c in jogador_a.cartas:
        if c[0] != "Coringa":
            total += 1

            assert c[1] in partida.manager_de_cartas.territorios_em_uso
    
    assert total == len(partida.manager_de_cartas.territorios_em_uso)
    assert (len(partida.manager_de_cartas.territorios_disponiveis) + total) == 42


def test_realizar_troca_de_cartas(partida: Partida):
    jogador: Jogador = partida.jogadores[0]
    troca = []

    territorio = partida.manager_de_cartas.territorios_disponiveis.pop()
    partida.manager_de_cartas.territorios_em_uso.append(territorio)
    jogador.cartas.append(["Círculo", territorio])
    troca.append(["Círculo", territorio])

    partida.realizar_troca(jogador, troca)

    assert len(jogador.cartas) == 1

    territorio = partida.manager_de_cartas.territorios_disponiveis.pop()
    partida.manager_de_cartas.territorios_em_uso.append(territorio)
    jogador.cartas.append(["Quadrado", territorio])
    troca.append(["Quadrado", territorio])

    territorio = partida.manager_de_cartas.territorios_disponiveis.pop()
    partida.manager_de_cartas.territorios_em_uso.append(territorio)
    jogador.cartas.append(["Triângulo", territorio])
    troca.append(["Triângulo", territorio])

    valor = partida.valor_da_troca
    exercitos = jogador.exercitos_reserva

    jogador.cartas.append(["Coringa", ""])
    jogador.cartas.append(["Coringa", ""])

    partida.realizar_troca(jogador, troca)

    assert len(jogador.cartas) == 2
    assert (valor + exercitos) == jogador.exercitos_reserva

    partida.realizar_troca(jogador, troca)

    assert len(jogador.cartas) == 2
    assert (valor + exercitos) == jogador.exercitos_reserva

    jogador.cartas.append(["Coringa", ""])

    valor = partida.valor_da_troca
    exercitos = jogador.exercitos_reserva

    partida.realizar_troca(jogador, [["Coringa", ""], ["Coringa", ""], ["Coringa", ""]])

    assert len(jogador.cartas) == 0
    assert (valor + exercitos) == jogador.exercitos_reserva

    jogador.cartas.append(["Coringa", ""])
    partida.realizar_troca(jogador, [["Coringa", ""]])

    assert len(jogador.cartas) == 1
    assert (valor + exercitos) == jogador.exercitos_reserva
