from .Partida import Partida

partida = Partida(3, 0, 120, [["Alice", "vermelho", "humano"], ["Bob", "azul", "humano"], ["Charlie", "verde", "humano"]])

print(f"Objetivos não utilizados: {partida.manager_de_objetivos.objetivos_disponiveis}\n")

print(f"Objetivos em uso: {partida.manager_de_objetivos.objetivos_em_uso}\n")

for i in partida.jogadores:
    print(f"\nObjetivo do Jogador {i.cor}: {i.objetivo}")