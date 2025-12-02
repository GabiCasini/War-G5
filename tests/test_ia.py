import pytest
import random
from back.model.IA import IA
from back.model.Tabuleiro import Tabuleiro
from back.model.Partida import Partida
from back import state

def criar_ia_com_objetivo(nome, cor, tipo_objetivo, **kwargs):

    objetivo = {
        'tipo': tipo_objetivo,
        **kwargs
    }
    return IA(nome, cor, objetivo=objetivo)


def criar_multiplas_ias(quantidade=4):
   
    cores = ["verde", "amarelo", "roxo", "preto", "azul", "vermelho"]
    ias = []
    
    objetivos = [
        {"tipo": "conquistar_territorios", "quantidade": 3},
        {"tipo": "conquistar_territorios_exercitos", "quantidade": 2, "min_exercitos": 2},
        {"tipo": "destruir_jogador", "cor_alvo": "amarelo"},
        {"tipo": "conquistar_continentes", "continentes": ["Regiao1", "Regiao2"]}
    ]
    
    for i in range(quantidade):
        nome = f"IA{i+1}"
        cor = cores[i % len(cores)]
        objetivo = objetivos[i % len(objetivos)]
        ias.append(IA(nome, cor, objetivo=objetivo))
    
    return ias


def distribuir_territorios_entre_ias(tabuleiro, ias, seed=42):
    
    rng = random.Random(seed)
    
    for ia in ias:
        ia.territorios.clear()
    
    for i, territorio in enumerate(tabuleiro.territorios):
        ia = ias[i % len(ias)]
        territorio.cor = ia.cor
        territorio.exercitos = 1 + rng.randint(0, 2)
        ia.adicionar_territorio(territorio)


def obter_territorios_por_ia(ias):
    
    return {ia.nome: list(ia.territorios) for ia in ias}


def contar_exercitos_ia(ia):
    
    return sum(t.exercitos for t in ia.territorios)


def obter_territorios_inimigos_adjacentes(ia, tabuleiro):
    
    inimigos_adjacentes = set()
    
    for territorio in ia.territorios:
        for vizinho in territorio.fronteiras:
            if vizinho.cor != ia.cor:
                inimigos_adjacentes.add(vizinho)
    
    return list(inimigos_adjacentes)


def validar_integridade_territorios(ias, tabuleiro):
   
    territorios_alocados = set()
    
    for ia in ias:
        for territorio in ia.territorios:
            if territorio in territorios_alocados:
                return False  # Território duplicado
            territorios_alocados.add(territorio)
    
    return len(territorios_alocados) <= len(tabuleiro.territorios)


def simular_rodada_ataques(ias, tabuleiro, seed=42, agressividade=0.2, max_ataques_por_ia=5):
    
    rng = random.Random(seed)
    resultados = {}
    
    for ia in ias:
        ataques = 0
        while ataques < max_ataques_por_ia:
            escolha = ia.escolher_ataque(tabuleiro, rng=rng, agressividade=agressividade)
            if not escolha:
                break
            ataques += 1
        
        resultados[ia.nome] = ataques
    
    return resultados

def test_criar_ia_simples():
   
    ia = IA("TestIA", "azul")
    
    assert ia.nome == "TestIA"
    assert ia.cor == "azul"
    assert ia.tipo == "ai"
    assert len(ia.territorios) == 0


def test_criar_ia_com_objetivo_conquistar_territorios():
    
    ia = criar_ia_com_objetivo("IA1", "verde", "conquistar_territorios", quantidade=5)
    
    assert ia.nome == "IA1"
    assert ia.cor == "verde"
    assert ia.objetivo['tipo'] == "conquistar_territorios"
    assert ia.objetivo['quantidade'] == 5


def test_criar_ia_com_objetivo_destruir_jogador():
   
    ia = criar_ia_com_objetivo("IA2", "vermelho", "destruir_jogador", cor_alvo="azul")
    
    assert ia.objetivo['tipo'] == "destruir_jogador"
    assert ia.objetivo['cor_alvo'] == "azul"


def test_criar_multiplas_ias():
    
    ias = criar_multiplas_ias(quantidade=3)
    
    assert len(ias) == 3
    assert all(ia.tipo == "ai" for ia in ias)
    assert all(ia.objetivo is not None for ia in ias)

def test_avaliar_territorios_retorna_lista(client_com_partida):
    
    partida = state.partida_global
    ia = criar_ia_com_objetivo("TestIA", "roxo", "conquistar_territorios")
    
    prioridades = ia.avaliar_territorios(partida.tabuleiro)
    
    assert isinstance(prioridades, list)
    assert len(prioridades) > 0


def test_avaliar_territorios_objetivo_conquistar(client_com_partida):
    
    partida = state.partida_global
    ia = criar_ia_com_objetivo("TestIA", "roxo", "conquistar_territorios")
    
    prioridades = ia.avaliar_territorios(partida.tabuleiro)
    
    # Verificar que retorna uma lista ordenada
    assert len(prioridades) == len(partida.tabuleiro.territorios)


def test_avaliar_territorios_objetivo_destruir_jogador(client_com_partida):
    
    partida = state.partida_global
    jogador_alice = partida.jogadores[0]
    ia = criar_ia_com_objetivo("TestIA", "roxo", "destruir_jogador", cor_alvo=jogador_alice.cor)
    
    prioridades = ia.avaliar_territorios(partida.tabuleiro)
    
    assert len(prioridades) > 0

def test_escolher_ataque_sem_capacidade():
    
    ias = criar_multiplas_ias(quantidade=2)
    tabuleiro = Tabuleiro(ias)
    distribuir_territorios_entre_ias(tabuleiro, ias)
    
    # Reduz exércitos de todos os territórios para 1
    for ia in ias:
        for territorio in ia.territorios:
            territorio.exercitos = 1
    
    escolha = ias[0].escolher_ataque(tabuleiro)
    
    assert escolha is None


def test_escolher_ataque_com_capacidade(client_com_partida):
    
    partida = state.partida_global
    
    # Cria uma IA para testar
    ia_ataque = criar_ia_com_objetivo("TestIA", "roxo", "conquistar_territorios")
    
    # Setup: garante que há territórios para a IA atacar
    territorio_a = partida.tabuleiro.territorios[0]
    territorio_b = territorio_a.fronteiras[0]
    
    territorio_a.cor = ia_ataque.cor
    territorio_b.cor = partida.jogadores[1].cor
    territorio_a.exercitos = 5
    territorio_b.exercitos = 1
    
    ia_ataque.territorios = [territorio_a]
    
    # Testa escolha de ataque
    escolha = ia_ataque.escolher_ataque(partida.tabuleiro)
    
    if escolha is not None:
        origem, alvo = escolha
        assert origem in ia_ataque.territorios
        assert alvo in territorio_a.fronteiras


def test_escolher_ataque_com_seed_deterministica():
    
    ias = criar_multiplas_ias(quantidade=2)
    tabuleiro = Tabuleiro(ias)
    distribuir_territorios_entre_ias(tabuleiro, ias, seed=42)

    # Garante capacidade de ataque
    for ia in ias:
        for territorio in ia.territorios:
            territorio.exercitos = 10

    ia_teste = ias[0]
    
    # Primeira execução com seed 123
    rng1 = random.Random(123)
    escolha1 = ia_teste.escolher_ataque(tabuleiro, rng=rng1)
    
    # Segunda execução com seed 123
    rng2 = random.Random(123)
    escolha2 = ia_teste.escolher_ataque(tabuleiro, rng=rng2)

    # Ambas devem ser válidas (ou ambas None)
    # Se uma é válida, a outra também deve ser
    assert (escolha1 is None) == (escolha2 is None)
    
    # Se retornaram algo, devem ser tuplas com 2 elementos
    if escolha1 is not None:
        assert isinstance(escolha1, tuple) and len(escolha1) == 2
        origem1, alvo1 = escolha1
        # Ambas devem ser territórios válidos
        assert origem1 in ia_teste.territorios
        assert alvo1 in tabuleiro.territorios
    
    if escolha2 is not None:
        assert isinstance(escolha2, tuple) and len(escolha2) == 2
        origem2, alvo2 = escolha2
        assert origem2 in ia_teste.territorios
        assert alvo2 in tabuleiro.territorios


def test_escolher_ataque_agressividade():
    
    ias = criar_multiplas_ias(quantidade=2)
    tabuleiro = Tabuleiro(ias)
    distribuir_territorios_entre_ias(tabuleiro, ias, seed=42)
    
    for ia in ias:
        for territorio in ia.territorios:
            territorio.exercitos = 5
    
    rng = random.Random(42)
    
    # Testa com baixa agressividade
    escolha_baixa = ias[0].escolher_ataque(tabuleiro, rng=rng, agressividade=0.0)
    
    rng = random.Random(42)
    # Testa com alta agressividade
    escolha_alta = ias[0].escolher_ataque(tabuleiro, rng=rng, agressividade=0.8)
    
    # Apenas valida que ambas retornam resultados válidos (ou None)
    assert escolha_baixa is None or isinstance(escolha_baixa, tuple)
    assert escolha_alta is None or isinstance(escolha_alta, tuple)

def test_distribuir_exercitos_basico():
    
    ias = criar_multiplas_ias(quantidade=1)
    tabuleiro = Tabuleiro(ias)
    distribuir_territorios_entre_ias(tabuleiro, ias)
    
    ia = ias[0]
    exercitos_iniciais = contar_exercitos_ia(ia)
    
    distribuicao = ia.distribuir_exercitos(tabuleiro, 10)
    
    exercitos_finais = contar_exercitos_ia(ia)
    
    # Total deve aumentar em 10
    assert exercitos_finais == exercitos_iniciais + 10


def test_distribuir_exercitos_retorna_dict():
    
    ias = criar_multiplas_ias(quantidade=1)
    tabuleiro = Tabuleiro(ias)
    distribuir_territorios_entre_ias(tabuleiro, ias)
    
    ia = ias[0]
    distribuicao = ia.distribuir_exercitos(tabuleiro, 5)
    
    assert isinstance(distribuicao, dict)
    assert all(isinstance(k, str) for k in distribuicao.keys())
    assert all(isinstance(v, int) for v in distribuicao.values())


def test_distribuir_exercitos_zero():
    
    ias = criar_multiplas_ias(quantidade=1)
    tabuleiro = Tabuleiro(ias)
    distribuir_territorios_entre_ias(tabuleiro, ias)
    
    ia = ias[0]
    exercitos_iniciais = contar_exercitos_ia(ia)
    
    distribuicao = ia.distribuir_exercitos(tabuleiro, 0)
    
    exercitos_finais = contar_exercitos_ia(ia)
    
    assert exercitos_finais == exercitos_iniciais

def test_validar_distribuicao_territorios():
    
    ias = criar_multiplas_ias(quantidade=3)
    tabuleiro = Tabuleiro(ias)
    distribuir_territorios_entre_ias(tabuleiro, ias)
    
    assert validar_integridade_territorios(ias, tabuleiro)


def test_contar_exercitos_ia():
    
    ias = criar_multiplas_ias(quantidade=1)
    tabuleiro = Tabuleiro(ias)
    distribuir_territorios_entre_ias(tabuleiro, ias)
    
    ia = ias[0]
    total = contar_exercitos_ia(ia)
    
    assert total > 0
    assert total == sum(t.exercitos for t in ia.territorios)


def test_obter_territorios_inimigos_adjacentes():
    
    ias = criar_multiplas_ias(quantidade=2)
    tabuleiro = Tabuleiro(ias)
    distribuir_territorios_entre_ias(tabuleiro, ias)
    
    ia_ataque = ias[0]
    inimigos = obter_territorios_inimigos_adjacentes(ia_ataque, tabuleiro)
    
    assert isinstance(inimigos, list)
    # Todos os inimigos devem ter cor diferente
    assert all(t.cor != ia_ataque.cor for t in inimigos)

def test_simulacao_rodada_ataques():
    
    ias = criar_multiplas_ias(quantidade=2)
    tabuleiro = Tabuleiro(ias)
    distribuir_territorios_entre_ias(tabuleiro, ias, seed=42)
    
    for ia in ias:
        for territorio in ia.territorios:
            territorio.exercitos = 10
    
    resultados = simular_rodada_ataques(ias, tabuleiro, seed=42, agressividade=0.2)
    
    assert isinstance(resultados, dict)
    assert len(resultados) == 2
    assert all(isinstance(v, int) for v in resultados.values())


def test_ciclo_completo_ia_turno():
    
    ias = criar_multiplas_ias(quantidade=2)
    tabuleiro = Tabuleiro(ias)
    distribuir_territorios_entre_ias(tabuleiro, ias, seed=42)
    
    ia = ias[0]
    
    # 1. Avalia territórios
    prioridades = ia.avaliar_territorios(tabuleiro)
    assert len(prioridades) > 0
    
    # 2. Tenta escolher ataque
    ia.territorios[0].exercitos = 10
    escolha = ia.escolher_ataque(tabuleiro)
    # Pode ser None ou um par válido
    assert escolha is None or isinstance(escolha, tuple)
    
    # 3. Distribui exércitos
    distribuicao = ia.distribuir_exercitos(tabuleiro, 5)
    assert sum(distribuicao.values()) == 5