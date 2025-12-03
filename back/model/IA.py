import random
import re
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

        # normalize objetivo: the game assigns objective as a string (several formats).
        # Convert known objective strings into a structured dict so the scoring logic
        # can work uniformly. Examples handled below are the project's objective list.
        def parse_objetivo(obj):
            if isinstance(obj, dict):
                return obj
            if not isinstance(obj, str):
                return None
            s = obj.lower()
            # Conquistar 24 territórios à sua escolha
            if '24 territ' in s:
                return {'tipo': 'conquistar_territorios', 'target': 24}
            # Conquistar 18 territórios e ocupar cada um deles com pelo menos 2 exércitos
            if '18 territ' in s and '2 ex' in s:
                return {'tipo': 'conquistar_territorios_exercitos', 'target': 18, 'min_exercitos': 2}
            # Regiões explícitas (ex.: "Região 2 e a Região 5")
            regs = re.findall(r'regi[ãa]\s*\s*(\d+)', s)
            if regs:
                regioes = [int(r) for r in regs]
                # detectar se a string permite escolher mais uma região
                if 'mais uma' in s or 'à sua escolha' in s:
                    return {'tipo': 'conquistar_continentes', 'regioes': regioes, 'allow_extra': True}
                return {'tipo': 'conquistar_continentes', 'regioes': regioes}
            # fallback: if contains "conquistar" treat as generic conquistar_territorios
            if 'conquistar' in s:
                return {'tipo': 'conquistar_territorios'}
            return None

        objetivo_dict = parse_objetivo(self.objetivo)

        # Se o objetivo permite escolher mais uma região, decidir qual é a melhor
        # candidata automaticamente: heurística simples = minimizar custo (nº de territórios
        # inimigos na região) e favorecer regiões com bônus maior.
        if objetivo_dict and objetivo_dict.get('tipo') == 'conquistar_continentes' and objetivo_dict.get('allow_extra'):
            regioes_existentes = set(objetivo_dict.get('regioes', []))
            todas_regioes = sorted({t.regiao for t in tabuleiro.territorios if isinstance(t.regiao, int)})
            candidato = None
            melhor_score = float('-inf')
            # map de bonus por região (se disponível em tabuleiro.regioes_com_bonus)
            bonus_map = {item[0]: (item[1] if len(item) > 1 else 0) for item in getattr(tabuleiro, 'regioes_com_bonus', [])}
            for r in todas_regioes:
                if r in regioes_existentes:
                    continue
                custo = sum(1 for t in tabuleiro.territorios if t.regiao == r and t.cor != self.cor)
                bonus = bonus_map.get(r, 0)
                # heurística: prefere regiões com menor custo e maior bônus
                score_r = -custo + bonus * 0.3
                if score_r > melhor_score:
                    melhor_score = score_r
                    candidato = r
            if candidato is not None:
                objetivo_dict.setdefault('regioes', []).append(candidato)
                # desativar allow_extra para não repetir seleção
                objetivo_dict['allow_extra'] = False

        # Para objetivos numéricos, calcular quantos territórios faltam
        target_remaining = None
        if objetivo_dict and objetivo_dict.get('tipo') in ('conquistar_territorios', 'conquistar_territorios_exercitos') and objetivo_dict.get('target'):
            owned = len(self.territorios)
            target_remaining = max(0, objetivo_dict.get('target') - owned)

        for territorio in tabuleiro.territorios:
            score = 0
            # 1. Objetivo: conquistar X territórios
            if objetivo_dict and objetivo_dict.get('tipo') == 'conquistar_territorios':
                if territorio.cor != self.cor:
                    # base
                    score += 2
                    # se faltam poucos territórios para a meta, aumentar agressividade
                    if target_remaining is not None and target_remaining <= 3:
                        score += (4 - target_remaining) * 1.5
            # 2. Objetivo: conquistar X territórios com pelo menos Y exércitos
            if objetivo_dict and objetivo_dict.get('tipo') == 'conquistar_territorios_exercitos':
                if territorio in self.territorios and territorio.exercitos < objetivo_dict.get('min_exercitos', 2):
                    score += 3  # Prioriza reforço
                elif territorio.cor != self.cor:
                    score += 1
                    # se faltam poucos territórios para a meta, dar peso extra a alvos capturáveis
                    if target_remaining is not None and target_remaining <= 3:
                        score += 2
            # 3. Objetivo: destruir jogador de cor específica
            if objetivo_dict and objetivo_dict.get('tipo') == 'destruir_jogador':
                cor_alvo = objetivo_dict.get('cor_alvo')
                if territorio.cor == cor_alvo:
                    score += 4  # Prioriza atacar territórios do alvo
            # 4. Objetivo: conquistar continentes / regiões específicas
            if objetivo_dict and objetivo_dict.get('tipo') == 'conquistar_continentes':
                # suportar ambas as chaves 'continentes' (legado) e 'regioes' (nova)
                regioes_alvo = objetivo_dict.get('continentes') or objetivo_dict.get('regioes') or []
                if territorio.regiao in regioes_alvo:
                    # território contribui para completar uma região alvo
                    score += 3
                else:
                    # se o objetivo permite escolher mais uma região, damos um bônus menor
                    if objetivo_dict.get('allow_extra'):
                        if territorio.cor != self.cor:
                            score += 1
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
                advantage = (origem.exercitos - alvo.exercitos) / alvo.exercitos
                fronteira_inimiga = len([t for t in origem.fronteiras if t.cor != self.cor])
                # combine fatores com pesos simples
                score = rank_score * 1.5 + advantage * 1.5 + fronteira_inimiga * 0.5

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
        eventos = []
        # limitar número de ataques prático por turno com base na agressividade
        efetivo_max = min(max_ataques, 3 + int(agressividade * 3))
        while ataques < efetivo_max:
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

            # registra evento de tentativa de ataque
            eventos.append({
                "tipo": "ataque_inicio",
                "origem": origem.nome,
                "alvo": alvo.nome,
                "exercitos_origem": origem.exercitos,
                "exercitos_alvo": alvo.exercitos,
            })

            # realiza o combate usando a rotina que retorna detalhes
            try:
                resultado = partida.resolver_combate_api(self, defensor, origem, alvo)
            except Exception:
                # se a versão da partida não expor resolver_combate_api, cai para a versão antiga e registra sem detalhes
                partida.resolver_combate(self, defensor, origem, alvo)
                resultado = {"territorio_conquistado": False}

            eventos.append({
                "tipo": "ataque_resultado",
                "origem": origem.nome,
                "alvo": alvo.nome,
                "dados_ataque": resultado.get("dados_ataque") if isinstance(resultado, dict) else None,
                "dados_defesa": resultado.get("dados_defesa") if isinstance(resultado, dict) else None,
                "territorio_conquistado": resultado.get("territorio_conquistado") if isinstance(resultado, dict) else None,
                "exercitos_restantes_no_inicio": resultado.get("exercitos_restantes_no_inicio") if isinstance(resultado, dict) else None,
                "exercitos_restantes_no_defensor": resultado.get("exercitos_restantes_no_defensor") if isinstance(resultado, dict) else None,
            })

            ataques += 1

        return ataques, eventos

    def executar_ataques_generator(self, partida, rng: random.Random | None = None, agressividade: float = 0.0, max_ataques: int = 10):
        """Gerador que produz eventos de ataque em tempo real.

        Iterar sobre ele retornará dicionários representando eventos ('ataque_inicio' e 'ataque_resultado').
        Mantém a mesma lógica de escolha de ataques, mas ao invés de coletar uma lista, emite cada evento com yield.
        """
        if rng is None:
            rng = random

        ataques = 0
        efetivo_max = min(max_ataques, 3 + int(agressividade * 3))
        while ataques < efetivo_max:
            escolha = self.escolher_ataque(partida.tabuleiro, rng=rng, agressividade=agressividade)
            if not escolha:
                break
            origem, alvo = escolha
            defensor = None
            for j in partida.jogadores:
                if j.cor == alvo.cor:
                    defensor = j
                    break
            if defensor is None:
                break

            # evento de inicio
            yield {
                "tipo": "ataque_inicio",
                "fase": "ataque",
                "origem": origem.nome,
                "alvo": alvo.nome,
                "exercitos_origem": origem.exercitos,
                "exercitos_alvo": alvo.exercitos,
            }

            # realiza combate
            try:
                resultado = partida.resolver_combate_api(self, defensor, origem, alvo)
            except Exception:
                partida.resolver_combate(self, defensor, origem, alvo)
                resultado = {"territorio_conquistado": False}

            yield {
                "tipo": "ataque_resultado",
                "fase": "ataque",
                "origem": origem.nome,
                "alvo": alvo.nome,
                "dados_ataque": resultado.get("dados_ataque") if isinstance(resultado, dict) else None,
                "dados_defesa": resultado.get("dados_defesa") if isinstance(resultado, dict) else None,
                "territorio_conquistado": resultado.get("territorio_conquistado") if isinstance(resultado, dict) else None,
                "exercitos_restantes_no_inicio": resultado.get("exercitos_restantes_no_inicio") if isinstance(resultado, dict) else None,
                "exercitos_restantes_no_defensor": resultado.get("exercitos_restantes_no_defensor") if isinstance(resultado, dict) else None,
            }

            ataques += 1

    def distribuir_exercitos(self, partida, exercitos_disponiveis):
        """
        Sugere uma distribuição dos exércitos disponíveis entre os territórios do jogador.
        Considera o tipo de objetivo para reforço mais inteligente.
        """
        import random

        # RNG local para testabilidade (poderemos expor seed no futuro)
        rng = random

        distribuicao = {t.nome: 0 for t in self.territorios}
        prioridades = self.avaliar_territorios(partida.tabuleiro)
        vulneraveis = sorted(self.territorios, key=lambda t: t.exercitos)

        if len(self.cartas) > 2:
            guia_cartas = [[], [], [], []]
            for c in range(len(self.cartas)):
                if self.cartas[c][0] == "Círculo":
                    guia_cartas[0].append(c)
            
                elif self.cartas[c][0] == "Quadrado":
                    guia_cartas[1].append(c)

                elif self.cartas[c][0] == "Triângulo":
                    guia_cartas[2].append(c)

                else:
                    guia_cartas[3].append(c)

            if len(guia_cartas[0]) >= 3:
                troca = []
                for i in range(3):
                    troca.append(self.cartas[guia_cartas[0][i]])
                valor = partida.valor_da_troca
                if partida.realizar_troca(self, troca):
                    exercitos_disponiveis += valor

            elif len(guia_cartas[1]) >= 3:
                troca = []
                for i in range(3):
                    troca.append(self.cartas[guia_cartas[1][i]])
                valor = partida.valor_da_troca
                if partida.realizar_troca(self, troca):
                    exercitos_disponiveis += valor

            elif len(guia_cartas[2]) >= 3:
                troca = []
                for i in range(3):
                    troca.append(self.cartas[guia_cartas[2][i]])
                valor = partida.valor_da_troca
                if partida.realizar_troca(self, troca):
                    exercitos_disponiveis += valor

            elif len(guia_cartas[0]) >= 1 and len(guia_cartas[1]) >= 1 and len(guia_cartas[2]) >= 1:
                troca = []
                troca.append(self.cartas[guia_cartas[0][0]])
                troca.append(self.cartas[guia_cartas[1][0]])
                troca.append(self.cartas[guia_cartas[2][0]])
                valor = partida.valor_da_troca
                if partida.realizar_troca(self, troca):
                    exercitos_disponiveis += valor

            elif len(guia_cartas[3]) > 0:
                troca = []
                count = 0

                for i in guia_cartas[3]:
                    if count == 3:
                        break
                    troca.append(self.cartas[i])
                    count += 1
                
                for i in guia_cartas[0]:
                    if count == 3:
                        break
                    troca.append(self.cartas[i])
                    count += 1

                for i in guia_cartas[1]:
                    if count == 3:
                        break
                    troca.append(self.cartas[i])
                    count += 1


                for i in guia_cartas[2]:
                    if count == 3:
                        break
                    troca.append(self.cartas[i])
                    count += 1

                if len(troca) == 3:
                    valor = partida.valor_da_troca
                    if partida.realizar_troca(self, troca):
                        exercitos_disponiveis += valor
        
                
        # preserva ordem ao combinar prioridades e vulneráveis
        def _unique_preserve_order(seq):
            seen = set()
            out = []
            for x in seq:
                if x not in seen:
                    seen.add(x)
                    out.append(x)
            return out

        # combinar algumas top prioridades com vulneráveis (pegar mais itens que antes)
        combined = prioridades[:3] + vulneraveis[:3]
        alvos = [t for t in _unique_preserve_order(combined) if t in self.territorios]

        restante = exercitos_disponiveis

        # garantir 1 exército em cada alvo prioritário, se possível
        for territorio in alvos:
            if restante <= 0:
                break
            distribuicao[territorio.nome] += 1
            self.adicionar_exercitos_territorio(territorio, 1)
            restante -= 1

        # reforçar os mesmos alvos até um limite por alvo (evita espalhar para todos os territórios)
        if restante > 0 and alvos:
            idx = 0
            n = len(alvos)
            max_por_alvo = 3
            ciclos = 0
            while restante > 0 and ciclos < n * max_por_alvo + 5:
                t = alvos[idx % n]
                if distribuicao[t.nome] < max_por_alvo:
                    distribuicao[t.nome] += 1
                    self.adicionar_exercitos_territorio(t, 1)
                    restante -= 1
                idx += 1
                ciclos += 1

        # não distribuir para territórios não prioritários por padrão
        return distribuicao

    def executar_reposicionamento(self, partida, max_movimentos: int = 10):
        """
        Heurística simples de reposicionamento:
        - Identifica territórios próprios vulneráveis (poucos exércitos e com fronteira inimiga)
        - Tenta mover exércitos de territórios com excesso para fortalecer os vulneráveis
        - Move no máximo `max_movimentos` transferências

        Retorna uma lista de movimentos realizados no formato:
          [ {"origem": origem.nome, "destino": destino.nome, "qtd": n}, ... ]
        """
        movimentos = []

        # destinos: territórios próprios com <=2 exércitos, que têm inimigos na fronteira
        # e que também possuem pelo menos um território próprio adjacente (para poder receber movimentos)
        destinos = [
            t for t in self.territorios
            if t.exercitos <= 2
            and any if(t.cor == self.cor)
        ]
       
        nova= []
        for destino in destinos:
            for f in destino.fronteiras:
                if f.cor == destino.cor:
                    nova.append(destino)
                    # o continue é inútil aqui, deveria ser um break ??
                    continue
                    
        destinos = nova

        for destino in destinos:
            for f in destino.fronteiras:
                cont = 0
                if f.cor == self.cor:
                    cont += 1
            if cont == len(destino.fronteiras):
                # se todas as fronteiras são nossas, não é um destino válido
                destinos.remove(destino)

        destinos = list(set(destinos))
        for d in destinos:
            print(d.nome)


        # fontes: territórios com mais de 1 exército (podem ceder)
        fontes = sorted([t for t in self.territorios if t.exercitos > 1], key=lambda x: x.exercitos, reverse=True)

        movimentos_feitos = 0
        for destino in destinos:
            if movimentos_feitos >= max_movimentos:
                break
            # seleciona apenas fontes que fazem fronteira com o destino (e são nossas)
            candidate_fontes = [f for f in fontes if f is not destino and f in destino.fronteiras and f.cor == self.cor and f.limite_de_repasse > 0]
           
            if not candidate_fontes:
                # nenhuma fonte adjacente disponível para esse destino
               
                continue

            # procura uma fonte adequada entre as candidate_fontes
            fonte_escolhida = None
            for fonte in candidate_fontes:
                # preferir fontes com mais de 3 exércitos ou fontes que não tenham inimigos na fronteira
                if not any(ff.cor != self.cor for ff in fonte.fronteiras):
                    fonte_escolhida = fonte
                    break

            if not fonte_escolhida:
                for fonte in candidate_fontes:
                # preferir fontes com mais de 3 exércitos ou fontes que não tenham inimigos na fronteira
                    if fonte.exercitos > 3:
                        fonte_escolhida = fonte
                        break

            if not fonte_escolhida:
                # escolher a fonte adjacente com mais exércitos
                fonte_escolhida = max(candidate_fontes, key=lambda x: x.exercitos)
                
            # decide quantidade a mover: deixa pelo menos 1 no origem e não mais que 3 por movimento
            qtd_possivel = max(0, fonte_escolhida.limite_de_repasse)
            # mover apenas o necessário para trazer o destino até um nível mínimo (ex.: 3 exércitos)
            nivel_desejado = 3
            necessario = max(0, nivel_desejado - destino.exercitos)
            if necessario <= 0:
                continue
            qtd_mover = min(3, qtd_possivel, necessario)
            if qtd_mover <= 0:
                continue

            # executar movimento
            try:
                # mover_exercitos definido em Jogador; agora retorna a quantidade efetivamente movida
                print(f"fonte_escolhida: {fonte_escolhida.nome} -> destino: {destino.nome} qtd: {qtd_mover}")
                moved = self.mover_exercitos(fonte_escolhida, destino, qtd_mover)
                if moved and moved > 0:
                    movimentos.append({"origem": fonte_escolhida.nome, "destino": destino.nome, "qtd": moved})
                movimentos_feitos += 1
                # atualizar listas locais
                # fonte_exercitos atualizados via mover_exercitos
            except Exception:
                # se falhar (por qualquer razão), pular
                continue
        return movimentos





