import random
import re

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

            # Para jogadores humanos, manter o texto original (legível).
            # Para IAs, mapear para uma estrutura (dict) quando possível para evitar tratamentos condicionais
            # no código da IA (que espera dicts) — caso não seja possível mapear, atribuímos None.
            if getattr(i, 'tipo', 'humano') == 'ai':
                i.objetivo = self._map_objetivo_para_dict(objetivo)
            else:
                i.objetivo = objetivo

    def _map_objetivo_para_dict(self, objetivo_str: str):
        """
        Tenta converter um objetivo textual em um dicionário com campos explícitos que a IA entende.
        Retorna None se o objetivo não puder ser mapeado de forma conservadora.
        """
        if not isinstance(objetivo_str, str):
            return None

        s = objetivo_str.strip()

        # Conquistar N territórios
        if s.startswith("Conquistar 24"):
            return {"tipo": "conquistar_territorios", "quantidade": 24}

        if "Conquistar 18 territórios" in s:
            return {"tipo": "conquistar_territorios_exercitos", "quantidade": 18, "min_exercitos": 2}

        # Conquistar na totalidade a Região X e a Região Y
        m = re.search(r"Reg[ií]o\s*(\d+).*Reg[ií]o\s*(\d+)", s)
        if m:
            reg1 = f"Região {m.group(1)}"
            reg2 = f"Região {m.group(2)}"
            return {"tipo": "conquistar_continentes", "continentes": [reg1, reg2]}

        # Casos com 3 regiões ("Região 1, a Região 3 e mais uma Região à sua escolha")
        m3 = re.search(r"Reg[ií]o\s*(\d+),\s*a\s*Reg[ií]o\s*(\d+).*mais uma Reg[ií]o", s)
        if m3:
            reg1 = f"Região {m3.group(1)}"
            reg2 = f"Região {m3.group(2)}"
            return {"tipo": "conquistar_continentes", "continentes": [reg1, reg2], "min_total": 3}

        # Elimine o jogador X
        m_elim = re.search(r"Elimine o jogador\s+(\w+)", s)
        if m_elim:
            cor_alvo = m_elim.group(1)
            return {"tipo": "destruir_jogador", "cor_alvo": cor_alvo}

        # Não foi possível mapear de forma confiável
        return None
    
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
