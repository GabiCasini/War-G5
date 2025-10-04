
from Jogador import Jogador
from Territorio import Territorio

class Partida:
    def __init__(self, qtd_humanos: int, qtd_ai: int, duracao_turno: int):
        assert 6 >= qtd_humanos + qtd_ai >= 3
        self.qtd_humanos = qtd_humanos
        self.qtd_ai = qtd_ai
        self.qtd_jogadores = qtd_humanos + qtd_ai
        self.duracao_turno = duracao_turno
        # self.jogadores = [] # Exemplo: lista de jogadores
        # self.territorios = [] # Exemplo: lista de territórios

    def resolver_combate(self, atacante: Jogador, defensor: Jogador, territorio_origem: Territorio, territorio_alvo: Territorio, exercitos_ataque: int, exercitos_defesa: int):
        """
        Resolve um combate entre atacante e defensor, atualizando exércitos e posse se necessário.
        """
        perdas_ataque, perdas_defesa = atacante.combate(exercitos_ataque, exercitos_defesa)
        atacante.remover_exercitos_territorio(territorio_origem, perdas_ataque)
        defensor.remover_exercitos_territorio(territorio_alvo, perdas_defesa)

        if territorio_alvo.exercitos == 0:
            self.transferir_territorio(atacante, defensor, territorio_alvo, territorio_origem, exercitos_ataque)
            return True  # território conquistado
        return False  # território não conquistado

    def transferir_territorio(self, vencedor: Jogador, perdedor: Jogador, territorio: Territorio, origem: Territorio, exercitos_ataque: int):
        """
        Transfere a posse do território para o vencedor e move exércitos obrigatórios.
        """
        perdedor.remover_territorio(territorio)
        vencedor.adicionar_territorio(territorio)
        # O atacante deve mover pelo menos o número de dados usados no ataque (exercitos_ataque)
        exercitos_para_mover = min(exercitos_ataque, origem.exercitos)
        vencedor.mover_exercitos(origem, territorio, exercitos_para_mover)
