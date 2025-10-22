import random
from .Jogador import Jogador


class IA(Jogador):
    def __init__(self, nome: str, cor: str, objetivo=None):
        super().__init__(nome, cor, tipo="ai")
        if objetivo:
            self.objetivo = objetivo

    def avaliar_territorios(self, tabuleiro):
        """
        Avalia os territórios do tabuleiro e retorna uma lista ordenada por prioridade.
        Agora suporta múltiplos tipos de objetivo do War:
        - Conquistar X territórios
        - Conquistar X territórios com pelo menos Y exércitos
        - Destruir jogador de cor específica
        - Conquistar continentes
        """
        prioridades = []
        for territorio in tabuleiro.territorios:
            score = 0
            # 1. Objetivo: conquistar X territórios
            if self.objetivo and self.objetivo.get('tipo') == 'conquistar_territorios':
                if territorio.cor != self.cor:
                    score += 2  # Prioriza territórios não conquistados
            # 2. Objetivo: conquistar X territórios com pelo menos Y exércitos
            if self.objetivo and self.objetivo.get('tipo') == 'conquistar_territorios_exercitos':
                if territorio in self.territorios and territorio.exercitos < self.objetivo.get('min_exercitos', 2):
                    score += 3  # Prioriza reforço
                elif territorio.cor != self.cor:
                    score += 1
            # 3. Objetivo: destruir jogador de cor específica
            if self.objetivo and self.objetivo.get('tipo') == 'destruir_jogador':
                cor_alvo = self.objetivo.get('cor_alvo')
                if territorio.cor == cor_alvo:
                    score += 4  # Prioriza atacar territórios do alvo
            # 4. Objetivo: conquistar continentes
            if self.objetivo and self.objetivo.get('tipo') == 'conquistar_continentes':
                continentes_alvo = self.objetivo.get('continentes', [])
                if territorio.regiao in continentes_alvo:
                    score += 3
            # Critérios gerais
            if territorio in self.territorios:
                score += 1
                score -= max(0, 3 - territorio.exercitos)
                inimigos = [t for t in territorio.fronteiras if t.cor != self.cor]
                score += len(inimigos)
            # Bônus de região
            for item in tabuleiro.regioes_com_bonus:
                # item pode ser [regiao, bonus] ou [regiao, bonus, lista_territorios]
                if len(item) >= 2:
                    regiao = item[0]
                    bonus = item[1]
                    if territorio.regiao == regiao:
                        score += bonus * 0.5
            # Aleatoriedade
            import random
            score += random.uniform(-1, 1)
            prioridades.append((territorio, score))
        prioridades.sort(key=lambda x: x[1], reverse=True)
        return [t[0] for t in prioridades]

    def escolher_ataque(self, tabuleiro, rng: random.Random | None = None, agressividade: float = 0.0):
        """
        Decide um par (origem, alvo) para atacar ou retorna None se nenhum ataque for recomendado.

        - tabuleiro: objeto Tabuleiro com territórios e regiões
        - rng: instância de random.Random para testes determinísticos (opcional)
        - agressividade: valor que diminui o limiar para ataques (valores maiores -> mais agressivo)

        Retorna: (origem_territorio, alvo_territorio) ou None
        """
        if rng is None:
            rng = random

        # mapa de prioridade a partir de avaliar_territorios (rank maior = mais prioridade)
        prioridades = self.avaliar_territorios(tabuleiro)
        if not prioridades:
            return None
        rank_map = {t: (len(prioridades) - i) for i, t in enumerate(prioridades)}

        melhor = None
        melhor_score = float('-inf')

        # para cada território que possuímos com capacidade de atacar
        for origem in list(self.territorios):
            if origem.exercitos < 2:
                continue
            # inimigos nas fronteiras
            inimigos = [t for t in origem.fronteiras if t.cor != self.cor]
            if not inimigos:
                continue

            for alvo in inimigos:
                # heurística simples: prioriza alvos com alta prioridade (rank_map), diferença de exércitos e quantidade de inimigos adjacentes
                rank_score = rank_map.get(alvo, 0)
                advantage = origem.exercitos - alvo.exercitos
                fronteira_inimiga = len([t for t in origem.fronteiras if t.cor != self.cor])
                # combine fatores com pesos simples
                score = rank_score * 1.5 + advantage * 1.0 + fronteira_inimiga * 0.5

                # adicionar pequeno ruído para evitar empates sempre iguais
                score += rng.uniform(-0.5, 0.5)

                # se alvo estiver claramente fraco, favorecer
                if alvo.exercitos <= 1:
                    score += 1.5

                # aplicar agressividade (se maior, diminui limiar para ataques arriscados)
                score += agressividade

                if score > melhor_score:
                    melhor_score = score
                    melhor = (origem, alvo)

        # limiar mínimo para realizar ataque (evita ataques muito arriscados)
        if melhor is None:
            return None
        if melhor_score < 1.0 - agressividade:
            return None

        return melhor

    def executar_ataques(self, partida, rng: random.Random | None = None, agressividade: float = 0.0, max_ataques: int = 10):
        """
        Executa uma sequência de ataques enquanto a IA encontrar ataques recomendados.
        - partida: objeto Partida (usa resolver_combate para aplicar o combate)
        - rng: random.Random opcional para determinismo
        - agressividade: favorece ataques arriscados quando maior
        - max_ataques: limite para evitar loops infinitos

        Retorna o número de ataques efetuados.
        """
        if rng is None:
            rng = random

        ataques = 0
        while ataques < max_ataques:
            escolha = self.escolher_ataque(partida.tabuleiro, rng=rng, agressividade=agressividade)
            if not escolha:
                break
            origem, alvo = escolha
            # encontra o jogador defensor pela cor do território alvo
            defensor = None
            for j in partida.jogadores:
                if j.cor == alvo.cor:
                    defensor = j
                    break
            if defensor is None:
                break

            # realiza o combate usando a lógica já implementada em Partida
            print(f"Atacante: {self.nome} ({self.cor}) vs Defensor: {defensor.nome} ({defensor.cor})")
            print(f"Origem: {origem} -  Alvo:{alvo}")
            
            partida.resolver_combate(self, defensor, origem, alvo)
            ataques += 1

        return ataques

    def distribuir_exercitos(self, tabuleiro, exercitos_disponiveis):
        """
        Sugere uma distribuição dos exércitos disponíveis entre os territórios do jogador.
        Considera o tipo de objetivo para reforço mais inteligente.
        """
        import random

        # RNG local para testabilidade (poderemos expor seed no futuro)
        rng = random

        distribuicao = {t.nome: 0 for t in self.territorios}
        prioridades = self.avaliar_territorios(tabuleiro)
        vulneraveis = sorted(self.territorios, key=lambda t: t.exercitos)

        # preserva ordem ao combinar prioridades e vulneráveis
        def _unique_preserve_order(seq):
            seen = set()
            out = []
            for x in seq:
                if x not in seen:
                    seen.add(x)
                    out.append(x)
            return out

        combined = prioridades[:2] + vulneraveis[:2]
        alvos = [t for t in _unique_preserve_order(combined) if t in self.territorios]

        restante = exercitos_disponiveis
        for territorio in alvos:
            if restante <= 0:
                break
            distribuicao[territorio.nome] +=1 
            self.adicionar_exercitos_territorio(territorio, 1)
            restante -= 1

        # construir pool ordenado para round-robin: prioriza 'alvos' e depois os demais territórios
        outros = [t for t in self.territorios if t not in alvos]
        pool = alvos + outros

        # Round-robin: cicla pela pool atribuindo 1 exército por vez até acabar
        if pool:
            idx = 0
            n = len(pool)
            while restante > 0:
                t = pool[idx % n]
                distribuicao[t.nome] += 1
                self.adicionar_exercitos_territorio(t, 1)
                restante -= 1
                idx += 1


        return distribuicao




