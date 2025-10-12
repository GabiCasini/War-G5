from .Partida import Partida

partida = Partida(3, 0, 120, [["Jogador1", "Vermelha"], ["Jogador2", "Azul"]])
print("Ordem de turno:")
print(partida.jogadores)
print()

for i in partida.tabuleiro.territorios:
    print(i)
    print(i.fronteiras)
    print()

#partida.jogadores[0].territorios = partida.tabuleiro.recuperar_territorios_por_cor(partida.jogadores[0].cor)
print("Territorios do Jogador Vermelho:")
print(partida.jogadores[0].territorios)

#partida.jogadores[1].territorios = partida.tabuleiro.recuperar_territorios_por_cor(partida.jogadores[1].cor)
print("\nTerritorios do Jogador Azul:")
print(partida.jogadores[1].territorios)

partida.jogadores[0].territorios[0].exercitos = 3
partida.tabuleiro.territorios[1].exercitos = 5

print("\nAlterando exercitos:")
for i in partida.tabuleiro.territorios:
    print(i)
    print(i.fronteiras)
    print()