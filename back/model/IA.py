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

    def distribuir_exercitos(self, tabuleiro, exercitos_disponiveis):
        """
        Sugere uma distribuição dos exércitos disponíveis entre os territórios do jogador.
        Considera o tipo de objetivo para reforço mais inteligente.
        """
        distribuicao = dict.fromkeys([t.nome for t in self.territorios], 0)
        prioridades = self.avaliar_territorios(tabuleiro)
        vulneraveis = sorted(self.territorios, key=lambda t: t.exercitos)
        alvos = [t for t in set(prioridades[:2] + vulneraveis[:2]) if t in self.territorios]
        restante = exercitos_disponiveis
        for territorio in alvos:
            if restante <= 0:
                break
            distribuicao[territorio.nome] += 1
            restante -= 1
        import random
        outros = [t for t in self.territorios if t not in alvos]
        while restante > 0 and outros:
            t = random.choice(outros)
            distribuicao[t.nome] += 1
            restante -= 1
        return distribuicao
