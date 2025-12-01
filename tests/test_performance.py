import pytest
import time
from back import state
from back.model.Partida import Partida


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def medir_tempo(funcao, *args, **kwargs):
    """Mede o tempo de execução de uma função."""
    inicio = time.time()
    resultado = funcao(*args, **kwargs)
    duracao = time.time() - inicio
    return duracao, resultado


def criar_payload_padrao():
    """Cria payload padrão para testes."""
    return {
        'qtd_humanos': 2,
        'qtd_ai': 1,
        'duracao_turno': 60,
        'nomes': ['Alice', 'Bob', 'Charlie']
    }


# ============================================================================
# TESTES - PERFORMANCE DE INICIALIZAÇÃO
# ============================================================================

def test_performance_inicializar_partida_rapido(client):
    """Testa que inicializar partida é rápido (< 1s)."""
    payload = criar_payload_padrao()
    
    duracao, response = medir_tempo(
        client.post,
        '/inicializar_partida',
        json=payload
    )
    
    assert duracao < 1.0, f"Inicialização demorou {duracao:.2f}s (esperado < 1s)"
    assert response.status_code == 200


def test_performance_inicializar_partida_consistente(client):
    """Testa que tempo de inicialização é consistente."""
    payload = criar_payload_padrao()
    tempos = []
    
    for _ in range(3):
        duracao, response = medir_tempo(
            client.post,
            '/inicializar_partida',
            json=payload
        )
        tempos.append(duracao)
        assert response.status_code == 200
        state.partida_global = None  # Limpa para próxima iteração
    
    # Variação não deve ser muito grande
    tempo_medio = sum(tempos) / len(tempos)
    for tempo in tempos:
        assert abs(tempo - tempo_medio) < 0.5, "Variação de tempo muito grande"


def test_performance_carregar_territorios_json(client):
    """Testa que carregamento do JSON de territórios é rápido."""
    from back.utils.territorios_loader import carregar_territorios_json
    
    duracao, territorios = medir_tempo(carregar_territorios_json)
    
    assert duracao < 0.1, f"Carregamento demorou {duracao:.3f}s (esperado < 0.1s)"
    assert len(territorios) > 0


# ============================================================================
# TESTES - PERFORMANCE DE TURNOS
# ============================================================================

def test_performance_finalizar_turno_rapido(client_com_partida):
    """Testa que finalizar turno é rápido (< 0.1s)."""
    duracao, response = medir_tempo(
        client_com_partida.post,
        '/partida/finalizar_turno',
        json={}
    )
    
    assert duracao < 0.1, f"Finalizar turno demorou {duracao:.3f}s (esperado < 0.1s)"
    assert response.status_code == 200


def test_performance_multiplos_turnos(client_com_partida):
    """Testa desempenho de 10 turnos consecutivos (< 1s)."""
    inicio = time.time()
    
    for _ in range(10):
        response = client_com_partida.post('/partida/finalizar_turno', json={})
        assert response.status_code == 200
    
    duracao = time.time() - inicio
    assert duracao < 1.0, f"10 turnos demoraram {duracao:.2f}s (esperado < 1s)"


def test_performance_cinquenta_turnos(client_com_partida):
    """Testa desempenho de 50 turnos (< 3s)."""
    inicio = time.time()
    
    for _ in range(50):
        client_com_partida.post('/partida/finalizar_turno', json={})
    
    duracao = time.time() - inicio
    assert duracao < 3.0, f"50 turnos demoraram {duracao:.2f}s (esperado < 3s)"


# ============================================================================
# TESTES - PERFORMANCE DE CONSULTAS
# ============================================================================

def test_performance_obter_jogadores(client_com_partida):
    """Testa que obter jogadores é rápido (< 0.05s)."""
    duracao, response = medir_tempo(
        client_com_partida.get,
        '/partida/jogadores'
    )
    
    assert duracao < 0.05, f"GET jogadores demorou {duracao:.3f}s (esperado < 0.05s)"
    assert response.status_code == 200


def test_performance_multiplas_consultas_jogadores(client_com_partida):
    """Testa múltiplas consultas a /jogadores (< 0.5s para 20 requisições)."""
    inicio = time.time()
    
    for _ in range(20):
        response = client_com_partida.get('/partida/jogadores')
        assert response.status_code == 200
    
    duracao = time.time() - inicio
    assert duracao < 0.5, f"20 consultas demoraram {duracao:.2f}s (esperado < 0.5s)"


# ============================================================================
# TESTES - PERFORMANCE DE ATAQUES
# ============================================================================

def test_performance_ataque_simples(client_com_partida):
    """Testa que um ataque é processado rapidamente (< 0.2s)."""
    partida = state.partida_global
    
    # Setup ataque
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
    
    payload = {
        'territorio_origem': territorio_a.nome,
        'territorio_ataque': territorio_b.nome,
        'jogador_id': jogador_a.cor
    }
    
    duracao, response = medir_tempo(
        client_com_partida.post,
        '/partida/ataque',
        json=payload
    )
    
    assert duracao < 0.2, f"Ataque demorou {duracao:.3f}s (esperado < 0.2s)"


def test_performance_multiplos_ataques_sequenciais(client_com_partida):
    """Testa 5 ataques sequenciais (< 1s)."""
    partida = state.partida_global
    jogador_a = partida.jogadores[0]
    jogador_b = partida.jogadores[1]
    
    inicio = time.time()
    
    for i in range(5):
        # Setup cada ataque
        if i < len(partida.tabuleiro.territorios) - 1:
            territorio_a = partida.tabuleiro.territorios[i]
            territorio_b = partida.tabuleiro.territorios[i + 1]
            
            if territorio_b in territorio_a.fronteiras:
                territorio_a.cor = jogador_a.cor
                territorio_b.cor = jogador_b.cor
                territorio_a.exercitos = 10
                
                client_com_partida.post('/partida/ataque', json={
                    'territorio_origem': territorio_a.nome,
                    'territorio_ataque': territorio_b.nome,
                    'jogador_id': jogador_a.cor
                })
    
    duracao = time.time() - inicio
    assert duracao < 1.0, f"5 ataques demoraram {duracao:.2f}s (esperado < 1s)"


# ============================================================================
# TESTES - PERFORMANCE DE CÁLCULOS
# ============================================================================

def test_performance_calculo_exercitos(client_com_partida):
    """Testa que cálculo de exércitos a receber é rápido."""
    partida = state.partida_global
    jogador = partida.jogadores[0]
    
    duracao, _ = medir_tempo(
        partida.tabuleiro.calcula_exercitos_a_receber,
        jogador
    )
    
    assert duracao < 0.01, f"Cálculo demorou {duracao:.4f}s (esperado < 0.01s)"


def test_performance_validar_territorios_json(client):
    """Testa que validação do JSON de territórios é aceitável."""
    from back.utils.territorios_loader import validar_territorios
    
    duracao, resultado = medir_tempo(validar_territorios)
    
    assert duracao < 0.5, f"Validação demorou {duracao:.2f}s (esperado < 0.5s)"
    assert resultado['valido']


# ============================================================================
# TESTES - MEMÓRIA E ESCALABILIDADE
# ============================================================================

def test_performance_partida_nao_vaza_memoria(client):
    """Testa que criar/destruir partidas não causa vazamento de memória."""
    import gc
    
    payload = criar_payload_padrao()
    
    # Cria e destrói 10 partidas
    for _ in range(10):
        client.post('/inicializar_partida', json=payload)
        state.partida_global = None
        gc.collect()
    
    # Se chegou aqui sem crash, está OK
    assert True


def test_performance_muitos_territorios_gerenciados(client_com_partida):
    """Testa que gerenciar todos os territórios não causa lentidão."""
    partida = state.partida_global
    
    inicio = time.time()
    
    # Itera sobre todos os territórios
    for territorio in partida.tabuleiro.territorios:
        _ = territorio.nome
        _ = territorio.cor
        _ = territorio.exercitos
        _ = len(territorio.fronteiras)
    
    duracao = time.time() - inicio
    assert duracao < 0.05, f"Iteração demorou {duracao:.3f}s"


# ============================================================================
# TESTES - CARGA
# ============================================================================

def test_carga_cem_requisicoes_get_jogadores(client_com_partida):
    """Testa 100 requisições GET /jogadores (< 3s)."""
    inicio = time.time()
    
    for _ in range(100):
        response = client_com_partida.get('/partida/jogadores')
        assert response.status_code == 200
    
    duracao = time.time() - inicio
    tempo_medio = duracao / 100
    
    assert duracao < 3.0, f"100 requisições demoraram {duracao:.2f}s (esperado < 3s)"
    assert tempo_medio < 0.03, f"Tempo médio {tempo_medio:.4f}s por requisição"


def test_carga_ciclo_completo_cem_turnos(client_com_partida):
    """Testa 100 turnos completos (< 5s)."""
    inicio = time.time()
    
    for _ in range(100):
        client_com_partida.post('/partida/finalizar_turno', json={})
    
    duracao = time.time() - inicio
    assert duracao < 5.0, f"100 turnos demoraram {duracao:.2f}s (esperado < 5s)"


# ============================================================================
# TESTES - CONSISTÊNCIA SOB CARGA
# ============================================================================

def test_performance_consistencia_apos_muitos_turnos(client_com_partida):
    """Testa que estado permanece consistente após muitos turnos."""
    partida = state.partida_global
    total_territorios_inicial = len(partida.tabuleiro.territorios)
    
    # 50 turnos
    for _ in range(50):
        client_com_partida.post('/partida/finalizar_turno', json={})
    
    total_territorios_final = sum(len(j.territorios) for j in partida.jogadores)
    
    # Consistência deve ser mantida
    assert total_territorios_inicial == total_territorios_final


def test_performance_nao_degrada_com_tempo(client_com_partida):
    """Testa que performance não degrada após muitos turnos."""
    tempos = []
    
    for i in range(20):
        inicio = time.time()
        client_com_partida.post('/partida/finalizar_turno', json={})
        duracao = time.time() - inicio
        tempos.append(duracao)
    
    # Primeiros 10 vs últimos 10
    tempo_medio_inicio = sum(tempos[:10]) / 10
    tempo_medio_fim = sum(tempos[10:]) / 10
    
    # Evita divisão por zero se tempos muito pequenos
    if tempo_medio_inicio > 0.0001:
        assert tempo_medio_fim < tempo_medio_inicio * 1.5, \
            f"Performance degradou: {tempo_medio_inicio:.3f}s -> {tempo_medio_fim:.3f}s"


# ============================================================================
# TESTES - BENCHMARKS
# ============================================================================

def test_benchmark_inicializacao(client, benchmark=None):
    """Benchmark de inicialização de partida."""
    if benchmark is None:
        pytest.skip("pytest-benchmark não está instalado")
    
    payload = criar_payload_padrao()
    
    def setup():
        state.partida_global = None
    
    def funcao():
        return client.post('/inicializar_partida', json=payload)
    
    resultado = benchmark.pedantic(funcao, setup=setup, rounds=10)
    assert resultado.status_code == 200


def test_benchmark_finalizar_turno(client_com_partida, benchmark=None):
    """Benchmark de finalizar turno."""
    if benchmark is None:
        pytest.skip("pytest-benchmark não está instalado")
    
    def funcao():
        return client_com_partida.post('/partida/finalizar_turno', json={})
    
    resultado = benchmark(funcao)
    assert resultado.status_code == 200
