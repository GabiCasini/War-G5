from .Partida import Partida

partida = Partida(3, 0, 120, [["Alice", "vermelho", "humano"], ["Bob", "azul", "humano"], ["Charlie", "verde", "humano"]])

print(f"Objetivos não utilizados: {partida.manager_de_objetivos.objetivos_disponiveis}\n")

for i in partida.jogadores:
    print(f"\nObjetivo do Jogador {i.cor}: {i.objetivo}")

jogador_a = partida.jogadores[0]
jogador_b = partida.jogadores[1]
jogador_c = partida.jogadores[2]

partida.jogadores.remove(jogador_b)
#jogador_b.eliminado_por = jogador_a.cor
jogador_b.eliminado_por = jogador_c.cor
partida.jogadores_eliminados.append(jogador_b)

jogador_a.objetivo = "Elimine o jogador " + jogador_b.cor + ". Caso você seja esse jogador, ou ele já tenha sido eliminado, seu objetivo passa a ser conquistar 24 territórios"

if partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador_a, partida.jogadores_eliminados):
    print(f"\nJogador {jogador_a.cor} venceu a partida!\n")
    print(f"Objetivo: {jogador_a.objetivo}")

else:
    print("\nNinguém venceu!\n")

