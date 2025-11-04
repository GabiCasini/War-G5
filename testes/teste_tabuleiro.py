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

for i in partida.jogadores[0].territorios:
    i.exercitos = 22

partida.calcular_limite_de_reposicionamento(partida.jogadores[0])

for i in partida.jogadores[0].territorios:
    print(f"\nTerritorio: {i}, Limite de Repasse: {i.limite_de_repasse}")

for i in partida.jogadores[0].territorios:
    for j in i.fronteiras:
        if j.cor == partida.jogadores[0].cor:
            print(f"\nRealizando Reposicionamento:\n")
            partida.jogadores[0].reposicionar_exercitos(i, j, 10)
            print(f"Territorio: {i}, Limite de Repasse: {i.limite_de_repasse}\n")
            print(f"Territorio: {j}, Limite de Repasse: {j.limite_de_repasse}\n")
            break