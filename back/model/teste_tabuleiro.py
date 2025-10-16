from .Partida import Partida

partida = Partida(3, 0, 120, [["Alice", "vermelho", "humano"], ["Bob", "azul", "humano"], ["Charlie", "verde", "humano"]])
print("Ordem de turno:")
print(partida.jogadores)
print()

partida.jogadores[0].territorios[0].exercitos = 3
partida.tabuleiro.territorios[5].exercitos = 5

for i in partida.jogadores:
    print(f"Territórios do Jogador {i.cor}")
    print()
    for j in i.territorios:
        print(j)
        print(j.fronteiras)
        print()