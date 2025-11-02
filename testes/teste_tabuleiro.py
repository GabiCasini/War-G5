from back.model.Partida import Partida

partida = Partida(3, 0, 120, [["Alice", "vermelho", "humano"], ["Bob", "azul", "humano"], ["Charlie", "verde", "humano"]])
print("Ordem de turno:")
print(partida.jogadores)

partida.jogadores[0].territorios[0].exercitos = 3
partida.tabuleiro.territorios[5].exercitos = 5

for i in partida.jogadores:
    print(f"\nTerritórios do Jogador {i.cor}:")
    for j in i.territorios:
        print(f"\n{j} - Fronteiras: {j.fronteiras}\n")

print("\nRegiões com bônus:")
print(partida.tabuleiro.regioes_com_bonus)

print(f"\n\nTerritórios em tabuleiro: {len(partida.tabuleiro.territorios)}")

for i in partida.tabuleiro.regioes_com_bonus:
    print(f"Territórios na {i[0]}: {len(i[2])}")

print()

for i in partida.jogadores:
    partida.tabuleiro.calcula_exercitos_a_receber(i)
    print(f"O Jogador {i.cor} tem {i.exercitos_reserva} exercitos a receber nesse turno")

for i in partida.tabuleiro.regioes_com_bonus[0][2]:
    i.cor = partida.jogadores[0].cor

print("\nDando territórios da Região 1 para o primeiro Jogador:")
partida.tabuleiro.calcula_exercitos_a_receber(partida.jogadores[0])
print(f"O Jogador {partida.jogadores[0].cor} tem {partida.jogadores[0].exercitos_reserva} exercitos a receber nesse turno")