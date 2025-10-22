import random
from .Territorio import Territorio

class Jogador:
    def __init__(self, nome: str, cor: str, tipo: str = "humano"):
        self.nome = nome
        self.cor = cor  # red, blue, green, orange, purple, yellow
        self.tipo = tipo  # 'humano' ou 'ai'
        self.territorios = []  # lista de objetos Territorio
        self.exercitos_reserva = [0, 0, 0, 0, 0, 0, 0]  # exércitos disponíveis para alocação para cada regiao e geral
        self.cartas = []
        self.objetivo = None

    def __repr__(self):
        return f"{self.nome} (Cor: {self.cor})"

    def adicionar_territorio(self, territorio: Territorio):
        territorio.cor = self.cor
        if territorio not in self.territorios:
            self.territorios.append(territorio)

    def remover_territorio(self, territorio: Territorio):
        if territorio in self.territorios:
            self.territorios.remove(territorio)

    # adiciona na lista exercitos_reserva os exércitos que o jogador poderá adicionar aos seus territórios na fase de posicionamento
    def adicionar_exercitos_para_posicionamento(self, quantidade: list[int]):
        for i in range (7):
            self.exercitos_reserva[i] = quantidade[i]

    # recebe uma lista com a quantidade de territórios que deve ser removida em cada índice
    # [regiao1, regiao2, regiao3, regiao4, regiao5, regiao6, geral]
    def remover_exercitos_para_posicionamento(self, quantidade: list[int]):
        for i in range (7):
            self.exercitos_reserva[i] = max(0, self.exercitos_reserva[i] - quantidade[i])

    def possui_territorio(self, territorio: Territorio):
        return territorio in self.territorios

    def exercitos_no_territorio(self, territorio: Territorio):
        if territorio in self.territorios:
            return territorio.exercitos
        return 0
    
    def adicionar_exercitos_territorio(self, territorio, quantidade):
        """Adiciona exércitos a um território do jogador."""
        if territorio in self.territorios:
            territorio.exercitos += quantidade
            print(f'Quantidade de exercito add: {quantidade}, Quantidade total de exercitos: {territorio.exercitos}')
        else:   
            print("Território não pertence ao jogador.")

    def remover_exercitos_territorio(self, territorio, quantidade):
        """Remove exércitos de um território do jogador."""
        if territorio in self.territorios:
            territorio.exercitos = max(0, territorio.exercitos - quantidade)
            print(f'Quantidade de exercito removido do {self.nome}: {quantidade}')
        else:
            print("Território não pertence ao jogador.")

    def mover_exercitos(self, origem, destino, quantidade):
        """Move exércitos de um território do jogador para outro."""
        if origem in self.territorios and destino in self.territorios and origem != destino:
            quantidade = min(quantidade, origem.exercitos - 1)
            origem.exercitos -= quantidade
            destino.exercitos += quantidade

    def combate(self, exercitos_ataque, exercitos_defesa):
        """
        Realiza a lógica de combate entre atacante e defensor.
        :param exercitos_ataque: int, quantidade de exércitos do atacante (máx 3)
        :param exercitos_defesa: int, quantidade de exércitos do defensor (máx 3)
        :return: (perdas_ataque, perdas_defesa)
        """
        dados_ataque = sorted([random.randint(1, 6) for _ in range(exercitos_ataque)], reverse=True)
        dados_defesa = sorted([random.randint(1, 6) for _ in range(exercitos_defesa)], reverse=True)

        perdas_ataque = 0
        perdas_defesa = 0

        for dado_a, dado_d in zip(dados_ataque, dados_defesa):
            if dado_d >= dado_a:
                perdas_ataque += 1
            else:
                perdas_defesa += 1

        return perdas_ataque, perdas_defesa
    
    def numero_de_territorios(self):
        return len(self.territorios)
    
    def numero_de_exercitos(self):
        soma = 0
        for i in self.territorios:
            soma += i.exercitos

        return soma
    
    def adicionar_carta(self, carta):
        self.cartas.append(carta)

    def remover_carta(self, carta):
        self.cartas.remove(carta)

    def trocar_cartas(self, cartas, valor_da_troca):
        self.adicionar_exercitos_para_posicionamento([0, 0, 0, 0, 0, 0, valor_da_troca])

        for i in cartas:
            if i[0] != "Coringa":
                for j in self.territorios:
                    if j.nome == i[1]:
                        self.adicionar_exercitos_territorio(j, 2)
            self.remover_carta(i)

    