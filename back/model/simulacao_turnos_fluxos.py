import random
from Partida import Partida
from Jogador import Jogador
from Territorio import Territorio

if __name__ == "__main__":
    print("Inicio de simulação de turnos")

    partida = Partida(qtd_humanos=2, qtd_ai=1, duracao_turno=60)

    cores = ["Azul", "Vermelho", "Verde"]
    jogador1 = Jogador("Gabizinha", cores[0], tipo='humano')
    jogador2 = Jogador("Raio", cores[1], tipo='humano')
    jogador3 = Jogador("IA 1", cores[2], tipo='ai')
    partida.jogadores = [jogador1, jogador2, jogador3]
    random.shuffle(partida.jogadores)

    nomes_territorios = ["Pavuna", "Méier", "Marechal Hermes", "Bonsucesso", "Honorio Gurgel", "Campo Grande"]
    partida.territorios = [Territorio(nome) for nome in nomes_territorios]

    territorios_a_distribuir = partida.territorios[:]
    idx_jogador = 0
    for territorio in territorios_a_distribuir:
        jogador_atual = partida.jogadores[idx_jogador]
        jogador_atual.adicionar_territorio(territorio)
        territorio.exercitos = 1
        idx_jogador = (idx_jogador + 1) % partida.qtd_jogadores
    
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