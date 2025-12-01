import pytest
from back import state
from back.model.Partida import Partida


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def criar_payload_inicializar(qtd_humanos=2, qtd_ai=1, duracao=60):
    """Cria payload padrão para inicializar partida."""
    nomes_disponiveis = ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank']
    total_jogadores = qtd_humanos + qtd_ai
    return {
        'qtd_humanos': qtd_humanos,
        'qtd_ai': qtd_ai,
        'duracao_turno': duracao,
        'nomes': nomes_disponiveis[:total_jogadores]
    }


def obter_jogadores(client):
    """Obtém lista de jogadores da API."""
    response = client.get('/partida/jogadores')
    assert response.status_code == 200
    return response.get_json()['jogadores']


def finalizar_turno(client):
    """Finaliza o turno atual."""
    response = client.post('/partida/finalizar_turno', json={})
    assert response.status_code == 200
    return response.get_json()


# ============================================================================
# TESTES E2E - FLUXO COMPLETO
# ============================================================================

def test_e2e_inicializar_partida_ate_primeiro_turno(client):
    """
    Testa o fluxo completo:
    1. POST /inicializar_partida
    2. GET /partida/jogadores
    3. POST /partida/finalizar_turno (primeiro turno)
    """
    # 1. Inicializa partida
    payload = criar_payload_inicializar()
    response = client.post('/inicializar_partida', json=payload)
    assert response.status_code == 200
    
    # 2. Verifica se jogadores foram criados
    jogadores = obter_jogadores(client)
    assert len(jogadores) == 3
    assert jogadores[0]['nome'] == 'Alice'
    assert jogadores[1]['nome'] == 'Bob'
    assert jogadores[2]['nome'] == 'Charlie'
    
    # 3. Finaliza primeiro turno
    resultado = finalizar_turno(client)
    assert 'proximo_jogador' in resultado
    assert resultado['proximo_jogador']['nome'] == 'Bob'


def test_e2e_ciclo_completo_tres_turnos(client):
    """Testa 3 ciclos completos de turno (todos jogadores)."""
    # Inicializa partida
    payload = criar_payload_inicializar()
    client.post('/inicializar_partida', json=payload)
    
    partida = state.partida_global
    num_jogadores = len(partida.jogadores)
    
    # Executa 3 ciclos completos (3 turnos por jogador)
    for ciclo in range(3):
        for jogador_idx in range(num_jogadores):
            resultado = finalizar_turno(client)
            
            # Verifica se retornou o próximo jogador correto
            proximo_idx = (jogador_idx + 1) % num_jogadores
            assert resultado['proximo_jogador']['jogador_id'] == partida.jogadores[proximo_idx].cor
    
    # Após 3 ciclos completos, deve estar no primeiro jogador novamente
    assert state.partida_global.jogador_atual_idx == 0


def test_e2e_inicializar_multiplas_configuracoes(client):
    """Testa inicialização com diferentes configurações de jogadores."""
    configuracoes = [
        (3, 0, 60),  # 3 humanos, 0 IA (mínimo 3 jogadores)
        (2, 2, 90),  # 2 humanos, 2 IA
        (3, 1, 120), # 3 humanos, 1 IA
    ]
    
    for qtd_humanos, qtd_ai, duracao in configuracoes:
        payload = criar_payload_inicializar(qtd_humanos, qtd_ai, duracao)
        response = client.post('/inicializar_partida', json=payload)
        assert response.status_code == 200
        
        jogadores = obter_jogadores(client)
        assert len(jogadores) == qtd_humanos + qtd_ai
        
        # Limpa partida para próxima iteração
        state.partida_global = None


def test_e2e_ataque_completo(client_com_partida):
    """Testa o fluxo completo de um ataque."""
    partida = state.partida_global
    
    # Setup
    jogador_a = partida.jogadores[0]
    jogador_b = partida.jogadores[1]
    territorio_a = partida.tabuleiro.territorios[0]
    territorio_b = territorio_a.fronteiras[0]
    
    territorio_a.cor = jogador_a.cor
    territorio_b.cor = jogador_b.cor
    territorio_a.exercitos = 10
    territorio_b.exercitos = 1
    
    jogador_a.territorios = [territorio_a]
    jogador_b.territorios = [territorio_b]
    
    # Ataque
    response = client_com_partida.post('/partida/ataque', json={
        'territorio_origem': territorio_a.nome,
        'territorio_ataque': territorio_b.nome,
        'jogador_id': jogador_a.cor
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'


def test_e2e_verificar_distribuicao_inicial_territorios(client):
    """Testa se territórios são distribuídos corretamente ao inicializar."""
    payload = criar_payload_inicializar()
    client.post('/inicializar_partida', json=payload)
    
    partida = state.partida_global
    
    # Todos os jogadores devem ter territórios
    for jogador in partida.jogadores:
        assert len(jogador.territorios) > 0
    
    # Total de territórios deve ser consistente
    total_territorios = sum(len(j.territorios) for j in partida.jogadores)
    assert total_territorios == len(partida.tabuleiro.territorios)


def test_e2e_verificar_exercitos_iniciais(client):
    """Testa se jogadores recebem exércitos iniciais corretamente."""
    payload = criar_payload_inicializar()
    client.post('/inicializar_partida', json=payload)
    
    jogadores = obter_jogadores(client)
    
    # Primeiro jogador deve ter exércitos para posicionar
    assert jogadores[0]['exercitos_reserva'] > 0


def test_e2e_finalizar_turno_atualiza_jogador_atual(client):
    """Testa se finalizar turno atualiza corretamente o jogador atual."""
    payload = criar_payload_inicializar()
    client.post('/inicializar_partida', json=payload)
    
    partida = state.partida_global
    jogador_inicial = partida.jogadores[0]
    
    # Finaliza turno
    resultado = finalizar_turno(client)
    
    # Jogador atual deve ter mudado
    assert partida.jogador_atual_idx == 1
    assert resultado['proximo_jogador']['nome'] != jogador_inicial.nome


def test_e2e_sequencia_completa_dez_turnos(client):
    """Testa uma sequência de 10 turnos consecutivos."""
    payload = criar_payload_inicializar()
    client.post('/inicializar_partida', json=payload)
    
    partida = state.partida_global
    num_jogadores = len(partida.jogadores)
    
    for i in range(10):
        idx_esperado_antes = i % num_jogadores
        assert partida.jogador_atual_idx == idx_esperado_antes
        
        finalizar_turno(client)
        
        idx_esperado_depois = (i + 1) % num_jogadores
        assert partida.jogador_atual_idx == idx_esperado_depois


def test_e2e_verificar_estado_apos_multiplos_turnos(client):
    """Testa a consistência do estado após múltiplos turnos."""
    payload = criar_payload_inicializar()
    client.post('/inicializar_partida', json=payload)
    
    partida = state.partida_global
    total_territorios_inicial = len(partida.tabuleiro.territorios)
    
    # Executa 5 turnos
    for _ in range(5):
        finalizar_turno(client)
    
    # Total de territórios deve permanecer o mesmo
    total_territorios_final = sum(len(j.territorios) for j in partida.jogadores)
    assert total_territorios_inicial == total_territorios_final


def test_e2e_reiniciar_partida(client):
    """Testa reiniciar uma partida."""
    # Primeira partida (mínimo 3 jogadores)
    payload1 = criar_payload_inicializar(qtd_humanos=3, qtd_ai=0)
    client.post('/inicializar_partida', json=payload1)
    jogadores1 = obter_jogadores(client)
    assert len(jogadores1) == 3
    
    # Segunda partida (reinicia)
    payload2 = criar_payload_inicializar(qtd_humanos=3, qtd_ai=1)
    client.post('/inicializar_partida', json=payload2)
    jogadores2 = obter_jogadores(client)
    assert len(jogadores2) == 4


def test_e2e_validar_resposta_json_em_todos_endpoints(client_com_partida):
    """Testa se todos os endpoints retornam JSON válido."""
    endpoints = [
        ('/partida/jogadores', 'GET', None),
        ('/partida/finalizar_turno', 'POST', {}),
    ]
    
    for endpoint, metodo, payload in endpoints:
        if metodo == 'GET':
            response = client_com_partida.get(endpoint)
        else:
            response = client_com_partida.post(endpoint, json=payload)
        
        assert response.content_type == 'application/json'
        data = response.get_json()
        assert data is not None
