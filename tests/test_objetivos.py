from back.model.Partida import Partida
from back.model.Jogador import Jogador


# FUNÇÕES AUXILIARES

def limpar_territorios_dos_jogadores(partida: Partida):
    """Remove todos os territórios do tabuleiro e dos jogadores, para criarmos territórios customizados por teste."""
    for j in partida.jogadores:
        j.territorios = []

    for t in partida.tabuleiro.territorios:
        t.cor = ""


def marcar_regiao_completa(partida, jogador: Jogador, indices):
    """
    Marca regiões no tabuleiro como dominadas pelo jogador.
    regioes_com_bonus[idx][2] representa a lista de territorios da Região_{idx}.
    """
    for idx in indices:
        for t in partida.tabuleiro.regioes_com_bonus[idx][2]:
            jogador.adicionar_territorio(t)


def remover_regiao_completa(partida, jogador: Jogador, indices):
    for idx in indices:
        for t in partida.tabuleiro.regioes_com_bonus[idx][2]:
            jogador.remover_territorio(t)
            t.cor = ""


# TESTE PARA GARANTIR QUE TODOS OS JOGADORES NA PARTIDA POSSUEM OBJETIVOS ATRIBUÍDOS

def test_distribuicao_de_objetivos(partida: Partida):
    for j in partida.jogadores:
        assert j.objetivo is not None


# TESTES PARA OBJETIVOS DE CONQUISTAR TERRITÓRIOS

def test_objetivo_conquistar_18_territorios_com_2_exercitos(partida: Partida):
    jogador: Jogador = partida.jogadores[0]
    jogador.objetivo = "Conquistar 18 territórios e ocupar cada um deles com pelo menos 2 exércitos"

    i = 0
    while (len(jogador.territorios)) < 18:
        if partida.tabuleiro.territorios[i].cor != jogador.cor:
            jogador.adicionar_territorio(partida.tabuleiro.territorios[i])

        i += 1

    for t in jogador.territorios:
        t.exercitos = 2

    assert partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)

    jogador.territorios[0].exercitos = 1

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)


def test_objetivo_conquistar_24_territorios(partida: Partida):
    jogador: Jogador = partida.jogadores[0]
    jogador.objetivo = "Conquistar 24 territórios à sua escolha"

    i = 0
    while (len(jogador.territorios)) < 23:
        if partida.tabuleiro.territorios[i].cor != jogador.cor:
            jogador.adicionar_territorio(partida.tabuleiro.territorios[i])

        i += 1

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)

    while (len(jogador.territorios)) < 24:
        if partida.tabuleiro.territorios[i].cor != jogador.cor:
            jogador.adicionar_territorio(partida.tabuleiro.territorios[i])

        i += 1

    assert partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)


# TESTES PARA OBJETIVOS DE REGIÕES

def test_objetivo_regiao_2_e_5(partida: Partida):
    jogador = partida.jogadores[0]
    limpar_territorios_dos_jogadores(partida)
    
    jogador.objetivo = "Conquistar na totalidade a Região 2 e a Região 5"
    marcar_regiao_completa(partida, jogador, [1, 4])

    assert partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)

    remover_regiao_completa(partida, jogador, [1])
    marcar_regiao_completa(partida, jogador, [0, 2, 3, 5])

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)

    remover_regiao_completa(partida, jogador, [4])
    marcar_regiao_completa(partida, jogador, [1])

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)


def test_objetivo_regiao_4_e_5(partida: Partida):
    jogador = partida.jogadores[0]
    limpar_territorios_dos_jogadores(partida)
    
    jogador.objetivo = "Conquistar na totalidade a Região 4 e a Região 5"
    marcar_regiao_completa(partida, jogador, [3, 4])

    assert partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)

    remover_regiao_completa(partida, jogador, [3])
    marcar_regiao_completa(partida, jogador, [0, 1, 2, 5])

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)

    remover_regiao_completa(partida, jogador, [4])
    marcar_regiao_completa(partida, jogador, [3])

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)


def test_objetivo_regiao_2_e_6(partida: Partida):
    jogador = partida.jogadores[0]
    limpar_territorios_dos_jogadores(partida)
    
    jogador.objetivo = "Conquistar na totalidade a Região 2 e a Região 6"
    marcar_regiao_completa(partida, jogador, [1, 5])

    assert partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)

    remover_regiao_completa(partida, jogador, [1])
    marcar_regiao_completa(partida, jogador, [0, 2, 3, 4])

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)

    remover_regiao_completa(partida, jogador, [5])
    marcar_regiao_completa(partida, jogador, [1])

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)


def test_objetivo_regiao_1_e_4(partida: Partida):
    jogador = partida.jogadores[0]
    limpar_territorios_dos_jogadores(partida)
    
    jogador.objetivo = "Conquistar na totalidade a Região 1 e a Região 4"
    marcar_regiao_completa(partida, jogador, [0, 3])

    assert partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)

    remover_regiao_completa(partida, jogador, [0])
    marcar_regiao_completa(partida, jogador, [1, 2, 4, 5])

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)

    remover_regiao_completa(partida, jogador, [3])
    marcar_regiao_completa(partida, jogador, [0])

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)


def test_objetivo_regiao_1_3_e_mais_uma(partida: Partida):
    jogador = partida.jogadores[0]
    limpar_territorios_dos_jogadores(partida)
    
    jogador.objetivo = "Conquistar na totalidade a Região 1, a Região 3 e mais uma Região à sua escolha"
    marcar_regiao_completa(partida, jogador, [0, 2])

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)

    marcar_regiao_completa(partida, jogador, [1])

    assert partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)

    remover_regiao_completa(partida, jogador, [0])
    marcar_regiao_completa(partida, jogador, [3, 4, 5])

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)

    remover_regiao_completa(partida, jogador, [2])
    marcar_regiao_completa(partida, jogador, [0])

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)


def test_objetivo_regiao_3_6_e_mais_uma(partida: Partida):
    jogador = partida.jogadores[0]
    limpar_territorios_dos_jogadores(partida)
    
    jogador.objetivo = "Conquistar na totalidade a Região 3, a Região 6 e mais uma Região à sua escolha"
    marcar_regiao_completa(partida, jogador, [2, 5])

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)

    marcar_regiao_completa(partida, jogador, [0])

    assert partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)

    remover_regiao_completa(partida, jogador, [2])
    marcar_regiao_completa(partida, jogador, [1, 3, 4])

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)

    remover_regiao_completa(partida, jogador, [5])
    marcar_regiao_completa(partida, jogador, [2])

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador, partida.jogadores_eliminados, partida.tabuleiro)


# OBJETIVO DE ELIMINAR UM JOGADOR

def test_objetivo_eliminar_jogador(partida: Partida):
    atacante = partida.jogadores[0]
    defensor = partida.jogadores[1]

    atacante.objetivo = "Elimine o jogador " + defensor.cor + ". Caso você seja esse jogador, ou ele já tenha sido eliminado, seu objetivo passa a ser conquistar 24 territórios"

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(atacante, partida.jogadores_eliminados, partida.tabuleiro)

    partida.jogadores.remove(defensor)
    defensor.territorios = []
    defensor.eliminado_por = atacante.cor
    partida.jogadores_eliminados.append(defensor)

    assert partida.manager_de_objetivos.verifica_objetivo_do_jogador(atacante, partida.jogadores_eliminados, partida.tabuleiro)

    defensor.eliminado_por = "nenhum"

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(atacante, partida.jogadores_eliminados, partida.tabuleiro)

    i = 0
    while (len(atacante.territorios)) < 24:
        if partida.tabuleiro.territorios[i].cor != atacante.cor:
            atacante.adicionar_territorio(partida.tabuleiro.territorios[i])

        i += 1

    assert partida.manager_de_objetivos.verifica_objetivo_do_jogador(atacante, partida.jogadores_eliminados, partida.tabuleiro)

    partida.jogadores_eliminados.remove(defensor)

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(atacante, partida.jogadores_eliminados, partida.tabuleiro)

    atacante.objetivo = "Elimine o jogador " + atacante.cor + ". Caso você seja esse jogador, ou ele já tenha sido eliminado, seu objetivo passa a ser conquistar 24 territórios"

    assert partida.manager_de_objetivos.verifica_objetivo_do_jogador(atacante, partida.jogadores_eliminados, partida.tabuleiro)

    atacante.territorios = []

    assert not partida.manager_de_objetivos.verifica_objetivo_do_jogador(atacante, partida.jogadores_eliminados, partida.tabuleiro)
