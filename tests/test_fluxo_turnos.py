import pytest
from back import state
from back.model.Partida import Partida


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def obter_jogador_atual(partida):
    """Obtém o jogador da vez."""
    return partida.jogadores[partida.jogador_atual_idx]


def contar_exercitos_jogador(jogador):
    """Conta total de exércitos de um jogador."""
    return sum(t.exercitos for t in jogador.territorios)


def simular_posicionamento_exercitos(jogador, territorio, quantidade):
    """Simula posicionamento de exércitos em um território."""
    if jogador.exercitos_reserva >= quantidade:
        territorio.exercitos += quantidade
        jogador.exercitos_reserva -= quantidade
        return True
    return False


# ============================================================================
# TESTES - FASES DO TURNO
# ============================================================================

def test_turno_fase_posicionamento_recebe_exercitos(client_com_partida):
    """Testa se jogador recebe exércitos na fase de posicionamento."""
    partida = state.partida_global
    jogador = obter_jogador_atual(partida)
    
    # Jogador deve ter exércitos para posicionar
    assert jogador.exercitos_reserva > 0


def test_turno_fase_posicionamento_quantidade_minima(client_com_partida):
    """Testa se jogador recebe no mínimo 3 exércitos."""
    partida = state.partida_global
    jogador = obter_jogador_atual(partida)
    
    # Mínimo de 3 exércitos
    assert jogador.exercitos_reserva >= 3


def test_turno_fase_posicionamento_bonus_territorios(client_com_partida):
    """Testa bônus por quantidade de territórios."""
    partida = state.partida_global
    jogador = obter_jogador_atual(partida)
    
    # Calcula bônus esperado
    bonus_esperado = max(3, len(jogador.territorios) // 2)
    
    # Deve receber pelo menos o bônus de territórios
    assert jogador.exercitos_reserva >= bonus_esperado


def test_turno_distribuir_exercitos_em_territorio(client_com_partida):
    """Testa distribuição de exércitos durante posicionamento."""
    partida = state.partida_global
    jogador = obter_jogador_atual(partida)
    territorio = jogador.territorios[0]
    
    exercitos_antes = territorio.exercitos
    exercitos_disponiveis = jogador.exercitos_reserva
    
    # Posiciona 2 exércitos
    sucesso = simular_posicionamento_exercitos(jogador, territorio, 2)
    
    assert sucesso
    assert territorio.exercitos == exercitos_antes + 2
    assert jogador.exercitos_reserva == exercitos_disponiveis - 2


def test_turno_nao_pode_posicionar_mais_que_disponivel(client_com_partida):
    """Testa que não pode posicionar mais exércitos do que tem."""
    partida = state.partida_global
    jogador = obter_jogador_atual(partida)
    territorio = jogador.territorios[0]
    
    exercitos_disponiveis = jogador.exercitos_reserva
    
    # Tenta posicionar mais do que tem
    sucesso = simular_posicionamento_exercitos(jogador, territorio, exercitos_disponiveis + 10)
    
    assert not sucesso


def test_turno_finalizar_passa_para_proximo(client_com_partida):
    """Testa que finalizar turno passa para o próximo jogador."""
    partida = state.partida_global
    idx_antes = partida.jogador_atual_idx
    
    partida.proximo_jogador()
    
    idx_depois = partida.jogador_atual_idx
    assert idx_depois == (idx_antes + 1) % len(partida.jogadores)


def test_turno_finalizar_circular(client_com_partida):
    """Testa que turno volta para primeiro jogador após o último."""
    partida = state.partida_global
    num_jogadores = len(partida.jogadores)
    
    # Avança todos os turnos
    for _ in range(num_jogadores):
        partida.proximo_jogador()
    
    # Deve estar no primeiro novamente
    assert partida.jogador_atual_idx == 0


# ============================================================================
# TESTES - SEQUÊNCIA DE TURNOS
# ============================================================================

def test_turno_sequencia_cinco_turnos(client_com_partida):
    """Testa sequência de 5 turnos consecutivos."""
    partida = state.partida_global
    
    jogadores_que_jogaram = []
    
    for _ in range(5):
        jogador_atual = obter_jogador_atual(partida)
        jogadores_que_jogaram.append(jogador_atual.nome)
        partida.proximo_jogador()
    
    # Verifica que houve alternância
    assert len(set(jogadores_que_jogaram)) > 1


def test_turno_cada_jogador_joga_uma_vez_por_ciclo(client_com_partida):
    """Testa que cada jogador joga exatamente uma vez por ciclo."""
    partida = state.partida_global
    num_jogadores = len(partida.jogadores)
    
    jogadores_que_jogaram = []
    
    for _ in range(num_jogadores):
        jogador_atual = obter_jogador_atual(partida)
        jogadores_que_jogaram.append(jogador_atual.nome)
        partida.proximo_jogador()
    
    # Todos devem ter jogado exatamente uma vez
    assert len(jogadores_que_jogaram) == num_jogadores
    assert len(set(jogadores_que_jogaram)) == num_jogadores


def test_turno_ordem_jogadores_consistente(client_com_partida):
    """Testa se ordem dos jogadores se mantém consistente."""
    partida = state.partida_global
    num_jogadores = len(partida.jogadores)
    
    # Primeira rodada
    ordem_primeira = []
    for _ in range(num_jogadores):
        ordem_primeira.append(obter_jogador_atual(partida).nome)
        partida.proximo_jogador()
    
    # Segunda rodada
    ordem_segunda = []
    for _ in range(num_jogadores):
        ordem_segunda.append(obter_jogador_atual(partida).nome)
        partida.proximo_jogador()
    
    # Ordem deve ser a mesma
    assert ordem_primeira == ordem_segunda


# ============================================================================
# TESTES - GESTÃO DE TURNO
# ============================================================================

def test_turno_gerenciar_nao_lanca_excecao(client_com_partida):
    """Testa que passar turno não lança exceção."""
    partida = state.partida_global
    
    try:
        # Apenas passa para o próximo jogador
        partida.proximo_jogador()
    except Exception as e:
        pytest.fail(f"proximo_jogador lançou exceção: {e}")


def test_turno_exercitos_nao_negativos(client_com_partida):
    """Testa que exércitos nunca ficam negativos durante turno."""
    partida = state.partida_global
    
    for _ in range(5):
        jogador = obter_jogador_atual(partida)
        
        for territorio in jogador.territorios:
            assert territorio.exercitos >= 0
        
        partida.proximo_jogador()


def test_turno_territorios_nao_desaparecem(client_com_partida):
    """Testa que territórios não desaparecem durante turnos normais."""
    partida = state.partida_global
    total_inicial = len(partida.tabuleiro.territorios)
    
    for _ in range(5):
        partida.proximo_jogador()
    
    total_final = sum(len(j.territorios) for j in partida.jogadores)
    assert total_final == total_inicial


# ============================================================================
# TESTES - BÔNUS E CÁLCULOS
# ============================================================================

def test_turno_bonus_continente(client_com_partida):
    """Testa bônus por dominar um continente."""
    partida = state.partida_global
    jogador = partida.jogadores[0]
    
    # Simula domínio de uma região completa
    regiao_teste = partida.tabuleiro.regioes_com_bonus[0]
    bonus_esperado = regiao_teste[1]
    
    # Atribui todos os territórios da região ao jogador
    for territorio in regiao_teste[2]:
        territorio.cor = jogador.cor
        if territorio not in jogador.territorios:
            jogador.territorios.append(territorio)
    
    # Recalcula exércitos
    partida.tabuleiro.calcula_exercitos_a_receber(jogador)
    
    # Deve ter recebido o bônus
    assert jogador.exercitos_reserva >= bonus_esperado


def test_turno_calculo_exercitos_multiplos_territorios(client_com_partida):
    """Testa cálculo de exércitos baseado em territórios."""
    partida = state.partida_global
    jogador = partida.jogadores[0]
    
    # Garante que jogador tem territórios suficientes
    num_territorios = len(jogador.territorios)
    bonus_esperado = max(3, num_territorios // 2)
    
    # Limpa e recalcula
    jogador.exercitos_reserva = 0
    partida.tabuleiro.calcula_exercitos_a_receber(jogador)
    
    # Deve ter recebido pelo menos o bônus de territórios
    assert jogador.exercitos_reserva >= bonus_esperado


# ============================================================================
# TESTES - VALIDAÇÃO DE ESTADO
# ============================================================================

def test_turno_indice_jogador_sempre_valido(client_com_partida):
    """Testa que índice do jogador atual é sempre válido."""
    partida = state.partida_global
    
    for _ in range(20):
        assert 0 <= partida.jogador_atual_idx < len(partida.jogadores)
        partida.proximo_jogador()


def test_turno_cores_territorios_consistentes(client_com_partida):
    """Testa que cor dos territórios é consistente com proprietário."""
    partida = state.partida_global
    
    for _ in range(3):
        for jogador in partida.jogadores:
            for territorio in jogador.territorios:
                assert territorio.cor == jogador.cor
        
        partida.proximo_jogador()
