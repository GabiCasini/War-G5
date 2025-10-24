from .Partida import Partida

partida = Partida(3, 0, 120, [["Alice", "vermelho", "humano"], ["Bob", "azul", "humano"], ["Charlie", "verde", "humano"]])
print("Ordem de turno:")
print(partida.jogadores)
print()

partida.jogadores[0].territorios[0].exercitos = 3
partida.tabuleiro.territorios[5].exercitos = 5

for i in partida.jogadores:
    print(f"\nTerritórios do Jogador {i.cor}:")
    print()
    for j in i.territorios:
        print(j)
        print(j.fronteiras)
        print()

print("\n\nRegiões com bônus:")
for i in partida.tabuleiro.regioes_com_bonus:
    print(i)
    print()

print(f"\n\nTerritórios em tabuleiro: {len(partida.tabuleiro.territorios)}")

for i in partida.tabuleiro.regioes_com_bonus:
    print(f"Territórios na {i[0]}: {len(i[2])}")

print()

for i in partida.jogadores:
    partida.tabuleiro.calcula_exercitos_a_receber(i)
    print(f"O Jogador {i.cor} tem {i.exercitos_reserva} exercitos a receber nesse turno")