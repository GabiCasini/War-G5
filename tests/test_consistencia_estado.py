import pytest
from back import state
from back.model.Partida import Partida


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def contar_total_territorios(partida):
    """Conta total de territórios distribuídos entre jogadores."""
    return sum(len(j.territorios) for j in partida.jogadores)


def contar_total_exercitos(partida):
    """Conta total de exércitos no mapa."""
    return sum(
        sum(t.exercitos for t in j.territorios) 
        for j in partida.jogadores
    )


def obter_cores_unicas(partida):
    """Retorna conjunto de cores únicas no tabuleiro."""
    return {t.cor for t in partida.tabuleiro.territorios}


def validar_territorios_nao_duplicados(partida):
    """Valida que nenhum território está duplicado."""
    territorios_vistos = set()
    for jogador in partida.jogadores:
        for territorio in jogador.territorios:
            if territorio in territorios_vistos:
                return False
            territorios_vistos.add(territorio)
    return True


# ============================================================================
# TESTES - CONSISTÊNCIA DE TERRITÓRIOS
# ============================================================================

def test_consistencia_total_territorios_partida(client_com_partida):
    """Testa que total de territórios distribuídos é igual ao total do tabuleiro."""
    partida = state.partida_global
    
    total_tabuleiro = len(partida.tabuleiro.territorios)
    total_distribuido = contar_total_territorios(partida)
    
    assert total_tabuleiro == total_distribuido


def test_consistencia_nenhum_territorio_duplicado(client_com_partida):
    """Testa que nenhum território pertence a dois jogadores."""
    partida = state.partida_global
    
    assert validar_territorios_nao_duplicados(partida)


def test_consistencia_todos_territorios_tem_proprietario(client_com_partida):
    """Testa que todos os territórios têm um proprietário."""
    partida = state.partida_global
    
    for territorio in partida.tabuleiro.territorios:
        # Deve ter uma cor válida
        assert territorio.cor in [j.cor for j in partida.jogadores]


def test_consistencia_cor_territorio_matches_proprietario(client_com_partida):
    """Testa que cor do território corresponde ao proprietário."""
    partida = state.partida_global
    
    for jogador in partida.jogadores:
        for territorio in jogador.territorios:
            assert territorio.cor == jogador.cor


def test_consistencia_territorio_nao_desaparece_apos_turno(client_com_partida):
    """Testa que territórios não desaparecem após passar turno."""
    partida = state.partida_global
    
    total_antes = contar_total_territorios(partida)
    
    # Passa 3 turnos
    for _ in range(3):
        partida.proximo_jogador()
    
    total_depois = contar_total_territorios(partida)
    
    assert total_antes == total_depois


# ============================================================================
# TESTES - CONSISTÊNCIA DE EXÉRCITOS
# ============================================================================

def test_consistencia_exercitos_nao_negativos(client_com_partida):
    """Testa que nenhum território tem exércitos negativos."""
    partida = state.partida_global
    
    for territorio in partida.tabuleiro.territorios:
        assert territorio.exercitos >= 0


def test_consistencia_exercitos_minimo_um(client_com_partida):
    """Testa que território ocupado tem pelo menos 1 exército."""
    partida = state.partida_global
    
    for jogador in partida.jogadores:
        for territorio in jogador.territorios:
            assert territorio.exercitos >= 1


def test_consistencia_total_exercitos_apos_ataque(client_com_partida):
    """Testa que total de exércitos é consistente após ataque."""
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
    """Testa que exércitos para posicionar não fica negativo."""
    partida = state.partida_global
    
    for jogador in partida.jogadores:
        assert jogador.exercitos_reserva >= 0


# ============================================================================
# TESTES - CONSISTÊNCIA DE JOGADORES
# ============================================================================

def test_consistencia_numero_jogadores(client_com_partida):
    """Testa que número de jogadores é consistente."""
    partida = state.partida_global
    
    # Deve ter 3 jogadores (conforme fixture)
    assert len(partida.jogadores) == 3


def test_consistencia_cores_jogadores_unicas(client_com_partida):
    """Testa que cada jogador tem cor única."""
    partida = state.partida_global
    
    cores = [j.cor for j in partida.jogadores]
    assert len(cores) == len(set(cores))


def test_consistencia_nomes_jogadores_nao_vazios(client_com_partida):
    """Testa que nomes de jogadores não são vazios."""
    partida = state.partida_global
    
    for jogador in partida.jogadores:
        assert jogador.nome
        assert len(jogador.nome) > 0


def test_consistencia_cada_jogador_tem_territorios(client_com_partida):
    """Testa que cada jogador tem pelo menos 1 território."""
    partida = state.partida_global
    
    for jogador in partida.jogadores:
        assert len(jogador.territorios) > 0


# ============================================================================
# TESTES - CONSISTÊNCIA DE FRONTEIRAS
# ============================================================================

def test_consistencia_fronteiras_bidirecionais(client_com_partida):
    """Testa que todas as fronteiras são bidirecionais."""
    partida = state.partida_global
    
    for territorio in partida.tabuleiro.territorios:
        for vizinho in territorio.fronteiras:
            assert territorio in vizinho.fronteiras, \
                f"{territorio.nome} -> {vizinho.nome}, mas {vizinho.nome} não tem {territorio.nome}"


def test_consistencia_territorio_nao_fronteira_de_si_mesmo(client_com_partida):
    """Testa que território não é sua própria fronteira."""
    partida = state.partida_global
    
    for territorio in partida.tabuleiro.territorios:
        assert territorio not in territorio.fronteiras


def test_consistencia_fronteiras_existem_no_tabuleiro(client_com_partida):
    """Testa que todas as fronteiras referenciadas existem no tabuleiro."""
    partida = state.partida_global
    territorios_validos = set(partida.tabuleiro.territorios)
    
    for territorio in partida.tabuleiro.territorios:
        for vizinho in territorio.fronteiras:
            assert vizinho in territorios_validos


# ============================================================================
# TESTES - CONSISTÊNCIA DE ÍNDICES
# ============================================================================

def test_consistencia_indice_jogador_atual_valido(client_com_partida):
    """Testa que índice do jogador atual é sempre válido."""
    partida = state.partida_global
    
    for _ in range(10):
        assert 0 <= partida.jogador_atual_idx < len(partida.jogadores)
        partida.proximo_jogador()


def test_consistencia_indice_jogador_atual_incrementa(client_com_partida):
    """Testa que índice incrementa corretamente."""
    partida = state.partida_global
    
    idx_antes = partida.jogador_atual_idx
    partida.proximo_jogador()
    idx_depois = partida.jogador_atual_idx
    
    assert idx_depois == (idx_antes + 1) % len(partida.jogadores)


# ============================================================================
# TESTES - CONSISTÊNCIA DE REGIÕES
# ============================================================================

def test_consistencia_regioes_bonus_nao_vazias(client_com_partida):
    """Testa que todas as regiões têm territórios."""
    partida = state.partida_global
    
    for regiao in partida.tabuleiro.regioes_com_bonus:
        nome_regiao, bonus, territorios = regiao
        assert len(territorios) > 0


def test_consistencia_territorios_pertencem_regiao_correta(client_com_partida):
    """Testa que territórios estão na região correta."""
    partida = state.partida_global
    
    for regiao in partida.tabuleiro.regioes_com_bonus:
        nome_regiao, _, territorios_regiao = regiao
        for territorio in territorios_regiao:
            assert territorio.regiao == nome_regiao


def test_consistencia_todas_regioes_representadas(client_com_partida):
    """Testa que todas as regiões estão representadas no tabuleiro."""
    partida = state.partida_global
    
    regioes_bonus = {r[0] for r in partida.tabuleiro.regioes_com_bonus}
    regioes_territorios = {t.regiao for t in partida.tabuleiro.territorios}
    
    assert regioes_bonus == regioes_territorios


# ============================================================================
# TESTES - CONSISTÊNCIA APÓS MÚLTIPLAS OPERAÇÕES
# ============================================================================

def test_consistencia_apos_cinco_turnos(client_com_partida):
    """Testa que consistência se mantém após 5 turnos."""
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
    """Testa que a distribuição de territórios permanece consistente."""
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
    """Testa que cores no tabuleiro correspondem aos jogadores."""
    partida = state.partida_global
    
    cores_jogadores = {j.cor for j in partida.jogadores}
    cores_territorios = obter_cores_unicas(partida)
    
    assert cores_territorios.issubset(cores_jogadores)


# ============================================================================
# TESTES - INTEGRIDADE DE DADOS
# ============================================================================

def test_integridade_nomes_territorios_nao_vazios(client_com_partida):
    """Testa que todos os territórios têm nomes válidos."""
    partida = state.partida_global
    
    for territorio in partida.tabuleiro.territorios:
        assert territorio.nome
        assert len(territorio.nome) > 0


def test_integridade_nomes_territorios_unicos(client_com_partida):
    """Testa que nomes de territórios são únicos."""
    partida = state.partida_global
    
    nomes = [t.nome for t in partida.tabuleiro.territorios]
    assert len(nomes) == len(set(nomes))


def test_integridade_referencias_territorios(client_com_partida):
    """Testa que referências de territórios são consistentes."""
    partida = state.partida_global
    
    # Territórios nos jogadores devem ser os mesmos objetos do tabuleiro
    territorios_tabuleiro = set(partida.tabuleiro.territorios)
    
    for jogador in partida.jogadores:
        for territorio in jogador.territorios:
            assert territorio in territorios_tabuleiro
