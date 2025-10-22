from .Partida import Partida

partida = Partida(3, 0, 120, [["Alice", "vermelho", "humano"], ["Bob", "azul", "humano"], ["Charlie", "verde", "humano"]])

jogador = partida.jogadores[0]

print(f"Cartas do Jogador {jogador.cor}: {jogador.cartas}")

partida.verifica_ganho_de_carta(jogador, True)
partida.verifica_ganho_de_carta(jogador, True)
partida.verifica_ganho_de_carta(jogador, True)
partida.verifica_ganho_de_carta(jogador, True)

print(f"\nCartas do Jogador {jogador.cor}: {jogador.cartas}")
print(f"\nExercitos que não tem carta associada: {len(partida.manager_de_cartas.territorios_disponiveis)}")

partida.verifica_ganho_de_carta(jogador, True)
partida.verifica_ganho_de_carta(jogador, True)
partida.verifica_ganho_de_carta(jogador, True)

print(f"\nCartas do Jogador {jogador.cor}: {jogador.cartas}\n")
print(f"\nExercitos que não tem carta associada: {len(partida.manager_de_cartas.territorios_disponiveis)}\n")

print(f"Territórios com carta associada: {partida.manager_de_cartas.territorios_em_uso}")

print("\nIndique (um por um) o indice das cartas a serem trocadas: \n")

lista = []
for i in range(3):
    carta = int(input())
    lista.append(jogador.cartas[carta])

print(f"\nExercitos para posicionamento do Jogador {jogador.cor} antes da troca: {jogador.exercitos_reserva}")

partida.realizar_troca(jogador, lista)

print(f"\nExercitos para posicionamento do Jogador {jogador.cor} após a troca: {jogador.exercitos_reserva}")

print(f"\nCartas do Jogador {jogador.cor}: {jogador.cartas}")

print(f"\nExercitos que não tem carta associada: {len(partida.manager_de_cartas.territorios_disponiveis)}\n")

print(partida.manager_de_cartas.territorios_disponiveis)

print(f"\nNovo valor da troca: {partida.valor_da_troca}")

partida.incrementar_troca()
print(f"Incrementando troca... Novo valor: {partida.valor_da_troca}")

partida.incrementar_troca()
print(f"Incrementando troca... Novo valor: {partida.valor_da_troca}")

partida.incrementar_troca()
print(f"Incrementando troca... Novo valor: {partida.valor_da_troca}")

partida.incrementar_troca()
print(f"Incrementando troca... Novo valor: {partida.valor_da_troca}")

partida.incrementar_troca()
print(f"Incrementando troca... Novo valor: {partida.valor_da_troca}")

partida.incrementar_troca()
print(f"Incrementando troca... Novo valor: {partida.valor_da_troca}")

partida.incrementar_troca()
print(f"Incrementando troca... Novo valor: {partida.valor_da_troca}")

partida.incrementar_troca()
print(f"Incrementando troca... Novo valor: {partida.valor_da_troca}")

# testar também a passagem de cartas quando um jogador é eliminado
