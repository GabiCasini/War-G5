from .Partida import Partida

if __name__ == "__main__":
    
    # Cria jogadores
    jogadores = [["Alice", "vermelho"], 
                 ["Bob", "azul"], 
                 ["Charlie", "verde"]
                ]
    

    # Cria partida
    partida = Partida(qtd_humanos=2, qtd_ai=1, duracao_turno=60, tupla_jogadores=jogadores)

    # Referencia dois jogadores criados em partida
    jogador_a = partida.jogadores[0]
    jogador_b = partida.jogadores[1]
    
    print(f'jogador a = {jogador_a}')
    print(f'jogador b = {jogador_b}')   
    
    print(jogador_a.territorios)
    print(jogador_b.territorios)
    

    # Referencia o primeiro territorio atribuído a cada jogador
    territorio_a = jogador_a.territorios[0]
    territorio_b = jogador_b.territorios[0]

    # Adiciona exércitos nos territórios
    jogador_a.adicionar_exercitos_territorio(territorio_a, 2)  # atacante
    jogador_b.adicionar_exercitos_territorio(territorio_b, 0)  # defensor

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
        
        partida.verificar_eliminacao(jogador_b) # retorna true ou false (em caso de true, partida remove o jogador da lista de jogadores)

    print(f'jogador a = {jogador_a.territorios}')
    print(f'jogador b = {jogador_b.territorios}')

    partida.tabuleiro.calcula_exercitos_a_receber(jogador_a)
    print(f"\nTerritorios a receber do Jogador {jogador_a.cor}: {jogador_a.exercitos_reserva}")