# conftest.py
# (Coloque este arquivo na pasta de testes)

import pytest
from flask import Flask
from back import state  # Importa o 'state' global
from back.model.Partida import Partida 

from back.controller.partida_controller import partida_bp

@pytest.fixture(scope='module')
def app():
    """Cria e configura uma nova instância do app Flask para cada módulo de teste."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Registra o blueprint da sua API
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
    # Setup: Cria e inicia a partida
    jogadores = [["Alice", "vermelho", "humano"], 
                 ["Bob", "azul", "humano"], 
                 ["Charlie", "verde", "humano"]]
    
    state.partida_global = Partida(
        qtd_humanos=3, 
        qtd_ai=0, 
        duracao_turno=60, 
        tupla_jogadores=jogadores
    )
    
    yield client  # O teste executa aqui
    
    # Teardown: Limpa a partida após o teste
    state.partida_global = None