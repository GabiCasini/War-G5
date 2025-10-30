import random
from .Jogador import Jogador
from .IA import IA
from .Tabuleiro import Tabuleiro
from .Territorio import Territorio
from .Manager_de_Cartas import Manager_de_Cartas
from .Manager_de_Objetivos import Manager_de_Objetivos

class Partida:
    def __init__(self, qtd_humanos: int, qtd_ai: int, duracao_turno: int, tupla_jogadores: list[tuple[str, str, str]]): # tupla representa o jogador (nome, cor, tipo)
        assert 6 >= qtd_humanos + qtd_ai >= 3
        self.qtd_humanos = qtd_humanos
        self.qtd_ai = qtd_ai
        self.qtd_jogadores = qtd_humanos + qtd_ai
        self.duracao_turno = duracao_turno
        self.jogadores = self.criar_jogadores(tupla_jogadores)
        self.jogadores_eliminados = []
        self.tabuleiro = Tabuleiro(self.jogadores) # cria o tabuleiro do jogo, que vai gerar todos os territórios, distribuindo eles para os jogadores
        self.tabuleiro.inicializar_exercitos_a_receber(self.jogadores)
        self.jogador_atual_idx = 0
        self.fase_do_turno = "posicionamento"  # 'posicionamento', 'ataque', 'reposicionamento'
        random.shuffle(self.jogadores) # define a ordem dos turnos embaralhando a lista de jogadores
        self.manager_de_cartas = Manager_de_Cartas()
        self.manager_de_objetivos = Manager_de_Objetivos(self.jogadores)
        self.valor_da_troca = 4

    def proximo_jogador(self):
        """Passa a vez para o próximo jogador."""
        self.jogador_atual_idx = (self.jogador_atual_idx + 1) % self.qtd_jogadores

    def avancar_fase_ou_turno(self):
        if self.fase_do_turno == "posicionamento":
            self.fase_do_turno = "ataque"

        elif self.fase_do_turno == "ataque":
            self.fase_do_turno = "reposicionamento"

        elif self.fase_do_turno == "reposicionamento":
            self.fase_do_turno = "posicionamento"
            self.tabuleiro.calcula_exercitos_a_receber(self.jogadores[self.jogador_atual_idx])
            self.proximo_jogador()
        # garante que jogador_atual esteja sempre definido antes de retornar
        jogador_atual = self.jogadores[self.jogador_atual_idx]

        return jogador_atual, self.fase_do_turno
    
    def fase_de_ataque(self, jogador: Jogador):
        """Lógica para o jogador realizar ataques."""
       
        # Se for IA, usar a rotina de ataque da IA
        if jogador.tipo == 'ai' and hasattr(jogador, 'executar_ataques'):
            try:
                import random
                rng = random.Random()
                # parâmetros básicos: agressividade baixa por padrão
                ataques = jogador.executar_ataques(self, rng=rng, agressividade=0.0, max_ataques=10)
                print(f'IA {jogador.nome} efetuou {ataques} ataques.')
            except Exception as e:
                print(f'Erro ao executar ataques da IA: {e}')
        else:
            print("O jogador decide se e como irá atacar.")
            pass

    def fase_de_reposicionamento(self, jogador: Jogador):
        """Lógica para o jogador mover exércitos."""
        print("O jogador decide se e como irá reposicionar seus exércitos.")
        pass
    
    def fase_de_reposicionamento_api(self, jogador_id: str, nome_origem: str, nome_destino: str, qtd_exercitos: int):
        jogador: Jogador = next((j for j in self.jogadores if j.cor == jogador_id), None)
        if not jogador:
            raise Exception("Jogador não encontrado")
    
        origem = next((t for t in jogador.territorios if t.nome == nome_origem), None)
        if not origem:
            raise Exception("Território de origem não é seu")
    
        destino = next((t for t in jogador.territorios if t.nome == nome_destino), None)
        if not destino:
            raise Exception("Território de destino não é seu")
        
        if origem.exercitos <= 1:
            raise Exception("Não é possível reposicionar de um território com apenas 1 exército.")
        
        max_reposicionar = origem.exercitos - 1
        if qtd_exercitos > max_reposicionar:
            raise Exception(f"Você só pode reposicionar até {max_reposicionar} exércitos.")
    
        jogador.reposicionar_exercitos(origem, destino, qtd_exercitos)
    
        return {
            "territorio_origem": { "nome": origem.nome, "exercitos": origem.exercitos },
            "territorio_destino": { "nome": destino.nome, "exercitos": destino.exercitos }
        }

    def fase_de_posicionamento(self, jogador: Jogador):
        """Lógica para o jogador posicionar seus novos exércitos."""
        self.tabuleiro.calcula_exercitos_a_receber(jogador=jogador)
        total_exercitos = jogador.exercitos_reserva
        print(f"Exércitos para posicionar: {total_exercitos}")
        # TODO: Substituir lógica aleatória por input do usuário ou lógica da IA
        if jogador.tipo == 'humano':
            print(f"Você tem {total_exercitos} exércitos para posicionar.")
            # Coloca tudo no primeiro território
            territorio_escolhido = jogador.territorios[0] # Necessita da api para saber qual territorio o jogador escolheu
            jogador.adicionar_exercitos_territorio(territorio_escolhido, total_exercitos)
            print(f"{jogador.nome} posicionou {total_exercitos} em {territorio_escolhido.nome}.")

    def fase_de_posicionamento_api(self, jogador_id: str, territorio_nome: str, qtd_exercitos: int):
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
        if atacante.exercitos_no_territorio(territorio_origem) >= 4:
            dados_ataque = 3
        
        else:
            dados_ataque = atacante.exercitos_no_territorio(territorio_origem) - 1

        
        #Dados de defesa
        if defensor.exercitos_no_territorio(territorio_alvo) >= 3:
            dados_defesa = 3

        else:
            dados_defesa = defensor.exercitos_no_territorio(territorio_alvo)
        
        # Compatibilidade: `Jogador.combate` pode retornar (perdas_ataque, perdas_defesa)
        # ou (perdas_ataque, perdas_defesa, dados_ataque, dados_defesa).
        try:
            resultado_combate = atacante.combate(dados_ataque, dados_defesa)
            # tenta desempacotar a forma longa
            if isinstance(resultado_combate, tuple) and len(resultado_combate) >= 2:
                perdas_ataque = resultado_combate[0]
                perdas_defesa = resultado_combate[1]
            else:
                # fallback conservador
                perdas_ataque, perdas_defesa = 0, 0
        except Exception as e:
            print(f"Erro ao executar combate: {e}")
            perdas_ataque, perdas_defesa = 0, 0

        atacante.remover_exercitos_territorio(territorio_origem, perdas_ataque)
        defensor.remover_exercitos_territorio(territorio_alvo, perdas_defesa)
        
        # Sugestao para ver o resultado do combate
        # print(f"Combate em {territorio_alvo.nome}: Atacante perdeu {perdas_ataque}, Defensor perdeu {perdas_defesa}.")

        if territorio_alvo.exercitos == 0:
            self.transferir_territorio(atacante, defensor, territorio_alvo, territorio_origem)
            return True  # território conquistado
        return False  # território não conquistado
    
    def resolver_combate_api(self, atacante: Jogador, defensor: Jogador, territorio_origem: Territorio, territorio_alvo: Territorio):
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
        if atacante.exercitos_no_territorio(territorio_origem) >= 4:
            dados_ataque = 3
        
        else:
            dados_ataque = atacante.exercitos_no_territorio(territorio_origem) - 1

        
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
        else:  # território não conquistado
            territorio_foi_conquistado = False 
        
        return {
             "dados_ataque": dados_ataque,
             "dados_defesa": dados_defesa,
             "territorio_conquistado": territorio_foi_conquistado,
             "exercitos_restantes_no_inicio": territorio_origem.exercitos,
             "exercitos_restantes_no_defensor": territorio_alvo.exercitos,
             "exercitos_disponiveis_a_mover": (territorio_origem.exercitos - 1) if territorio_foi_conquistado else 0
         }
    
    
    def transferir_territorio(self, vencedor: Jogador, perdedor: Jogador, territorio: Territorio, origem: Territorio):
        """
        Transfere a posse do território para o vencedor e move exércitos obrigatórios.
        """
        perdedor.remover_territorio(territorio)
        vencedor.adicionar_territorio(territorio) #adiciona o território na lista do jogador e atualiza a cor 
        
        # Decide quantos exércitos mover para o território conquistado.
        # Preferimos mover até 3, mas garantindo que a origem mantenha pelo menos 1 exercito.
        # Se a origem não tiver exércitos sobrando (<=1), forçamos que o território conquistado receba 1 exército
        # e, caso seja possível, diminuímos a origem para manter coerência de soma total.
        if origem.exercitos > 1:
            exercitos_para_mover = min(3, origem.exercitos - 1)
            origem.exercitos -= exercitos_para_mover
            territorio.exercitos += exercitos_para_mover
        else:
            if origem.exercitos >= 1:
                origem.exercitos -= 1
            territorio.exercitos += 1

    # verifica se o jogador foi eliminado (caso sua lista de territorios tenha tamanho zero)
    # falta implementar a passagem das cartas do jogador eliminado para quem o eliminou, além da verificação de cumprimento dos objetivos
    def verificar_eliminacao(self, jogador: Jogador):
        if jogador.numero_de_territorios() == 0:
            self.jogadores.remove(jogador)
            print(f"\nJogador {jogador.cor} eliminado\n")
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

    # Essa função deve ser utilizada ao final da fase ataque de cada jogador, passando um valor booleano que indica
    # se ele conquistou ou não algum território durante o ataque
    def verifica_ganho_de_carta(self, jogador: Jogador, conquistado: bool):
        if conquistado and len(jogador.cartas) < 5:
            jogador.adicionar_carta(self.manager_de_cartas.atribuir_carta())

    def realizar_troca(self, jogador: Jogador, cartas):
        if self.manager_de_cartas.validar_possivel_troca(cartas):
            jogador.trocar_cartas(cartas, self.valor_da_troca)
            self.manager_de_cartas.cartas_trocadas(cartas) # os territorios das cartas que foram trocados serão colocados na lista de disponíveis
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
