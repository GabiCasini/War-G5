from back.model.Tabuleiro import Tabuleiro
from back.model.IA import IA
from back.model.Partida import Partida
import random

# Cenário de teste controlado para IA_2

def criar_jogadores_e_ias():
    # 4 IAs com diferentes objetivos
    jogadores = [
        IA("IA1", "verde", objetivo={"tipo": "conquistar_territorios", "quantidade": 3}),
        IA("IA2", "amarelo", objetivo={"tipo": "conquistar_territorios_exercitos", "quantidade": 2, "min_exercitos": 2}),
        IA("IA3", "roxo", objetivo={"tipo": "destruir_jogador", "cor_alvo": "amarelo"}),
        IA("IA4", "preto", objetivo={"tipo": "conquistar_continentes", "continentes": ["Regiao1", "Regiao2"]})
    ]
    return jogadores


def distribuir_territorios_e_exercitos(tabuleiro, jogadores):
    # Cada IA terá 2 ou 3 territórios, e cada território pode receber mais de 1 exército
    for jogador in jogadores:
        jogador.territorios.clear()
    territorios = tabuleiro.territorios
    # Distribui todos os territórios do tabuleiro entre os jogadores em round-robin
    # Atribui 1-3 exércitos por território usando RNG com seed fixa para reprodutibilidade
    rng = random.Random(42)
    for j in jogadores:
        j.territorios.clear()

    for i, territorio in enumerate(territorios):
        jogador = jogadores[i % len(jogadores)]
        territorio.cor = jogador.cor
        # exércitos iniciais entre 1 e 3
        territorio.exercitos = 1 + rng.randint(0, 2)
        jogador.adicionar_territorio(territorio)


def testar_ia_2():
    jogadores = criar_jogadores_e_ias()
    tabuleiro = Tabuleiro(jogadores)
    distribuir_territorios_e_exercitos(tabuleiro, jogadores)

    print("\nSituação inicial:\n")
    for jogador in jogadores:
        print(f"{jogador.nome} ({jogador.cor}):")
        for t in jogador.territorios:
            print(f"  - {t.nome}: {t.exercitos} exércitos")
        print("")

    print("\nAvaliação de territórios pelas IAs:\n")
    for jogador in jogadores:
        if isinstance(jogador, IA):
            avaliados = jogador.avaliar_territorios(tabuleiro)
            print(f"{jogador.nome} ({jogador.objetivo['tipo']}) prioridade: {[t.nome for t in avaliados]}\n")

    print("\nDistribuição de exércitos pelas IAs (exemplo com 7 exércitos):\n")
    for jogador in jogadores:
        if isinstance(jogador, IA):
            distribuicao = jogador.distribuir_exercitos(tabuleiro, 7)
            print(f"{jogador.nome} distribuição:")
            for t, qtd in distribuicao.items():
                print(f"  - {t}: +{qtd} exércitos")
            print("")


    print("\nSituação final:\n")
    for jogador in jogadores:
        print(f"{jogador.nome} ({jogador.cor}):")
        for t in jogador.territorios:
            print(f"  - {t.nome}: {t.exercitos} exércitos")
        print("")

    # --- Preparar uma Partida para permitir que as IAs executem ataques ---
    # Criamos uma Partida 'placeholder' e substituímos os jogadores e o tabuleiro
    partida = Partida(qtd_humanos=0, qtd_ai=4, duracao_turno=60, tupla_jogadores=[('p','c','ai')]*4)
    partida.jogadores = jogadores
    partida.tabuleiro = tabuleiro
    partida.qtd_jogadores = len(jogadores)

    # Executar ataques para cada IA
    print("\nExecutando ataques das IAs:\n")
    for jogador in jogadores:
        if isinstance(jogador, IA):
            rng = random.Random(42)  # seed para resultados reproduzíveis
            ataques = jogador.executar_ataques(partida, rng=rng, agressividade=0.2, max_ataques=10)
            print(f"{jogador.nome} efetuou {ataques} ataques.")
            # Mostrar estado dos territórios do jogador após ataques
            print(f"Estado dos territórios de {jogador.nome} após ataques:")
            for t in jogador.territorios:
                print(f"  - {t.nome}: {t.exercitos} exércitos (cor: {t.cor})")
            print("")


if __name__ == "__main__":
    testar_ia_2()
