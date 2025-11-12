import random
import math
from .Territorio import Territorio
from .Jogador import Jogador
from back.utils.territorios_loader import carregar_territorios_json

class Tabuleiro:
    def __init__(self, jogadores: list[Jogador]):
        # [nome da região, bônus, territórios pertences à região]
        self.regioes_com_bonus = [["Regiao_1", 2, []], ["Regiao_2", 5, []], ["Regiao_3", 5, []], ["Regiao_4", 6, []], ["Regiao_5", 4, []], ["Regiao_6", 2, []]]
        self.territorios = self.gerar_territorios(len(jogadores), jogadores)
        
    def gerar_territorios(self, num: int, jogadores: list[Jogador]):
        """
        Inicializa os territórios carregados do JSON, atribui suas fronteiras,
        e atribui cada território a um jogador de acordo com a sua cor.
        """
        lista = []
        count = 0
        
        # Carrega territórios do JSON
        TERRITORIOS = carregar_territorios_json()
        random.shuffle(TERRITORIOS)
        
        # Cria objetos Territorio e distribui entre jogadores
        for t_dados in TERRITORIOS:
            temp = Territorio(t_dados['nome'], jogadores[count].cor, t_dados['regiao'])
            lista.append(temp)
            jogadores[count].adicionar_territorio(temp)

            # Adiciona à região com bônus
            for regiao_info in self.regioes_com_bonus:
                if regiao_info[0] == temp.regiao:
                    regiao_info[2].append(temp)
            
            if count == num - 1:
                count = 0
            else:
                count += 1

        # Cria as fronteiras referenciando os objetos Territorio
        mapa_nomes = {territorio.nome: territorio for territorio in lista}
        
        for i, t_dados in enumerate(TERRITORIOS):
            territorio_obj = mapa_nomes[t_dados['nome']]
            for nome_fronteira in t_dados['fronteiras']:
                if nome_fronteira in mapa_nomes:
                    territorio_obj.fronteiras.append(mapa_nomes[nome_fronteira])

        return lista
        
    def inicializar_exercitos_a_receber(self, jogadores: list[Jogador]):
        # Só inicializa para o primeiro jogador, pois os outros receberão seus exércitos ao final do turno de cada jogador anterior
        self.calcula_exercitos_a_receber(jogador=jogadores[0])
    
    # calcula a quantidade de exercitos recebidos na fase de posicionamento
    def calcula_exercitos_a_receber(self, jogador: Jogador):
        valor = 0
        regioes_dominadas = self.regioes_dominadas_pelo_jogador(jogador)

        for i in range(6):
            if regioes_dominadas[i]:
                valor += self.regioes_com_bonus[i][1]

        valor += int(max(3, math.floor(len(jogador.territorios)/2)))
        
        jogador.adicionar_exercitos_para_posicionamento(valor)
        
    def regioes_dominadas_pelo_jogador(self, jogador: Jogador):
        lista = [1, 1, 1, 1, 1, 1]

        for i in range(6):
            for j in self.regioes_com_bonus[i][2]:
                if j.cor != jogador.cor:
                    lista[i] = 0
                    break

        return lista