class Territorio:
    def __init__(self, nome, cor, regiao):
        self.nome = nome
        self.exercitos = 1
        self.cor = cor
        self.regiao = regiao 
        self.fronteiras = []
        self.limite_de_repasse = 0


    def __repr__(self):
        return f"{self.nome} (Exércitos da cor {self.cor}: {self.exercitos})"
