import random
from Territorio import Territorio

class Jogador:
    def __init__(self, nome, cor, tipo='humano'):
        self.nome = nome
        self.cor = cor  # cor do jogador no mapa
        self.tipo = tipo  # 'humano' ou 'ai'
        self.territorios = []  # lista de objetos Territorio
        self.exercitos_reserva = 0  # exércitos disponíveis para alocação

    def adicionar_territorio(self, territorio: Territorio):
        if territorio not in self.territorios:
            self.territorios.append(territorio)

    def remover_territorio(self, territorio: Territorio):
        if territorio in self.territorios:
            self.territorios.remove(territorio)

    def adicionar_exercitos(self, quantidade):
        self.exercitos_reserva += quantidade

    def remover_exercitos(self, quantidade):
        self.exercitos_reserva = max(0, self.exercitos_reserva - quantidade)

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
            print(f'Quantidade de exercito add: {territorio.exercitos}')
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
            quantidade = min(quantidade, origem.exercitos)
            origem.exercitos -= quantidade
            destino.exercitos += quantidade

    def combate(self, exercitos_ataque, exercitos_defesa):
        """
        Realiza a lógica de combate entre atacante e defensor.
        :param exercitos_ataque: int, quantidade de exércitos do atacante (máx 3)
        :param exercitos_defesa: int, quantidade de exércitos do defensor (máx 2)
        :return: (perdas_ataque, perdas_defesa)
        """
        dados_ataque = sorted([random.randint(1, 6) for _ in range(min(3, exercitos_ataque))], reverse=True)
        dados_defesa = sorted([random.randint(1, 6) for _ in range(min(2, exercitos_defesa))], reverse=True)

        perdas_ataque = 0
        perdas_defesa = 0

        for dado_a, dado_d in zip(dados_ataque, dados_defesa):
            if dado_d >= dado_a:
                perdas_ataque += 1
            else:
                perdas_defesa += 1

        return perdas_ataque, perdas_defesa