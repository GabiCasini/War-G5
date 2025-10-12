import random
import math
from .Territorio import Territorio
from .Jogador import Jogador

# lista onde cada elemento é uma lista que possui informações de cada territorio do jogo -> [nome, regiao, lista de fronteiras]
TERRITORIOS = [["Rio de Janeiro", "Regiao1", ["Niterói", "Mesquita"]], ["Niterói", "Regiao2", ["Rio de Janeiro", "Maricá"]],
               ["Mesquita", "Regiao1", ["Rio de Janeiro", "Maricá"]], ["Maricá", "Regiao2", ["Niterói", "Mesquita"]]]

class Tabuleiro:
    def __init__(self, jogadores):
        self.territorios = self.gerar_territorios(len(jogadores), jogadores)
        self.regioes_com_bonus = [["Regiao1", 2], ["Regiao2", 3]]
        
    #inicializa os territorios, atribui suas fronteiras, e atribui cada territorio a um jogador de acordo com a sua cor
    def gerar_territorios(self, num, jogadores):
        lista = []
        count = 0
        random.shuffle(TERRITORIOS)
        
        for i in TERRITORIOS:
            temp = Territorio(i[0], jogadores[count].cor, i[1])
            lista.append(temp)
            jogadores[count].adicionar_territorio(temp)
            
            if count == num - 1:
                count = 0
            else:
                count += 1

        for i in range(len(lista)):
            for j in range(len(lista)):
                if lista[j].nome in TERRITORIOS[i][2]:
                    lista[i].fronteiras.append(lista[j])

        return lista
    
    #Retorna a lista de territorios que o jogador daquela cor possui
    def recuperar_territorios_por_cor(self, cor):
        lista = []
        for i in self.territorios:
            if i.cor == cor:
                lista.append(i)

        return lista
    
    # calcula a quantidade de exercitos recebidos na fase de posicionamento
    # ainda não foi implementada a lógica dos bônus de região
    def calcula_tropas_a_receber(self, jogador: Jogador):
        lista = [0, 0, 0, 0, 0, 0, 0]

        lista[6] = int(max(3, math.floor(jogador.numero_de_territorios()/2)))
        
        jogador.adicionar_exercitos_para_posicionamento(lista)