from .Partida import Partida

partida = Partida(3, 0, 120, [["Alice", "vermelho", "humano"], ["Bob", "azul", "humano"], ["Charlie", "verde", "humano"]])

print(f"Objetivos não utilizados: {partida.manager_de_objetivos.objetivos_disponiveis}\n")

for i in partida.jogadores:
    print(f"\nObjetivo do Jogador {i.cor}: {i.objetivo}")

jogador_a = partida.jogadores[0]
jogador_b = partida.jogadores[1]
jogador_c = partida.jogadores[2]

partida.jogadores.remove(jogador_b)
jogador_b.eliminado_por = jogador_a.cor
#jogador_b.eliminado_por = jogador_c.cor
partida.jogadores_eliminados.append(jogador_b)

jogador_a.objetivo = "Elimine o jogador " + jogador_b.cor + ". Caso você seja esse jogador, ou ele já tenha sido eliminado, seu objetivo passa a ser conquistar 24 territórios"
jogador_c.objetivo = "Conquistar na totalidade a Região 1 e a Região 4"

if partida.manager_de_objetivos.verifica_objetivo_do_jogador(jogador_a, partida.jogadores_eliminados, partida.tabuleiro):
    print(f"\nJogador {jogador_a.cor} venceu a partida!\n")
    print(f"Objetivo: {jogador_a.objetivo}")

else:
    print("\nNinguém venceu!\n")

print("\nVerificando Funções de validação de objetivo:\n")

print(f"Regiões dominadas pelo Jogador {jogador_a.cor}: {partida.tabuleiro.regioes_dominadas_pelo_jogador(jogador_a)}\n")
print(f"Regiões dominadas pelo Jogador {jogador_b.cor}: {partida.tabuleiro.regioes_dominadas_pelo_jogador(jogador_b)}\n")
print(f"Regiões dominadas pelo Jogador {jogador_c.cor}: {partida.tabuleiro.regioes_dominadas_pelo_jogador(jogador_c)}\n")

for i in partida.tabuleiro.regioes_com_bonus[0][2]:
    i.cor = jogador_c.cor

for i in partida.tabuleiro.regioes_com_bonus[3][2]:
    i.cor = jogador_c.cor

print("\nObjetivos dos jogadores após a alteração:")
for i in partida.jogadores:
    print(f"\nObjetivo do Jogador {i.cor}: {i.objetivo}")

print(f"\nRegiões dominadas pelo Jogador {jogador_c.cor} após alteração: {partida.tabuleiro.regioes_dominadas_pelo_jogador(jogador_c)}\n")

resultado = partida.manager_de_objetivos.verifica_objetivo_de_todos_os_jogadores(jogador_a, partida.jogadores, partida.jogadores_eliminados, partida.tabuleiro)

if resultado:
    print(f"Jogador {resultado} venceu!")

resultado = partida.manager_de_objetivos.verifica_objetivo_de_todos_os_jogadores(jogador_c, partida.jogadores, partida.jogadores_eliminados, partida.tabuleiro)

if resultado:
    print(f"Jogador {resultado} venceu!")