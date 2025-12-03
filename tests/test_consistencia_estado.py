import pytest
from back import state
from back.model.Partida import Partida

def contar_total_territorios(partida):
    
    return sum(len(j.territorios) for j in partida.jogadores)


def contar_total_exercitos(partida):
    
    return sum(
        sum(t.exercitos for t in j.territorios) 
        for j in partida.jogadores
    )


def obter_cores_unicas(partida):
    
    return {t.cor for t in partida.tabuleiro.territorios}


def validar_territorios_nao_duplicados(partida):
    
    territorios_vistos = set()
    for jogador in partida.jogadores:
        for territorio in jogador.territorios:
            if territorio in territorios_vistos:
                return False
            territorios_vistos.add(territorio)
    return True

def test_consistencia_total_territorios_partida(client_com_partida):
    
    partida = state.partida_global
    
    total_tabuleiro = len(partida.tabuleiro.territorios)
    total_distribuido = contar_total_territorios(partida)
    
    assert total_tabuleiro == total_distribuido


def test_consistencia_nenhum_territorio_duplicado(client_com_partida):

    partida = state.partida_global
    
    assert validar_territorios_nao_duplicados(partida)


def test_consistencia_todos_territorios_tem_proprietario(client_com_partida):

    partida = state.partida_global
    
    for territorio in partida.tabuleiro.territorios:
        # Deve ter uma cor válida
        assert territorio.cor in [j.cor for j in partida.jogadores]


def test_consistencia_cor_territorio_matches_proprietario(client_com_partida):
    
    partida = state.partida_global
    
    for jogador in partida.jogadores:
        for territorio in jogador.territorios:
            assert territorio.cor == jogador.cor


def test_consistencia_territorio_nao_desaparece_apos_turno(client_com_partida):
    
    partida = state.partida_global
    
    total_antes = contar_total_territorios(partida)
    
    # Passa 3 turnos
    for _ in range(3):
        partida.proximo_jogador()
    
    total_depois = contar_total_territorios(partida)
    
    assert total_antes == total_depois

def test_consistencia_exercitos_nao_negativos(client_com_partida):
    
    partida = state.partida_global
    
    for territorio in partida.tabuleiro.territorios:
        assert territorio.exercitos >= 0


def test_consistencia_exercitos_minimo_um(client_com_partida):
    
    partida = state.partida_global
    
    for jogador in partida.jogadores:
        for territorio in jogador.territorios:
            assert territorio.exercitos >= 1


def test_consistencia_total_exercitos_apos_ataque(client_com_partida):
    
    partida = state.partida_global
    
    # Setup ataque
    jogador_a = partida.jogadores[0]
    jogador_b = partida.jogadores[1]
    territorio_a = partida.tabuleiro.territorios[0]
    territorio_b = territorio_a.fronteiras[0]
    
    territorio_a.cor = jogador_a.cor
    territorio_b.cor = jogador_b.cor
    territorio_a.exercitos = 10
    territorio_b.exercitos = 2
    
    jogador_a.territorios = [territorio_a]
    jogador_b.territorios = [territorio_b]
    
    total_antes = contar_total_exercitos(partida)
    
    # Executa ataque (simulado)
    response = client_com_partida.post('/partida/ataque', json={
        'territorio_origem': territorio_a.nome,
        'territorio_ataque': territorio_b.nome,
        'jogador_id': jogador_a.cor
    })
    
    total_depois = contar_total_exercitos(partida)
    
    # Total pode diminuir (perdas), mas não aumentar
    assert total_depois <= total_antes


def test_consistencia_exercitos_para_posicionar_nao_negativo(client_com_partida):
    
    partida = state.partida_global
    
    for jogador in partida.jogadores:
        assert jogador.exercitos_reserva >= 0

def test_consistencia_numero_jogadores(client_com_partida):
    
    partida = state.partida_global
    
    # Deve ter 3 jogadores (conforme fixture)
    assert len(partida.jogadores) == 3


def test_consistencia_cores_jogadores_unicas(client_com_partida):
    
    partida = state.partida_global
    
    cores = [j.cor for j in partida.jogadores]
    assert len(cores) == len(set(cores))


def test_consistencia_nomes_jogadores_nao_vazios(client_com_partida):
    
    partida = state.partida_global
    
    for jogador in partida.jogadores:
        assert jogador.nome
        assert len(jogador.nome) > 0


def test_consistencia_cada_jogador_tem_territorios(client_com_partida):
    
    partida = state.partida_global
    
    for jogador in partida.jogadores:
        assert len(jogador.territorios) > 0

def test_consistencia_fronteiras_bidirecionais(client_com_partida):
    
    partida = state.partida_global
    
    for territorio in partida.tabuleiro.territorios:
        for vizinho in territorio.fronteiras:
            assert territorio in vizinho.fronteiras, \
                f"{territorio.nome} -> {vizinho.nome}, mas {vizinho.nome} não tem {territorio.nome}"


def test_consistencia_territorio_nao_fronteira_de_si_mesmo(client_com_partida):
    
    partida = state.partida_global
    
    for territorio in partida.tabuleiro.territorios:
        assert territorio not in territorio.fronteiras


def test_consistencia_fronteiras_existem_no_tabuleiro(client_com_partida):
    
    partida = state.partida_global
    territorios_validos = set(partida.tabuleiro.territorios)
    
    for territorio in partida.tabuleiro.territorios:
        for vizinho in territorio.fronteiras:
            assert vizinho in territorios_validos

def test_consistencia_indice_jogador_atual_valido(client_com_partida):
    
    partida = state.partida_global
    
    for _ in range(10):
        assert 0 <= partida.jogador_atual_idx < len(partida.jogadores)
        partida.proximo_jogador()


def test_consistencia_indice_jogador_atual_incrementa(client_com_partida):
    
    partida = state.partida_global
    
    idx_antes = partida.jogador_atual_idx
    partida.proximo_jogador()
    idx_depois = partida.jogador_atual_idx
    
    assert idx_depois == (idx_antes + 1) % len(partida.jogadores)

def test_consistencia_regioes_bonus_nao_vazias(client_com_partida):
    
    partida = state.partida_global
    
    for regiao in partida.tabuleiro.regioes_com_bonus:
        nome_regiao, bonus, territorios = regiao
        assert len(territorios) > 0


def test_consistencia_territorios_pertencem_regiao_correta(client_com_partida):
    
    partida = state.partida_global
    
    for regiao in partida.tabuleiro.regioes_com_bonus:
        nome_regiao, _, territorios_regiao = regiao
        for territorio in territorios_regiao:
            assert territorio.regiao == nome_regiao


def test_consistencia_todas_regioes_representadas(client_com_partida):
    
    partida = state.partida_global
    
    regioes_bonus = {r[0] for r in partida.tabuleiro.regioes_com_bonus}
    regioes_territorios = {t.regiao for t in partida.tabuleiro.territorios}
    
    assert regioes_bonus == regioes_territorios

def test_consistencia_apos_cinco_turnos(client_com_partida):
    
    partida = state.partida_global
    
    for _ in range(5):
        # Valida antes de passar turno
        assert validar_territorios_nao_duplicados(partida)
        assert contar_total_territorios(partida) == len(partida.tabuleiro.territorios)
        
        for jogador in partida.jogadores:
            for territorio in jogador.territorios:
                assert territorio.cor == jogador.cor
                assert territorio.exercitos >= 1
        
        partida.proximo_jogador()


def test_consistencia_territorios_entre_turnos(client_com_partida):
    
    partida = state.partida_global
    
    distribuicao_inicial = {
        jogador.nome: len(jogador.territorios) 
        for jogador in partida.jogadores
    }
    
    # Passa 3 turnos
    for _ in range(3):
        partida.proximo_jogador()
    
    distribuicao_final = {
        jogador.nome: len(jogador.territorios) 
        for jogador in partida.jogadores
    }
    
    # Sem ataques, distribuição deve permanecer igual
    assert distribuicao_inicial == distribuicao_final


def test_consistencia_cores_no_tabuleiro(client_com_partida):
    
    partida = state.partida_global
    
    cores_jogadores = {j.cor for j in partida.jogadores}
    cores_territorios = obter_cores_unicas(partida)
    
    assert cores_territorios.issubset(cores_jogadores)
    
def test_integridade_nomes_territorios_nao_vazios(client_com_partida):
    
    partida = state.partida_global
    
    for territorio in partida.tabuleiro.territorios:
        assert territorio.nome
        assert len(territorio.nome) > 0


def test_integridade_nomes_territorios_unicos(client_com_partida):
    
    partida = state.partida_global
    
    nomes = [t.nome for t in partida.tabuleiro.territorios]
    assert len(nomes) == len(set(nomes))


def test_integridade_referencias_territorios(client_com_partida):
    
    partida = state.partida_global
    
    # Territórios nos jogadores devem ser os mesmos objetos do tabuleiro
    territorios_tabuleiro = set(partida.tabuleiro.territorios)
    
    for jogador in partida.jogadores:
        for territorio in jogador.territorios:
            assert territorio in territorios_tabuleiro
