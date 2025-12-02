import pickle
import os

# Variavel para segurar o estado atual do jogo
partida_global = None
ARQUIVO = "partida.pkl"

def salvar_partida(partida):
    with open(ARQUIVO, "wb") as f:
        pickle.dump(partida, f)

def carregar_partida():
    with open(ARQUIVO, "rb") as f:
        partida = pickle.load(f)
        os.remove(ARQUIVO)  # Remove o arquivo apos carregar a partida
        return partida
    
def apagar_partida():
    if os.path.exists(ARQUIVO):
        os.remove(ARQUIVO)