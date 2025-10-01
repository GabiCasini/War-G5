class Territorio:
    def __init__(self, nome):
        self.nome = nome
        self.exercitos = 0  # quantidade de exércitos no território

    def __repr__(self):
        return f"{self.nome} (Exércitos: {self.exercitos})"
