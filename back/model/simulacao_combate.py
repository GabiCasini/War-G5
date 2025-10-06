
from Jogador import Jogador
from Territorio import Territorio
from Partida import Partida

if __name__ == "__main__":
    
    # Cria jogadores
    jogadores = [["Alice", "vermelho"], 
                 ["Bob", "azul"], 
                 ["Charlie", "verde"]
                ]
    

    # Cria partida
    partida = Partida(qtd_humanos=2, qtd_ai=1, duracao_turno=60, tupla_jogadores=jogadores)

    # Cria dois jogadores
    # jogador_a = Jogador(jogadores[0][0], jogadores[0][1])
    # jogador_b = Jogador(jogadores[1][0], jogadores[1][1])
    jogador_a = partida.jogadores[0]
    jogador_b = partida.jogadores[1]
    
    print(f'jogador a = {jogador_a}')
    
    print(f'jogador b = {jogador_b}')   
    
    print(jogador_a.territorios)
    print(jogador_b.territorios)
    

    # Cria territórios
    territorio_a = Territorio("Rio de Janeiro", jogador_a.cor, "Regiao1")
    territorio_b = Territorio("São Paulo", jogador_b.cor, "Regiao2")

    # Adiciona territórios aos jogadores
    jogador_a.adicionar_territorio(territorio_a)
    jogador_b.adicionar_territorio(territorio_b)

    # Define exércitos nos territórios
    jogador_a.adicionar_exercitos_territorio(territorio_a, 5)  # atacante
    jogador_b.adicionar_exercitos_territorio(territorio_b, 2)  # defensor

    print("Antes do ataque:")
    print(territorio_a)
    print(territorio_b)

    # Realiza o combate
    conquistado = partida.resolver_combate(jogador_a, jogador_b, territorio_a, territorio_b)

    print("\nDepois do ataque:")
    print(territorio_a)
    print(territorio_b)

    if conquistado:
        print(f"\n{jogador_a.nome} conquistou {territorio_b.nome}!")
        print(f"Exércitos em {territorio_a.nome}: {territorio_a.exercitos}")
        print(f"Exércitos em {territorio_b.nome}: {territorio_b.exercitos}")

    print(f'jogador a = {jogador_a.territorios}')
    print(f'jogador b = {jogador_b.territorios}')