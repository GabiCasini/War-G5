import pytest
from back import state 

def test_get_jogadores_sem_partida(client):
    """
    Testa se o endpoint /jogadores retorna erro 400
    quando state.partida_global é None.
    """
    state.partida_global = None
    response = client.get('/partida/jogadores')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'erro'
    assert json_data['mensagem'] == 'Partida não iniciada'

def test_get_jogadores_com_partida(client_com_partida):
    """
    Testa se o endpoint /jogadores retorna a lista correta de jogadores
    quando uma partida está ativa.
    """
    response = client_com_partida.get('/partida/jogadores')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'jogadores' in json_data
    assert len(json_data['jogadores']) == 3
    
    jogador_alice = None
    for j in json_data['jogadores']:
        if j['nome'] == 'Alice':
            jogador_alice = j
            break
            
    assert jogador_alice is not None, "Jogador 'Alice' não foi encontrado na resposta da API"
    assert jogador_alice['cor'] == 'vermelho'
    assert jogador_alice['jogador_id'] == 'vermelho'
    assert jogador_alice['ia'] == False


def test_api_ataque_ignora_exercitos(client_com_partida):
    """
    Testa o endpoint /ataque.
    Este teste valida que o controller 'partida_controller.py' 
    ignora o campo 'exercitos' do body, como está escrito no código.
    """
    partida = state.partida_global 
    
    jogador_a = partida.jogadores[0] 
    jogador_b = partida.jogadores[1]
    
    territorio_a = partida.tabuleiro.territorios[0]
    territorio_b = territorio_a.fronteiras[0] 
    
    territorio_a.cor = jogador_a.cor
    territorio_b.cor = jogador_b.cor
    jogador_a.territorios = [territorio_a]
    jogador_b.territorios = [territorio_b]
    
    territorio_a.exercitos = 10
    territorio_b.exercitos = 1  
    partida.jogador_atual_idx = 0 
    
    payload = {
        "jogador_id": jogador_a.cor,
        "territorio_inicio": territorio_a.nome,
        "territorio_ataque": territorio_b.nome,
        "exercitos": 5  
    }

    response = client_com_partida.post('/partida/ataque', json=payload)
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'ok'
    assert json_data['territorio_conquistado'] == True 
    assert territorio_b.cor == jogador_a.cor 

def test_api_finalizar_turno_ignora_body(client_com_partida):
    """
    Testa o endpoint /finalizar_turno.
    Este teste VALIDA que o seu controller 'partida_controller.py'
    IGNORA o body da requisição, como está escrito no código.
    """
    partida = state.partida_global
    
    partida.jogador_atual_idx = 0
    jogador_atual_antes = partida.jogadores[0]
    proximo_jogador_esperado = partida.jogadores[1]
    
    payload = {
        "jogador_id": jogador_atual_antes.cor 
    }
    
    response = client_com_partida.post('/partida/finalizar_turno', json=payload)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'ok'
    
    assert 'proximo_jogador' in json_data
    assert json_data['proximo_jogador']['jogador_id'] == proximo_jogador_esperado.cor
    assert json_data['proximo_jogador']['nome'] == proximo_jogador_esperado.nome
    
    assert state.partida_global.jogador_atual_idx == 1