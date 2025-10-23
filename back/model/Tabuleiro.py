import random
import math
from .Territorio import Territorio
from .Jogador import Jogador

# lista onde cada elemento é uma lista que possui informações de cada territorio do jogo -> [nome, regiao, lista de fronteiras]
TERRITORIOS = [["Rio de Janeiro", "Regiao_1", ["Nova Iguaçu", "Mesquita", "São João de Meriti", "Niterói"]],
               ["Nova Iguaçu", "Regiao_1", ["Rio de Janeiro", "Mesquita", "Seropédica"]],
               ["Mesquita", "Regiao_1", ["Rio de Janeiro", "Nova Iguaçu", "São João de Meriti"]],
               ["São João de Meriti", "Regiao_1", ["Rio de Janeiro", "Mesquita"]], 
               ["Seropédica", "Regiao_2", ["Nova Iguaçu", "Queimados", "Japeri", "Paracambi"]],
               ["Queimados", "Regiao_2", ["Japeri", "Seropédica"]],
               ["Japeri", "Regiao_2", ["Miguel Pereira", "Queimados", "Seropédica", "Paracambi"]],
               ["Paracambi", "Regiao_2", ["Miguel Pereira", "Eng Paulo de Frontin", "Seropédica", "Japeri"]],
               ["Miguel Pereira", "Regiao_2", ["Paty do Alferes", "Vassouras", "Eng Paulo de Frontin", "Japeri", "Paracambi"]],
               ["Eng Paulo de Frontin", "Regiao_2", ["Vassouras", "Miguel Pereira", "Paracambi"]],
               ["Vassouras", "Regiao_2", ["Paty do Alferes", "Miguel Pereira", "Eng Paulo de Frontin", "Paraíba do Sul"]],
               ["Paty do Alferes", "Regiao_2", ["Vassouras", "Miguel Pereira", "Paraíba do Sul"]],
               ["Paraíba do Sul", "Regiao_2", ["Paty do Alferes", "Vassouras", "Comendador Levy Gasparian"]],
               ["Comendador Levy Gasparian", "Regiao_3", ["Três Rios", "Paraíba do Sul"]],
               ["Três Rios", "Regiao_3", ["Comendador Levy Gasparian", "Sapucaia", "Areal"]],
               ["Areal", "Regiao_3", ["Petrópolis", "Três Rios"]],
               ["Sapucaia", "Regiao_3", ["Três Rios", "Teresópolis", "São José do Vale do Rio Preto"]],
               ["Petrópolis", "Regiao_3", ["Areal", "Teresópolis", "Magé", "Guapimirim"]],
               ["Teresópolis", "Regiao_3", ["Sapucaia", "Petrópolis", "Cachoeiras de Macacu", "Guapimirim", "Nova Friburgo"]],
               ["Cachoeiras de Macacu", "Regiao_3", ["Teresópolis", "Guapimirim", "Itaboraí"]],
               ["São José do Vale do Rio Preto", "Regiao_4", ["Sapucaia", "Sumidouro"]],
               ["Sumidouro", "Regiao_4", ["São José do Vale do Rio Preto", "Carmo", "Duas Barras", "Nova Friburgo"]],
               ["Nova Friburgo", "Regiao_4", ["Teresópolis", "Sumidouro", "Duas Barras", "Bom Jardim", "Cordeiro", "Trajano de Moraes"]],
               ["Bom Jardim", "Regiao_4", ["Duas Barras", "Nova Friburgo", "Macuco"]],
               ["Duas Barras", "Regiao_4", ["Cantagalo", "Carmo", "Sumidouro", "Nova Friburgo", "Bom Jardim"]],
               ["Carmo", "Regiao_4", ["Cantagalo", "Duas Barras", "Sumidouro"]],
               ["Cantagalo", "Regiao_4", ["Duas Barras", "Carmo", "Macuco", "São Sebastião do Alto", "Itaocara", "Santo Antônio de Pádua"]],
               ["Macuco", "Regiao_4", ["Cantagalo", "São Sebastião do Alto", "Bom Jardim"]],
               ["São Sebastião do Alto", "Regiao_4", ["Cantagalo", "Macuco", "Itaocara"]],
               ["Itaocara", "Regiao_4", ["Cantagalo", "São Sebastião do Alto", "Santo Antônio de Pádua", "Cambuci"]],
               ["Santo Antônio de Pádua", "Regiao_4", ["Cantagalo", "Itaocara", "Cambuci"]],
               ["Cambuci", "Regiao_4", ["Santo Antônio de Pádua", "Itaocara"]],
               ["Magé", "Regiao_5", ["Petrópolis", "Guapimirim"]],
               ["Guapimirim", "Regiao_5", ["Petrópolis", "Magé", "Teresópolis", "Cachoeiras de Macacu", "Itaboraí"]],
               ["Itaboraí", "Regiao_5", ["Guapimirim", "Cachoeiras de Macacu", "São Gonçalo", "Maricá"]],
               ["São Gonçalo", "Regiao_5", ["Itaboraí", "Maricá", "Niterói"]],
               ["Maricá", "Regiao_5", ["Itaboraí", "São Gonçalo", "Niterói"]],
               ["Niterói", "Regiao_5", ["São Gonçalo", "Maricá", "Rio de Janeiro"]],
               ["Cordeiro", "Regiao_6", ["Nova Friburgo", "Trajano de Moraes"]],
               ["Trajano de Moraes", "Regiao_6", ["Nova Friburgo", "Cordeiro", "Macaé"]],
               ["Macaé", "Regiao_6", ["Trajano de Moraes", "Casimiro de Abreu"]],
               ["Casimiro de Abreu", "Regiao_6", ["Macaé"]]
               ]

class Tabuleiro:
    def __init__(self, jogadores):
        # [nome da região, bônus, territórios pertences à região]
        self.regioes_com_bonus = [["Regiao_1", 2, []], ["Regiao_2", 5, []], ["Regiao_3", 5, []], ["Regiao_4", 6, []], ["Regiao_5", 4, []], ["Regiao_6", 2, []]]
        self.territorios = self.gerar_territorios(len(jogadores), jogadores)
        
    #inicializa os territorios, atribui suas fronteiras, e atribui cada territorio a um jogador de acordo com a sua cor
    def gerar_territorios(self, num, jogadores):
        lista = []
        count = 0
        random.shuffle(TERRITORIOS)
        
        for i in TERRITORIOS:
            temp = Territorio(i[0], jogadores[count].cor, i[1])
            lista.append(temp)
            jogadores[count].adicionar_territorio(temp)

            for i in self.regioes_com_bonus:
                if i[0] == temp.regiao:
                    i[2].append(temp)
            
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
    def calcula_exercitos_a_receber(self, jogador: Jogador):
        lista = [0, 0, 0, 0, 0, 0, 0]

        for i in range(6):
            dominado = True
            for j in self.regioes_com_bonus[i][2]:
                if j.cor != jogador.cor:
                    dominado = False
                    break
            if dominado:
                lista[i] = self.regioes_com_bonus[i][1]

        lista[6] = int(max(3, math.floor(len(jogador.territorios)/2)))
        
        jogador.adicionar_exercitos_para_posicionamento(lista)
        
    def regioes_dominadas_pelo_jogador(self, jogador: Jogador):
        lista = [1, 1, 1, 1, 1, 1]

        for i in range(6):
            for j in self.regioes_com_bonus[i][2]:
                if j.cor != jogador.cor:
                    lista[i] = 0
                    break

        return lista