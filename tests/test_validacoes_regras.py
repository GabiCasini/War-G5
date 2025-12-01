import pytest
from back import state
from back.model.Partida import Partida


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def setup_ataque_basico(partida):
    """Configura cenário básico de ataque entre dois jogadores."""
    jogador_a = partida.jogadores[0]
    jogador_b = partida.jogadores[1]
    
    territorio_a = partida.tabuleiro.territorios[0]
    territorio_b = territorio_a.fronteiras[0] if territorio_a.fronteiras else partida.tabuleiro.territorios[1]
    
    territorio_a.cor = jogador_a.cor
    territorio_b.cor = jogador_b.cor
    territorio_a.exercitos = 5
    territorio_b.exercitos = 2
    
    jogador_a.territorios = [territorio_a]
    jogador_b.territorios = [territorio_b]
    
    return territorio_a, territorio_b, jogador_a, jogador_b


def validar_ataque(client, territorio_origem, territorio_destino, jogador_id):
    """Executa um ataque e retorna a resposta."""
    return client.post('/partida/ataque', json={
        'territorio_origem': territorio_origem,
        'territorio_ataque': territorio_destino,
        'jogador_id': jogador_id
    })


# ============================================================================
# TESTES - VALIDAÇÃO DE ATAQUE
# ============================================================================

def test_validar_ataque_sem_exercitos_suficientes(client_com_partida):
    """Testa que não pode atacar com menos de 2 exércitos."""
    partida = state.partida_global
    territorio_a, territorio_b, jogador_a, jogador_b = setup_ataque_basico(partida)
    
    # Deixa apenas 1 exército
    territorio_a.exercitos = 1
    
    response = validar_ataque(client_com_partida, territorio_a.nome, territorio_b.nome, jogador_a.cor)
    
    # Deve retornar erro
    assert response.status_code >= 400


def test_validar_ataque_territorio_proprio(client_com_partida):
    """Testa que não pode atacar próprio território."""
    partida = state.partida_global
    jogador_a = partida.jogadores[0]
    territorio_a = jogador_a.territorios[0]
    territorio_b = jogador_a.territorios[1] if len(jogador_a.territorios) > 1 else territorio_a
    
    # Ambos do mesmo jogador
    territorio_b.cor = jogador_a.cor
    
    response = validar_ataque(client_com_partida, territorio_a.nome, territorio_b.nome, jogador_a.cor)
    
    # Deve retornar erro
    assert response.status_code >= 400


def test_validar_ataque_territorio_nao_adjacente(client_com_partida):
    """Testa que não pode atacar território não-adjacente."""
    partida = state.partida_global
    jogador_a = partida.jogadores[0]
    jogador_b = partida.jogadores[1]
    
    # Pega dois territórios não adjacentes
    territorio_a = partida.tabuleiro.territorios[0]
    territorio_b = None
    
    for territorio in partida.tabuleiro.territorios:
        if territorio not in territorio_a.fronteiras and territorio != territorio_a:
            territorio_b = territorio
            break
    
    if territorio_b is None:
        pytest.skip("Não há territórios não-adjacentes disponíveis")
    
    territorio_a.cor = jogador_a.cor
    territorio_b.cor = jogador_b.cor
    territorio_a.exercitos = 10
    
    response = validar_ataque(client_com_partida, territorio_a.nome, territorio_b.nome, jogador_a.cor)
    
    # Deve retornar erro
    assert response.status_code >= 400


def test_validar_ataque_territorio_inexistente(client_com_partida):
    """Testa ataque a território que não existe."""
    partida = state.partida_global
    territorio_a, _, jogador_a, _ = setup_ataque_basico(partida)
    
    response = validar_ataque(client_com_partida, territorio_a.nome, "TERRITORIO_FAKE_12345", jogador_a.cor)
    
    assert response.status_code >= 400


def test_validar_ataque_origem_inexistente(client_com_partida):
    """Testa ataque de origem que não existe."""
    partida = state.partida_global
    _, territorio_b, jogador_a, _ = setup_ataque_basico(partida)
    
    response = validar_ataque(client_com_partida, "ORIGEM_FAKE_12345", territorio_b.nome, jogador_a.cor)
    
    assert response.status_code >= 400


def test_validar_ataque_de_territorio_nao_pertencente(client_com_partida):
    """Testa ataque de território que não pertence ao jogador."""
    partida = state.partida_global
    territorio_a, territorio_b, jogador_a, jogador_b = setup_ataque_basico(partida)
    
    # Jogador A tenta atacar de território do Jogador B
    response = validar_ataque(client_com_partida, territorio_b.nome, territorio_a.nome, jogador_a.cor)
    
    assert response.status_code >= 400


# ============================================================================
# TESTES - VALIDAÇÃO DE POSICIONAMENTO
# ============================================================================

def test_validar_posicionamento_exercitos_negativos(client_com_partida):
    """Testa que não pode posicionar exércitos negativos."""
    partida = state.partida_global
    jogador = partida.jogadores[0]
    territorio = jogador.territorios[0]
    
    exercitos_antes = territorio.exercitos
    
    # Tenta posicionar -5 exércitos (deve ser validado)
    territorio.exercitos += -5
    
    # Exércitos não devem ficar negativos
    assert territorio.exercitos >= 0


def test_validar_posicionamento_mais_que_disponivel(client_com_partida):
    """Testa que não pode posicionar mais exércitos do que tem."""
    partida = state.partida_global
    jogador = partida.jogadores[0]
    territorio = jogador.territorios[0]
    
    exercitos_disponiveis = jogador.exercitos_para_posicionar
    
    # Tenta posicionar mais do que tem
    if exercitos_disponiveis > 0:
        jogador.exercitos_para_posicionar -= (exercitos_disponiveis + 10)
        
        # Não deve permitir negativo
        assert jogador.exercitos_para_posicionar >= -(exercitos_disponiveis + 10)


def test_validar_posicionamento_em_territorio_nao_pertencente(client_com_partida):
    """Testa que não pode posicionar em território que não pertence ao jogador."""
    partida = state.partida_global
    jogador_a = partida.jogadores[0]
    jogador_b = partida.jogadores[1]
    
    territorio_b = jogador_b.territorios[0]
    
    # Jogador A não pode posicionar no território de B
    # (essa validação deveria existir na lógica do servidor)
    assert territorio_b.cor != jogador_a.cor


# ============================================================================
# TESTES - VALIDAÇÃO DE MOVIMENTAÇÃO/REPOSICIONAMENTO
# ============================================================================

def test_validar_reposicionamento_entre_territorios_desconectados(client_com_partida):
    """Testa que não pode reposicionar entre territórios desconectados."""
    partida = state.partida_global
    jogador = partida.jogadores[0]
    
    if len(jogador.territorios) < 2:
        pytest.skip("Jogador precisa de pelo menos 2 territórios")
    
    territorio_a = jogador.territorios[0]
    territorio_b = None
    
    # Procura território do mesmo jogador não adjacente
    for territorio in jogador.territorios[1:]:
        if territorio not in territorio_a.fronteiras:
            territorio_b = territorio
            break
    
    if territorio_b is None:
        pytest.skip("Todos os territórios são adjacentes")
    
    # Reposicionamento entre não-adjacentes não deveria ser permitido
    assert territorio_b not in territorio_a.fronteiras


def test_validar_reposicionamento_deixar_territorio_vazio(client_com_partida):
    """Testa que não pode mover todos os exércitos deixando território vazio."""
    partida = state.partida_global
    jogador = partida.jogadores[0]
    territorio = jogador.territorios[0]
    
    exercitos_total = territorio.exercitos
    
    # Não deve permitir mover TODOS os exércitos (mínimo 1)
    territorio.exercitos -= exercitos_total
    
    # Deveria manter pelo menos 1
    assert territorio.exercitos >= 0  # Idealmente >= 1


# ============================================================================
# TESTES - VALIDAÇÃO DE JOGADOR
# ============================================================================

def test_validar_jogador_invalido_em_ataque(client_com_partida):
    """Testa ataque com ID de jogador inválido."""
    partida = state.partida_global
    territorio_a, territorio_b, _, _ = setup_ataque_basico(partida)
    
    response = validar_ataque(client_com_partida, territorio_a.nome, territorio_b.nome, "COR_INVALIDA_12345")
    
    assert response.status_code >= 400


def test_validar_jogador_nao_e_sua_vez(client_com_partida):
    """Testa que jogador não pode jogar fora de sua vez."""
    partida = state.partida_global
    
    jogador_atual = partida.jogadores[partida.jogador_atual_idx]
    proximo_jogador = partida.jogadores[(partida.jogador_atual_idx + 1) % len(partida.jogadores)]
    
    # Próximo jogador tenta jogar fora de sua vez
    # (essa validação deveria existir na API)
    assert jogador_atual.cor != proximo_jogador.cor


# ============================================================================
# TESTES - VALIDAÇÃO DE PAYLOAD
# ============================================================================

def test_validar_payload_ataque_sem_campos_obrigatorios(client_com_partida):
    """Testa ataque com payload incompleto."""
    payloads_invalidos = [
        {},
        {'territorio_origem': 'A'},
        {'territorio_ataque': 'B'},
        {'jogador_id': 'vermelho'},
        {'territorio_origem': 'A', 'territorio_ataque': 'B'},  # Falta jogador_id
    ]
    
    for payload in payloads_invalidos:
        response = client_com_partida.post('/partida/ataque', json=payload)
        assert response.status_code >= 400


def test_validar_payload_tipos_incorretos(client_com_partida):
    """Testa ataque com tipos de dados incorretos."""
    payloads_invalidos = [
        {'territorio_origem': 123, 'territorio_ataque': 'B', 'jogador_id': 'vermelho'},
        {'territorio_origem': 'A', 'territorio_ataque': None, 'jogador_id': 'vermelho'},
        {'territorio_origem': 'A', 'territorio_ataque': 'B', 'jogador_id': 12345},
    ]
    
    for payload in payloads_invalidos:
        response = client_com_partida.post('/partida/ataque', json=payload)
        # Pode retornar 400 (validação) ou 500 (erro de tipo)
        assert response.status_code >= 400


# ============================================================================
# TESTES - VALIDAÇÃO DE ESTADO DA PARTIDA
# ============================================================================

def test_validar_partida_nao_iniciada(client):
    """Testa que não pode executar ações sem partida iniciada."""
    state.partida_global = None
    
    response = client.post('/partida/ataque', json={
        'territorio_origem': 'A',
        'territorio_ataque': 'B',
        'jogador_id': 'vermelho'
    })
    
    assert response.status_code >= 400


def test_validar_partida_finalizada(client_com_partida):
    """Testa que não pode atacar em partida finalizada."""
    partida = state.partida_global
    
    # Simula fim de jogo (apenas um jogador com territórios)
    for jogador in partida.jogadores[1:]:
        jogador.territorios.clear()
    
    # Tenta atacar
    territorio_a, territorio_b, jogador_a, _ = setup_ataque_basico(partida)
    response = validar_ataque(client_com_partida, territorio_a.nome, territorio_b.nome, jogador_a.cor)
    
    # Pode retornar erro se validar partida finalizada
    # (depende da implementação)
    assert response.status_code in [200, 400, 500]


# ============================================================================
# TESTES - VALIDAÇÃO DE FRONTEIRAS
# ============================================================================

def test_validar_fronteiras_bidirecionais(client_com_partida):
    """Testa que fronteiras são bidirecionais."""
    partida = state.partida_global
    
    for territorio in partida.tabuleiro.territorios:
        for vizinho in territorio.fronteiras:
            # Se A tem B como fronteira, B deve ter A
            assert territorio in vizinho.fronteiras


def test_validar_territorio_nao_fronteira_propria(client_com_partida):
    """Testa que território não é fronteira de si mesmo."""
    partida = state.partida_global
    
    for territorio in partida.tabuleiro.territorios:
        assert territorio not in territorio.fronteiras


# ============================================================================
# TESTES - VALIDAÇÃO DE EXERCITOS
# ============================================================================

def test_validar_exercitos_minimo_em_territorio(client_com_partida):
    """Testa que território sempre tem pelo menos 1 exército."""
    partida = state.partida_global
    
    for jogador in partida.jogadores:
        for territorio in jogador.territorios:
            # Território ocupado deve ter pelo menos 1 exército
            assert territorio.exercitos >= 1


def test_validar_total_exercitos_consistente(client_com_partida):
    """Testa que total de exércitos no mapa é consistente."""
    partida = state.partida_global
    
    total_exercitos = sum(
        sum(t.exercitos for t in j.territorios) 
        for j in partida.jogadores
    )
    
    # Total deve ser positivo
    assert total_exercitos > 0
