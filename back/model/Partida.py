import random
from .Jogador import Jogador
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
        self.jogador_atual_idx = 0
        self.fase_do_turno = "posicionamento"  # 'posicionamento', 'ataque', 'reposicionamento'
        random.shuffle(self.jogadores) # define a ordem dos turnos embaralhando a lista de jogadores
        self.manager_de_cartas = Manager_de_Cartas()
        self.manager_de_objetivos = Manager_de_Objetivos(self.jogadores)
        self.valor_da_troca = 4

    def proximo_jogador(self):
        """Passa a vez para o próximo jogador."""
        self.jogador_atual_idx = (self.jogador_atual_idx + 1) % self.qtd_jogadores

    # def gerenciar_turno(self, jogador: Jogador):
    #     """Orquestra as três fases do turno de um jogador."""
    #     # Fase de Posicionamento
    #     self.fase_do_turno = "posicionamento"
    #     print(f"Fase de {self.fase_do_turno}...")
    #     self.fase_de_posicionamento(jogador)

    #     # Fase de Ataque
    #     self.fase_do_turno = "ataque"
    #     print(f"Fase de {self.fase_do_turno}...")
    #     self.fase_de_ataque(jogador)

        # Fase de reposicionamento
        self.fase_do_turno = "reposicionamento"
        print(f"Fase de {self.fase_do_turno}...")
        self.fase_de_reposicionamento(jogador)
        
    #     print(f"Fim do turno de {jogador.nome}")

    def avancar_fase_ou_turno(self):
        if self.fase_do_turno == "posicionamento":
            self.fase_do_turno = "ataque"

        elif self.fase_do_turno == "ataque":
            self.fase_do_turno = "reposicionamento"

        elif self.fase_do_turno == "reposicionamento":
            self.fase_do_turno = "posicionamento"
            self.proximo_jogador()
        # garante que jogador_atual esteja sempre definido antes de retornar
        jogador_atual = self.jogadores[self.jogador_atual_idx]

        return jogador_atual, self.fase_do_turno
    
    def fase_de_ataque(self, jogador: Jogador):
        """Lógica para o jogador realizar ataques."""
        print("O jogador decide se e como irá atacar.")
        pass # 'pass' significa que o método não faz nada

    def fase_de_reposicionamento(self, jogador: Jogador):
        """Lógica para o jogador mover exércitos."""
        print("O jogador decide se e como irá reposicionar seus exércitos.")
        pass
    
    def fase_de_reposicionamento_api(self, jogador_id, nome_origem, nome_destino, qtd_exercitos):
        jogador = next((j for j in self.jogadores if j.cor == jogador_id), None)
        if not jogador: raise Exception("Jogador não encontrado")
    
        origem = next((t for t in jogador.territorios if t.nome == nome_origem), None)
        if not origem: raise Exception("Território de origem não é seu")
    
        destino = next((t for t in jogador.territorios if t.nome == nome_destino), None)
        if not destino: raise Exception("Território de destino não é seu")
    
        jogador.mover_exercitos(origem, destino, qtd_exercitos)
    
        return {
            "territorio_origem": { "nome": origem.nome, "exercitos": origem.exercitos },
            "territorio_destino": { "nome": destino.nome, "exercitos": destino.exercitos }
        }

    def fase_de_posicionamento(self, jogador: Jogador,):
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

    def fase_de_posicionamento_api(self, jogador_id, territorio_nome, qtd_exercitos):
        jogador = next((j for j in self.jogadores if j.cor == jogador_id), None)
        if not jogador:
            raise Exception("Jogador não encontrado")
    
        territorio = next((t for t in jogador.territorios if t.nome == territorio_nome), None)
        if not territorio:
            raise Exception("Território não pertence ao jogador")
    
        total_reserva = sum(jogador.exercitos_reserva)

        if qtd_exercitos > total_reserva:
            raise Exception("Exércitos insuficientes na reserva")
        
        jogador.adicionar_exercitos_territorio(territorio, qtd_exercitos)
        
        jogador.remover_exercitos_para_posicionamento([0,0,0,0,0,0,qtd_exercitos]) # isso precisa ser consertado
        
        return sum(jogador.exercitos_reserva)
    

    # cria os objetos jogador a partir da tupla contendo o nome do jogador e sua respectiva cor
    def criar_jogadores(self, tupla_jogadores):
        lista = []
        for i in tupla_jogadores:
            if len(i) == 3:
                lista.append(Jogador(i[0], i[1], i[2]))
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
        
        perdas_ataque, perdas_defesa = atacante.combate(dados_ataque, dados_defesa)
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
        
        # move 1 exercito automaticamente para o territorio conquistado
        # eventualmente o jogador deve poder escolher a quantidade (de 1 a 3, sendo que o territorio de origem deve continuar com pelo menos 1 exercito)
        exercitos_para_mover = 1
        vencedor.mover_exercitos(origem, territorio, exercitos_para_mover)

    # verifica se o jogador foi eliminado (caso sua lista de territorios tenha tamanho zero) e trata a eliminação caso necessário
    def verificar_eliminacao(self, atacante: Jogador, defensor: Jogador):
        if len(defensor.territorios) == 0:
            self.jogadores.remove(defensor)
            defensor.eliminado_por = atacante.cor
            self.jogadores_eliminados.append(defensor)

            # transfere as cartas do jogador eliminado para o atacante até que o limite de 5 cartas seja atingido
            for i in defensor.cartas:
                if len(atacante.cartas) < 5:
                    atacante.adicionar_carta(i)
                else:
                    self.manager_de_cartas.cartas_trocadas(i)

            defensor.cartas = []
                
            print(f"\nJogador {defensor.cor} eliminado\n")
            return True
        return False
    
    def transferir_territorio(self, vencedor: Jogador, perdedor: Jogador, territorio: Territorio, origem: Territorio):
        """
        Transfere a posse do território para o vencedor e move exércitos obrigatórios.
        """
        perdedor.remover_territorio(territorio)
        vencedor.adicionar_territorio(territorio) #adiciona o território na lista do jogador e atualiza a cor 
        
        # move 1 exercito automaticamente para o territorio conquistado
        # eventualmente o jogador deve poder escolher a quantidade (de 1 a 3, sendo que o territorio de origem deve continuar com pelo menos 1 exercito)
        exercitos_para_mover = 1
        vencedor.mover_exercitos(origem, territorio, exercitos_para_mover)

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
