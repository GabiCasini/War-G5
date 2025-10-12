class Territorio:
    def __init__(self, nome, cor, regiao):
        self.nome = nome
        self.exercitos = 1  # quantidade de exércitos no território
        self.cor = cor
        self.regiao = regiao
        self.fronteiras = []


    def __repr__(self):
        return f"{self.nome} (Exércitos da cor {self.cor}: {self.exercitos})"
