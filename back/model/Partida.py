import random
from Jogador import Jogador
from Territorio import Territorio

class Partida:
    def __init__(self, qtd_humanos: int, qtd_ai: int, duracao_turno: int):
        assert 6 >= qtd_humanos + qtd_ai >= 3
        self.qtd_humanos = qtd_humanos
        self.qtd_ai = qtd_ai
        self.qtd_jogadores = qtd_humanos + qtd_ai
        self.duracao_turno = duracao_turno
        
        self.jogadores = []
        self.territorios = []
        self.jogador_atual_idx = 0
        self.fase_do_turno = "preparacao"  # 'preparacao', 'posicionamento', 'ataque', 'remanejamento'


    def proximo_jogador(self):
        """Passa a vez para o próximo jogador."""
        self.jogador_atual_idx = (self.jogador_atual_idx + 1) % self.qtd_jogadores

    def gerenciar_turno(self, jogador: Jogador):
        """Orquestra as três fases do turno de um jogador."""
        # Fase de Posicionamento
        self.fase_do_turno = "posicionamento"
        print(f"Fase de {self.fase_do_turno}...")
        self.fase_de_posicionamento(jogador)

        # Fase de Ataque
        self.fase_do_turno = "ataque"
        print(f"Fase de {self.fase_do_turno}...")
        self.fase_de_ataque(jogador)

        # Fase de remanejamento
        self.fase_do_turno = "remanejamento"
        print(f"Fase de {self.fase_do_turno}...")
        self.fase_de_remanejamento(jogador)
        
        print(f"Fim do turno de {jogador.nome}")
    
    def fase_de_ataque(self, jogador: Jogador):
        """Lógica para o jogador realizar ataques."""
        print("O jogador decide se e como irá atacar.")
        pass # 'pass' significa que o método não faz nada

    def fase_de_remanejamento(self, jogador: Jogador):
        """Lógica para o jogador mover exércitos."""
        print("O jogador decide se e como irá remanejar seus exércitos.")
        pass

    def calcular_exercitos_novos(self, jogador: Jogador):
        """Calcula a quantidade de exércitos que o jogador recebe."""
        exercitos_ganhos = max(3, len(jogador.territorios) // 3)
        print(f"{jogador.nome} recebe {exercitos_ganhos} novos exércitos.")
        return exercitos_ganhos

    def fase_de_posicionamento(self, jogador: Jogador):
        """Lógica para o jogador posicionar seus novos exércitos."""
        exercitos_a_posicionar = self.calcular_exercitos_novos(jogador)
        # TODO: Substituir lógica aleatória por input do usuário ou lógica da IA
        if jogador.tipo == 'humano':
            print(f"Você tem {exercitos_a_posicionar} exércitos para posicionar.")
            # Coloca tudo no primeiro território
            territorio_escolhido = jogador.territorios[0]
            jogador.adicionar_exercitos_territorio(territorio_escolhido, exercitos_a_posicionar)
            print(f"{jogador.nome} posicionou {exercitos_a_posicionar} em {territorio_escolhido.nome}.")

    

    def resolver_combate(self, atacante: Jogador, defensor: Jogador, territorio_origem: Territorio, territorio_alvo: Territorio, exercitos_ataque: int):
        
        """
        Resolve um combate entre atacante e defensor, atualizando exércitos e posse se necessário.
        """
        # Conserto de assinatura do metodo, agora recebe apenas exercitos_ataque
        # Uso a defesa que esta no territorio alvo
        exercitos_defesa = territorio_alvo.exercitos
        
        perdas_ataque, perdas_defesa = atacante.combate(exercitos_ataque, exercitos_defesa)
        
        atacante.remover_exercitos_territorio(territorio_origem, perdas_ataque)
        defensor.remover_exercitos_territorio(territorio_alvo, perdas_defesa)
        
        # Sugestao para ver o resultado do combate
        # print(f"Combate em {territorio_alvo.nome}: Atacante perdeu {perdas_ataque}, Defensor perdeu {perdas_defesa}.")

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
        
        # Garante que o território de origem fique com pelo menos 1 exército.
        # O jogador deve mover no mínimo `exercitos_ataque` e no máximo o que tiver, menos 1.
        # O atacante deve mover pelo menos o número de dados usados no ataque (exercitos_ataque)
        exercitos_para_mover = min(exercitos_ataque, origem.exercitos - 1)
        
        vencedor.mover_exercitos(origem, territorio, exercitos_para_mover)
        