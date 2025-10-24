import random

from .Jogador import Jogador
from .Tabuleiro import Tabuleiro

class Manager_de_Objetivos:
    def __init__(self, jogadores):
        self.objetivos_disponiveis = self.inicializa_objetivos(jogadores)
        self.atribui_objetivos(jogadores)

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
        for i in jogadores:
            objetivo = random.choice(self.objetivos_disponiveis)
            self.objetivos_disponiveis.remove(objetivo)
            i.objetivo = objetivo
    
    # verifica se qualquer jogador cumpriu seu objetivo, priorizando: 1 - o jogador do turno; 2 - a ordem dos turnos 
    # retorna a cor do vencedor (se houver), e False se ninguém ganhou
    def verifica_objetivo_de_todos_os_jogadores(self, jogador_do_turno: Jogador, jogadores_vivos, jogadores_eliminados, tabuleiro: Tabuleiro):
        vencedor = False

        for i in jogadores_vivos:
            resultado = self.verifica_objetivo_do_jogador(i, jogadores_eliminados, tabuleiro)
            if resultado and (jogador_do_turno == i or not vencedor):
                vencedor = i.cor
            
        return vencedor
        
    # função para verificar se um único jogador específico cumpriu seu objetivo
    def verifica_objetivo_do_jogador(self, jogador: Jogador, jogadores_eliminados, tabuleiro: Tabuleiro):
        objetivo = jogador.objetivo
        
        match objetivo:
            case "Conquistar 24 territórios à sua escolha":
                if len(jogador.territorios) >= 24:
                    return True
            
            case "Conquistar 18 territórios e ocupar cada um deles com pelo menos 2 exércitos":
                count = 0
                for i in jogador.territorios:
                    if i.exercitos > 1:
                        count += 1
                if count >= 18:
                    return True
            
            case obj if "Conquistar na totalidade" in obj:
                regioes_dominadas = tabuleiro.regioes_dominadas_pelo_jogador(jogador)

                if "Região 2 e a Região 5" in obj:
                    if regioes_dominadas[1] and regioes_dominadas[4]:
                        return True
                
                elif "Região 4 e a Região 5" in obj:
                    if regioes_dominadas[3] and regioes_dominadas[4]:
                        return True
                    
                elif "Região 2 e a Região 6" in obj:
                    if regioes_dominadas[1] and regioes_dominadas[5]:
                        return True
                    
                elif "Região 1 e a Região 4" in obj:
                    if regioes_dominadas[0] and regioes_dominadas[3]:
                        return True
                    
                elif "Região 1, a Região 3 e mais uma Região à sua escolha" in obj:
                    if regioes_dominadas[0] and regioes_dominadas[2] and sum(regioes_dominadas) > 2:
                        return True

                elif "Região 3, a Região 6 e mais uma Região à sua escolha" in obj:
                    if regioes_dominadas[2] and regioes_dominadas[5] and sum(regioes_dominadas) > 2:
                        return True

                return False
            
            case obj if "Elimine" in obj:
                if jogador.cor in obj and len(jogador.territorios) >= 24:
                    return True
                
                else:
                    for i in jogadores_eliminados:
                        if i.cor in obj:
                            if i.eliminado_por != jogador.cor:
                                if len(jogador.territorios) >= 24:
                                    return True
                                else:
                                    return False
                            
                            else:
                                return True
                        
                return False
            
            case _:
                print("\nObjetivo desconhecido!\n")
                return False
