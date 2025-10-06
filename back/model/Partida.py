import random
from Jogador import Jogador
from Tabuleiro import Tabuleiro
from Territorio import Territorio

class Partida:
    def __init__(self, qtd_humanos: int, qtd_ai: int, duracao_turno: int, tupla_jogadores: list[tuple[str, str]]): # tupla representa o jogador (nome, cor)
        assert 6 >= qtd_humanos + qtd_ai >= 3
        self.qtd_humanos = qtd_humanos
        self.qtd_ai = qtd_ai
        self.qtd_jogadores = qtd_humanos + qtd_ai
        self.duracao_turno = duracao_turno
        self.jogadores = self.criar_jogadores(tupla_jogadores)
        self.tabuleiro = Tabuleiro(self.jogadores) # cria o tabuleiro do jogo, que vai gerar todos os territórios, distribuindo eles para os jogadores
        random.shuffle(self.jogadores) # define a ordem dos turnos embaralhando a lista de jogadores

    # cria os objetos jogador a partir da tupla contendo o nome do jogador e sua respectiva cor
    def criar_jogadores(self, tupla_jogadores):
        lista = []
        for i in tupla_jogadores:
            lista.append(Jogador(i[0], i[1]))
        return lista
    
    def resolver_combate(self, atacante: Jogador, defensor: Jogador, territorio_origem: Territorio, territorio_alvo: Territorio):
        """
        Resolve um combate entre atacante e defensor, atualizando exércitos e posse se necessário.
        """
        
        if atacante == defensor:
            print("Atacante e defensor são o mesmo jogador.")
            return False
        
        if atacante.exercitos_no_territorio(territorio_origem) <=1:
            print("Atacante não possui exércitos suficientes para atacar.")
            return False
        
        #Dados de ataque
        if atacante.exercitos_no_territorio(territorio_origem) == 2:
            dados_ataque = 1

        elif atacante.exercitos_no_territorio(territorio_origem) == 3:
            dados_ataque = 2
            
        elif atacante.exercitos_no_territorio(territorio_origem) >= 4:
            dados_ataque = 3
        
        #Dados de defesa
        if defensor.exercitos_no_territorio(territorio_alvo) == 1:
            dados_defesa = 1

        elif defensor.exercitos_no_territorio(territorio_alvo) == 2:
            dados_defesa = 2

        elif defensor.exercitos_no_territorio(territorio_alvo) >= 3:
            dados_defesa = 3
        
        perdas_ataque, perdas_defesa = atacante.combate(dados_ataque, dados_defesa)
        atacante.remover_exercitos_territorio(territorio_origem, perdas_ataque)
        defensor.remover_exercitos_territorio(territorio_alvo, perdas_defesa)

        if territorio_alvo.exercitos == 0:
            self.transferir_territorio(atacante, defensor, territorio_alvo, territorio_origem, dados_ataque)
            return True  # território conquistado
        return False  # território não conquistado

    def transferir_territorio(self, vencedor: Jogador, perdedor: Jogador, territorio: Territorio, origem: Territorio, dados_ataque: int):
        """
        Transfere a posse do território para o vencedor e move exércitos obrigatórios.
        """
        perdedor.remover_territorio(territorio)
        vencedor.adicionar_territorio(territorio)
        territorio.cor = vencedor.cor  # Atualiza a cor do território para a do novo dono
        
        # O atacante deve mover pelo menos o número de dados usados no ataque (dados_ataque)
        exercitos_para_mover = min(dados_ataque, origem.exercitos)
        vencedor.mover_exercitos(origem, territorio, exercitos_para_mover)
