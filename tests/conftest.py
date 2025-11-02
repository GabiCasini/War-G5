import pytest
from flask import Flask
from back import state
from back.model.Partida import Partida 

from back.controller.partida_controller import partida_bp

@pytest.fixture(scope='module')
def app():
    """Cria e configura uma nova instância do app Flask para cada módulo de teste."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Registra o blueprint da API
    app.register_blueprint(partida_bp)
    
    yield app

@pytest.fixture(scope='module')
def client(app):
    """Um cliente de teste para o app."""
    return app.test_client()

@pytest.fixture
def client_com_partida(client):
    """
    Um cliente de teste onde uma partida global já foi iniciada.
    Isso limpa o estado após cada teste.
    """

    jogadores = [["Alice", "vermelho", "humano"], 
                 ["Bob", "azul", "humano"], 
                 ["Charlie", "verde", "humano"]]
    
    state.partida_global = Partida(
        qtd_humanos=3, 
        qtd_ai=0, 
        duracao_turno=60, 
        tupla_jogadores=jogadores,
        shuffle_jogadores=False
    )
    
    yield client  # O teste executa aqui
    
    # Limpa a partida após o teste
    state.partida_global = None

@pytest.fixture
def partida(client_com_partida):
    return state.partida_global