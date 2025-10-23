import random

from .Jogador import Jogador

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
    
    # função para verificar se um único jogador específico cumpriu seu objetivo
    def verifica_objetivo_do_jogador(self, jogador: Jogador, jogadores_eliminados):
        return self.aux_confere_objetivo(jogador, jogadores_eliminados)
    
    # verifica se qualquer jogador cumpriu seu objetivo, priorizando: 1 - o jogador do turno; 2 - a ordem dos turnos 
    def verifica_objetivo_de_todos_os_jogadores(self, jogador_do_turno: Jogador, jogadores):
        # implementar lógica
        print("Não implementado ainda")
        
    # função auxiliar exclusiva das 2 funções acima, não deve ser chamada por nenhum outro arquivo
    def aux_confere_objetivo(self, jogador, jogadores_eliminados):
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
                # fazer lógica para cada caso
                return False
            
            case obj if "Elimine" in obj:
                for i in jogadores_eliminados:
                    if i.cor in obj:
                        if i == jogador or (i.eliminado_por != "nenhum" and i.eliminado_por != jogador.cor):
                            if len(jogador.territorios) >= 24:
                                return True
                            else:
                                return False
                            
                        elif i.eliminado_por == jogador.cor:
                            return True
                        
                        else:
                            return False
                        
                return False
            
            case _:
                print("\nObjetivo desconhecido!\n")
                return False
