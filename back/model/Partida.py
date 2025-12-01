import random
from .Jogador import Jogador
from .IA import IA
from .Tabuleiro import Tabuleiro
from .Territorio import Territorio
from .Manager_de_Cartas import Manager_de_Cartas
from .Manager_de_Objetivos import Manager_de_Objetivos


class Partida:
    def __init__(self, qtd_humanos: int, qtd_ai: int, duracao_turno: int, tupla_jogadores: list[tuple[str, str, str]], shuffle_jogadores: bool = True): # tupla representa o jogador (nome, cor, tipo)
        assert 6 >= qtd_humanos + qtd_ai >= 3

        self.qtd_humanos = qtd_humanos
        self.qtd_ai = qtd_ai
        self.qtd_jogadores = qtd_humanos + qtd_ai
        self.duracao_turno = duracao_turno

        self.jogadores = self.criar_jogadores(tupla_jogadores)
        self.jogadores_eliminados = []
        self.jogador_atual_idx = 0

        self.tabuleiro = Tabuleiro(self.jogadores) # Cria o tabuleiro do jogo, que vai gerar todos os territórios, distribuindo eles para os jogadores
        self.fase_do_turno = "posicionamento"  # 'posicionamento', 'ataque', 'reposicionamento'
        
        if shuffle_jogadores:
            random.shuffle(self.jogadores) # Define a ordem dos turnos embaralhando a lista de jogadores
        self.tabuleiro.inicializar_exercitos_a_receber(self.jogadores)
        
        self.manager_de_cartas = Manager_de_Cartas()
        self.manager_de_objetivos = Manager_de_Objetivos(self.jogadores)
        self.valor_da_troca = 4
        self.conquistou_algum_territorio = False
        self.libera_ataque = False
        self.finalizado = False  # Indica se a partida foi finalizada
        self.vencedor = None     # Guarda a cor do vencedor

    def finalizar_partida(self, cor_vencedor):
        self.finalizado = True
        self.vencedor = cor_vencedor

    def proximo_jogador(self):
        """Passa a vez para o próximo jogador."""
        self.jogador_atual_idx = (self.jogador_atual_idx + 1) % self.qtd_jogadores
        if self.jogador_atual_idx == 0:
            self.libera_ataque = True

    def avancar_fase_ou_turno(self):
        if self.fase_do_turno == "posicionamento":
            if self.libera_ataque:
                self.fase_do_turno = "ataque"
            else:
                self.proximo_jogador()
                self.tabuleiro.calcula_exercitos_a_receber(self.jogadores[self.jogador_atual_idx])

        elif self.fase_do_turno == "ataque":
            self.fase_do_turno = "reposicionamento"
            
            if self.conquistou_algum_territorio :
                self.verifica_ganho_de_carta(self.jogadores[self.jogador_atual_idx])
                self.conquistou_algum_territorio = False
            
            self.calcular_limite_de_reposicionamento(self.jogadores[self.jogador_atual_idx])

        elif self.fase_do_turno == "reposicionamento":
            self.fase_do_turno = "posicionamento"
            self.proximo_jogador()
            self.tabuleiro.calcula_exercitos_a_receber(self.jogadores[self.jogador_atual_idx])
        
        # Garante que jogador_atual esteja sempre definido antes de retornar
        jogador_atual = self.jogadores[self.jogador_atual_idx]

        return jogador_atual, self.fase_do_turno
    
    def finalizar_turno_atual(self):
        self.fase_do_turno = "posicionamento"
        self.proximo_jogador()
        self.tabuleiro.calcula_exercitos_a_receber(self.jogadores[self.jogador_atual_idx])

        # Garante que jogador_atual esteja sempre definido antes de retornar
        jogador_atual = self.jogadores[self.jogador_atual_idx]
        return jogador_atual, self.fase_do_turno
    
    def fase_de_reposicionamento(self, jogador_id: str, nome_origem: str, nome_destino: str, qtd_exercitos: int):
        jogador: Jogador = next((j for j in self.jogadores if j.cor == jogador_id), None)
        if not jogador:
            raise Exception("Jogador não encontrado")
    
        origem = next((t for t in jogador.territorios if t.nome == nome_origem), None)
        if not origem:
            raise Exception("Território de origem não é seu")
    
        destino = next((t for t in jogador.territorios if t.nome == nome_destino), None)
        if not destino:
            raise Exception("Território de destino não é seu")
        
        if origem.limite_de_repasse < 1:
            raise Exception("Não é possível reposicionar mais nenhum exército a partir deste território.")
        
        if qtd_exercitos > origem.limite_de_repasse:
            raise Exception(f"Você só pode reposicionar até {origem.limite_de_repasse} exércitos a partir deste território.")
    
        jogador.mover_exercitos(origem, destino, qtd_exercitos)
    
        return {
            "territorio_origem": { "nome": origem.nome, "exercitos": origem.exercitos },
            "territorio_destino": { "nome": destino.nome, "exercitos": destino.exercitos }
        }

    def fase_de_posicionamento(self, jogador_id: str, territorio_nome: str, qtd_exercitos: int):
        jogador: Jogador = next((j for j in self.jogadores if j.cor == jogador_id), None)
        if not jogador:
            raise Exception("Jogador não encontrado")
    
        territorio = next((t for t in jogador.territorios if t.nome == territorio_nome), None)
        if not territorio:
            raise Exception("Território não pertence ao jogador")
    
        total_reserva = jogador.exercitos_reserva

        if qtd_exercitos > total_reserva:
            raise Exception("Exércitos insuficientes na reserva")
        
        jogador.adicionar_exercitos_territorio(territorio, qtd_exercitos)
        jogador.remover_exercitos_para_posicionamento(qtd_exercitos)
        return jogador.exercitos_reserva
    

    # cria os objetos jogador a partir da tupla contendo o nome do jogador e sua respectiva cor
    def criar_jogadores(self, tupla_jogadores):
        lista = []
        for i in tupla_jogadores:
            if len(i) == 3:
                tipo = i[2]
                if tipo == 'ai':
                    # não passar a string 'ai' como objetivo (IA espera dict ou None)
                    lista.append(IA(i[0], i[1]))
                else:
                    lista.append(Jogador(i[0], i[1], tipo))
            else:
                lista.append(Jogador(i[0], i[1]))
        return lista
    
    def resolver_combate(self, atacante: Jogador, defensor: Jogador, territorio_origem: Territorio, territorio_alvo: Territorio):
        """
        Resolve um combate entre atacante e defensor, atualizando exércitos e posse se necessário.
        """
        
        if atacante == defensor:
            print("Atacante e defensor são o mesmo jogador.")
            return False
        
        if atacante.exercitos_no_territorio(territorio_origem) <=1:
            print("Atacante não possui exércitos suficientes para atacar.")
            return False
        
        #Dados de ataque
        dados_ataque = 3 if atacante.exercitos_no_territorio(territorio_origem) >= 4 else atacante.exercitos_no_territorio(territorio_origem) - 1

        #Dados de defesa
        if defensor.exercitos_no_territorio(territorio_alvo) >= 3:
            dados_defesa = 3
        else:
            dados_defesa = defensor.exercitos_no_territorio(territorio_alvo)
        
        perdas_ataque, perdas_defesa, num_dados_ataque, num_dados_defesa = atacante.combate(dados_ataque, dados_defesa)

        atacante.remover_exercitos_territorio(territorio_origem, perdas_ataque)
        defensor.remover_exercitos_territorio(territorio_alvo, perdas_defesa)

        if territorio_alvo.exercitos == 0:
            self.transferir_territorio(atacante, defensor, territorio_alvo, territorio_origem)
            territorio_foi_conquistado = True
            self.conquistou_algum_territorio = True
        else:
            territorio_foi_conquistado = False 
        
        if territorio_foi_conquistado:
            self.verificar_eliminacao(atacante, defensor)

        return {
             "dados_ataque": dados_ataque,
             "dados_defesa": dados_defesa,
             "rolagens_ataque": num_dados_ataque,
             "rolagens_defesa": num_dados_defesa,
             "perdas_ataque": perdas_ataque,
             "perdas_defesa": perdas_defesa,
             "territorio_conquistado": territorio_foi_conquistado,
             "exercitos_restantes_no_inicio": territorio_origem.exercitos,
             "exercitos_restantes_no_defensor": territorio_alvo.exercitos,
             "exercitos_disponiveis_a_mover": (territorio_origem.exercitos - 1) if territorio_foi_conquistado else 0
        }

    def transferir_territorio(self, vencedor: Jogador, perdedor: Jogador, territorio: Territorio, origem: Territorio):
        """
        Transfere a posse do território para o vencedor e move exércitos obrigatórios.
        """
        print(f"Território {territorio.nome} conquistado por {vencedor.cor} de {perdedor.cor}")
        perdedor.remover_territorio(territorio)
        # Move 1 exercito automaticamente para o territorio conquistado
        # Eventualmente o jogador deve poder escolher a quantidade (de 1 a 3, sendo que o territorio de origem deve continuar com pelo menos 1 exercito)
        exercitos_para_mover = 1
        vencedor.receber_territorio_conquistado(origem, territorio, exercitos_para_mover) #adiciona o território na lista do jogador e atualiza a cor 

    # Verifica se o jogador foi eliminado (caso sua lista de territorios tenha tamanho zero) e trata a eliminação caso necessário
    def verificar_eliminacao(self, atacante: Jogador, defensor: Jogador):
        if len(defensor.territorios) == 0:
            for i in range(self.qtd_jogadores):
                if self.jogadores[i] == defensor:
                    defensor_index = i
                elif self.jogadores[i] == atacante:
                    atacante_index = i
            
            if defensor_index < atacante_index:
                self.jogador_atual_idx -= 1
            
            self.qtd_jogadores -= 1
            self.jogadores.remove(defensor)
            defensor.eliminado_por = atacante.cor
            self.jogadores_eliminados.append(defensor)

            # Transfere as cartas do jogador eliminado para o atacante até que o limite de 5 cartas seja atingido
            for i in defensor.cartas:
                if len(atacante.cartas) < 5:
                    atacante.adicionar_carta(i)
                else:
                    self.manager_de_cartas.cartas_trocadas([i])

            defensor.cartas = []
               
            print(f"\nJogador {defensor.cor} eliminado\n")
            return True
        return False
    
    def get_territorio_por_nome(self, nome_territorio: str):
        for territorio in self.tabuleiro.territorios:
            if territorio.nome == nome_territorio:
                return territorio
        return None
    
    def get_jogador_por_cor(self, cor_jogador: str):
        for jogador in self.jogadores:
            if jogador.cor == cor_jogador:
                return jogador
        return None
    
    def get_jogadores_eliminados(self):
        return self.jogadores_eliminados
    
    def get_jogadores_vivos(self):
        return self.jogadores
    
    def get_tabuleiro(self):
        return self.tabuleiro

    # Função para verificar ao final da fase de ataque se aquele jogador deve receber uma carta (em caso positivo, atribui a carta)
    def verifica_ganho_de_carta(self, jogador: Jogador):
        if self.conquistou_algum_territorio and len(jogador.cartas) < 5:
            jogador.adicionar_carta(self.manager_de_cartas.atribuir_carta())

    def realizar_troca(self, jogador: Jogador, cartas):
        if self.manager_de_cartas.validar_possivel_troca(cartas):
            jogador.trocar_cartas(cartas, self.valor_da_troca)
            self.manager_de_cartas.cartas_trocadas(cartas)
            self.incrementar_troca()
    
    def incrementar_troca(self):
        if self.valor_da_troca < 12:
            self.valor_da_troca += 2
        elif self.valor_da_troca < 15:
            self.valor_da_troca += 3
        else:
            self.valor_da_troca += 5

    def executar_turnos_ia_consecutivos(self, max_ias: int = 10, max_ataques: int = 50):
        """
        Executa turnos completos para jogadores IA enquanto o jogador atual for IA.
        Retorna uma lista com os resultados de cada IA executada.
        """
        partida = self
        ia_aggregate = []

        while getattr(partida.jogadores[partida.jogador_atual_idx], 'tipo', None) == 'ai':
            jogador_ia = partida.jogadores[partida.jogador_atual_idx]
            ia_result = {"jogador_id": jogador_ia.cor, "nome": jogador_ia.nome}

            # POSICIONAMENTO
            try:
                partida.tabuleiro.calcula_exercitos_a_receber(jogador_ia)
                if getattr(jogador_ia, 'exercitos_reserva', 0) > 0 and hasattr(jogador_ia, 'distribuir_exercitos'):
                    distribuicao = jogador_ia.distribuir_exercitos(partida.tabuleiro, jogador_ia.exercitos_reserva)
                    try:
                        jogador_ia.remover_exercitos_para_posicionamento(jogador_ia.exercitos_reserva)
                    except Exception:
                        pass
                else:
                    distribuicao = {}
                ia_result['posicionamento'] = distribuicao
            except Exception as e:
                ia_result['posicionamento_error'] = str(e)

            # avançar para fase de ataque
            try:
                partida.avancar_fase_ou_turno()
            except Exception:
                pass

            # ATAQUE
            try:
                ataques = 0
                if hasattr(jogador_ia, 'executar_ataques'):
                    ataques = jogador_ia.executar_ataques(partida, rng=None, agressividade=0.0, max_ataques=max_ataques)
                ia_result['ataques_efetuados'] = ataques
            except Exception as e:
                ia_result['ataques_error'] = str(e)

            # avançar para fase de reposicionamento
            try:
                partida.avancar_fase_ou_turno()
            except Exception:
                pass

            # REPOSICIONAMENTO
            try:
                repos = []
                if hasattr(jogador_ia, 'executar_reposicionamento'):
                    repos = jogador_ia.executar_reposicionamento(partida, max_movimentos=10)
                ia_result['reposicionamento'] = repos
            except Exception as e:
                ia_result['reposicionamento_error'] = str(e)

            # finalizar reposicionamento e avançar para o próximo jogador (posicionamento do próximo)
            try:
                partida.avancar_fase_ou_turno()
            except Exception:
                pass

            ia_aggregate.append(ia_result)

            # proteção para evitar loop infinito (caso algo dê errado)
            if len(ia_aggregate) > max_ias:
                break

        return ia_aggregate
    
    # Calcula o limite máximo de exercitos que podem ser repassados por cada territorio
    def calcular_limite_de_reposicionamento(self, jogador: Jogador):
        for i in jogador.territorios:
            i.limite_de_repasse = i.exercitos - 1
