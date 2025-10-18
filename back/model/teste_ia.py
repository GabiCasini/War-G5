from .Tabuleiro import Tabuleiro
from .Jogador import Jogador
from .IA import IA
from .Territorio import Territorio

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
    # Exemplo: 4 IAs, 10 territórios (ajuste conforme necessário)
    distribuicao = [
        (jogadores[0], [(0, 3), (1, 2), (2, 1)]),  # IA1: 3 territórios
        (jogadores[1], [(3, 2), (4, 4), (5, 1)]),  # IA2: 3 territórios
        (jogadores[2], [(6, 2), (7, 3)]),          # IA3: 2 territórios
        (jogadores[3], [(8, 1), (9, 5)])           # IA4: 2 territórios
    ]
    for jogador, terrs in distribuicao:
        for idx, ex in terrs:
            territorios[idx].cor = jogador.cor
            territorios[idx].exercitos = ex
            jogador.adicionar_territorio(territorios[idx])


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

if __name__ == "__main__":
    testar_ia_2()
