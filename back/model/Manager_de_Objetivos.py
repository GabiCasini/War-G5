import random

from .Jogador import Jogador

class Manager_de_Objetivos:
    def __init__(self, jogadores):
        self.objetivos_disponiveis = self.inicializa_objetivos(jogadores)
        self.objetivos_em_uso = self.atribui_objetivos(jogadores) # [objetivo, jogador]

    def inicializa_objetivos(self, jogadores):
        objetivos = ["Conquistar 24 territórios à sua escolha",
                     "Conquistar 18 territórios e ocupar cada um deles com pelo menos 2 exércitos",
                     "Conquistar na totalidade a Região 2 e a Região 5",
                     "Conquistar na totalidade a Região 4 e a Região 5",
                     "Conquistar na totalidade a Região 2 e a Região 6",
                     "Conquistar na totalidade a Região 1, a Região 3 e mais uma Região à sua escolha",
                     "Conquistar na totalidade a Região 1 e a Região 4",
                     "Conquistar na totalidade a Região 3, a Região 6 e mais uma Região à sua escolha"
                     ]
        
        for i in jogadores:
            objetivos.append("Elimine o jogador " + i.cor + ". Caso você seja esse jogador, ou ele já tenha sido eliminado, seu objetivo passa a ser conquistar 24 territórios")

        return objetivos
    
    def atribui_objetivos(self, jogadores):
        lista = []
        for i in jogadores:
            objetivo = random.choice(self.objetivos_disponiveis)
            self.objetivos_disponiveis.remove(objetivo)
            i.objetivo = objetivo
            lista.append([objetivo, i])

        return lista
        