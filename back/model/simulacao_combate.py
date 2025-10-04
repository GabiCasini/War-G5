
from Jogador import Jogador
from Territorio import Territorio
from Partida import Partida

if __name__ == "__main__":
    # Cria partida
    partida = Partida(qtd_humanos=2, qtd_ai=1, duracao_turno=60)

    # Cria dois jogadores
    jogador_a = Jogador("Alice", "vermelho")
    jogador_b = Jogador("Bob", "azul")

    # Cria territórios
    territorio_a = Territorio("Rio de Janeiro")
    territorio_b = Territorio("São Paulo")

    # Adiciona territórios aos jogadores
    jogador_a.adicionar_territorio(territorio_a)
    jogador_b.adicionar_territorio(territorio_b)

    # Define exércitos nos territórios
    jogador_a.adicionar_exercitos_territorio(territorio_a, 5)  # atacante
    jogador_b.adicionar_exercitos_territorio(territorio_b, 2)  # defensor

    print("Antes do ataque:")
    print(territorio_a)
    print(territorio_b)

    # Simula ataque usando a lógica da Partida
    exercitos_ataque = 3  # Alice ataca com 3
    exercitos_defesa = 2  # Bob defende com 2
    conquistado = partida.resolver_combate(jogador_a, jogador_b, territorio_a, territorio_b, exercitos_ataque, exercitos_defesa)

    print("\nDepois do ataque:")
    print(territorio_a)
    print(territorio_b)

    if conquistado:
        print(f"\n{jogador_a.nome} conquistou {territorio_b.nome}!")
        print(f"Exércitos em {territorio_a.nome}: {territorio_a.exercitos}")
        print(f"Exércitos em {territorio_b.nome}: {territorio_b.exercitos}")

    print(f'jogador a = {jogador_a.territorios}')
    print(f'jogador b = {jogador_b.territorios}')