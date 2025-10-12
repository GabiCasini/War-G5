import random
from .Partida import Partida
from .Jogador import Jogador
from .Territorio import Territorio

if __name__ == "__main__":
    print("Inicio de simulação de turnos")

    # Cria jogadores
    jogadores = [["Alice", "vermelho"], 
                 ["Bob", "azul"], 
                 ["Charlie", "verde"]
                ]
    partida = Partida(qtd_humanos=2, qtd_ai=1, duracao_turno=60, tupla_jogadores=jogadores)

    
    print("Jogadores e territórios distribuídos.")

    for jogador in partida.jogadores:
        nomes_territorios = [t.nome for t in jogador.territorios]
        print(f"Jogador: {jogador.nome} | Territórios: {nomes_territorios}")


    for i in range(3):
        jogador_da_vez = partida.jogadores[partida.jogador_atual_idx]

        print(f"\nTurno de {jogador_da_vez.nome} ({len(jogador_da_vez.territorios)} territórios)")
        
        partida.gerenciar_turno(jogador_da_vez)
        
        # Passa para o próximo jogador
        partida.proximo_jogador()