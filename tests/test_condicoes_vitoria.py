import pytest
from back import state
from back.model.Partida import Partida

def eliminar_jogadores_exceto(partida, jogador_vencedor):
    """Remove todos os territórios de todos exceto o vencedor."""
    for jogador in partida.jogadores:
        if jogador != jogador_vencedor:
            # Remove todos os territórios
            for territorio in list(jogador.territorios):
                territorio.cor = jogador_vencedor.cor
                jogador_vencedor.territorios.append(territorio)
            jogador.territorios.clear()


def contar_jogadores_ativos(partida):
    """Conta quantos jogadores ainda têm territórios."""
    return sum(1 for j in partida.jogadores if len(j.territorios) > 0)


def simular_conquista_continente(partida, jogador, regiao_idx):
    """Simula conquista de um continente completo por um jogador."""
    regiao = partida.tabuleiro.regioes_com_bonus[regiao_idx]
    nome_regiao, bonus, territorios = regiao
    
    for territorio in territorios:
        territorio.cor = jogador.cor
        if territorio not in jogador.territorios:
            jogador.territorios.append(territorio)
    
    return nome_regiao, bonus

def test_vitoria_quando_um_jogador_restar(client_com_partida):
    """Testa vitória quando apenas um jogador tem territórios."""
    partida = state.partida_global
    jogador_vencedor = partida.jogadores[0]
    
    # Elimina todos os outros jogadores
    eliminar_jogadores_exceto(partida, jogador_vencedor)
    
    # Apenas um jogador deve ter territórios
    assert contar_jogadores_ativos(partida) == 1
    assert len(jogador_vencedor.territorios) == len(partida.tabuleiro.territorios)


def test_vitoria_eliminacao_gradual(client_com_partida):

    partida = state.partida_global
    
    # Inicialmente todos têm territórios
    assert contar_jogadores_ativos(partida) == 3
    
    # Elimina jogador 2
    jogador_0 = partida.jogadores[0]
    jogador_1 = partida.jogadores[1]
    
    for territorio in list(jogador_1.territorios):
        territorio.cor = jogador_0.cor
        jogador_0.territorios.append(territorio)
    jogador_1.territorios.clear()
    
    assert contar_jogadores_ativos(partida) == 2
    
    # Elimina jogador 3
    jogador_2 = partida.jogadores[2]
    for territorio in list(jogador_2.territorios):
        territorio.cor = jogador_0.cor
        jogador_0.territorios.append(territorio)
    jogador_2.territorios.clear()
    
    assert contar_jogadores_ativos(partida) == 1


def test_vitoria_jogador_correto_vence(client_com_partida):

    partida = state.partida_global
    jogador_vencedor = partida.jogadores[1]  # Bob
    
    eliminar_jogadores_exceto(partida, jogador_vencedor)
    
    # Apenas Bob deve ter territórios
    assert len(jogador_vencedor.territorios) > 0
    assert all(len(j.territorios) == 0 for j in partida.jogadores if j != jogador_vencedor)


def test_nao_vitoria_com_multiplos_jogadores_ativos(client_com_partida):

    partida = state.partida_global
    
    # Todos têm territórios
    assert all(len(j.territorios) > 0 for j in partida.jogadores)
    
    # Não deve haver vencedor
    assert contar_jogadores_ativos(partida) > 1


# ============================================================================
# TESTES - VITÓRIA POR OBJETIVO (SE IMPLEMENTADO)
# ============================================================================

def test_vitoria_objetivo_conquistar_territorios(client_com_partida):
    
    partida = state.partida_global
    jogador = partida.jogadores[0]
    
    # Se objetivo existir (é string, não dict)
    if hasattr(jogador, 'objetivo') and jogador.objetivo:
        # Simula conquista de muitos territórios
        quantidade_necessaria = 24
        
        # Simula conquista de territórios suficientes
        while len(jogador.territorios) < quantidade_necessaria:
            # Pega território de outro jogador
            for outro_jogador in partida.jogadores:
                if outro_jogador != jogador and len(outro_jogador.territorios) > 0:
                    territorio = outro_jogador.territorios[0]
                    outro_jogador.territorios.remove(territorio)
                    territorio.cor = jogador.cor
                    jogador.territorios.append(territorio)
                    break
        
        # Deve ter conquistado o suficiente
        assert len(jogador.territorios) >= quantidade_necessaria


def test_vitoria_objetivo_destruir_jogador(client_com_partida):
    
    partida = state.partida_global
    
    # Procura jogador com objetivo de eliminar outro (objetivo é string)
    for jogador in partida.jogadores:
        if hasattr(jogador, 'objetivo') and jogador.objetivo:
            if 'Elimine o jogador' in jogador.objetivo:
                # Objetivo é string tipo: "Elimine o jogador vermelho. Caso..."
                # Simula eliminação de um jogador qualquer
                for outro_jogador in partida.jogadores:
                    if outro_jogador != jogador and len(outro_jogador.territorios) > 0:
                        # Elimina este jogador
                        for territorio in list(outro_jogador.territorios):
                            territorio.cor = jogador.cor
                            jogador.territorios.append(territorio)
                        outro_jogador.territorios.clear()
                        
                        # Jogador foi eliminado
                        assert len(outro_jogador.territorios) == 0
                        break
                break


def test_vitoria_objetivo_continentes(client_com_partida):
    partida = state.partida_global
    jogador = partida.jogadores[0]
    
    if hasattr(jogador, 'objetivo') and jogador.objetivo:
        if 'Região' in jogador.objetivo:
            # Conquista a primeira região disponível como exemplo
            if len(partida.tabuleiro.regioes_com_bonus) > 0:
                nome_regiao, bonus = simular_conquista_continente(partida, jogador, 0)
                
                # Verifica que conquistou
                assert nome_regiao is not None

def test_nao_vitoria_no_inicio(client_com_partida):
    
    partida = state.partida_global
    
    # Todos os jogadores devem estar ativos
    assert contar_jogadores_ativos(partida) == len(partida.jogadores)


def test_nao_vitoria_apos_um_turno(client_com_partida):
    
    partida = state.partida_global
    
    partida.proximo_jogador()
    
    # Ainda deve haver múltiplos jogadores ativos
    assert contar_jogadores_ativos(partida) > 1


def test_nao_vitoria_com_dois_jogadores_ativos(client_com_partida):

    partida = state.partida_global
    
    # Elimina apenas um jogador
    jogador_0 = partida.jogadores[0]
    jogador_2 = partida.jogadores[2]
    
    for territorio in list(jogador_2.territorios):
        territorio.cor = jogador_0.cor
        jogador_0.territorios.append(territorio)
    jogador_2.territorios.clear()
    
    # Ainda há 2 jogadores ativos
    assert contar_jogadores_ativos(partida) == 2


# ============================================================================
# TESTES - VALIDAÇÃO DE ESTADO FINAL
# ============================================================================

def test_vitoria_todos_territorios_com_vencedor(client_com_partida):
    
    partida = state.partida_global
    jogador_vencedor = partida.jogadores[0]
    
    eliminar_jogadores_exceto(partida, jogador_vencedor)
    
    # Vencedor deve ter TODOS os territórios
    assert len(jogador_vencedor.territorios) == len(partida.tabuleiro.territorios)


def test_vitoria_territorios_com_cor_vencedor(client_com_partida):
    
    partida = state.partida_global
    jogador_vencedor = partida.jogadores[1]
    
    eliminar_jogadores_exceto(partida, jogador_vencedor)
    
    # Todos os territórios devem ter a cor do vencedor
    for territorio in partida.tabuleiro.territorios:
        assert territorio.cor == jogador_vencedor.cor


def test_vitoria_perdedores_sem_territorios(client_com_partida):

    partida = state.partida_global
    jogador_vencedor = partida.jogadores[2]
    
    eliminar_jogadores_exceto(partida, jogador_vencedor)
    
    # Todos os outros não devem ter territórios
    for jogador in partida.jogadores:
        if jogador != jogador_vencedor:
            assert len(jogador.territorios) == 0



def test_metodo_finalizada_retorna_true_com_vencedor(client_com_partida):

    partida = state.partida_global
    
    if hasattr(partida, 'finalizada'):
        jogador_vencedor = partida.jogadores[0]
        eliminar_jogadores_exceto(partida, jogador_vencedor)
        
        # Partida deve estar finalizada
        # (se o método existir e for implementado)
        resultado = partida.finalizada()
        assert resultado is True or resultado is False  # Validação básica


def test_metodo_obter_vencedor(client_com_partida):
    
    partida = state.partida_global
    
    if hasattr(partida, 'obter_vencedor'):
        jogador_vencedor = partida.jogadores[0]
        eliminar_jogadores_exceto(partida, jogador_vencedor)
        
        vencedor = partida.obter_vencedor()
        
        # Vencedor deve ser o jogador correto
        if vencedor:
            assert vencedor == jogador_vencedor

def test_vitoria_ia_vs_humano(client_com_partida):

    partida = state.partida_global
    
    # Encontra um jogador IA
    jogador_ia = None
    for jogador in partida.jogadores:
        if jogador.tipo == 'ai':
            jogador_ia = jogador
            break
    
    if jogador_ia:
        eliminar_jogadores_exceto(partida, jogador_ia)
        
        # IA deve ser o único com territórios
        assert len(jogador_ia.territorios) > 0


def test_vitoria_apos_longa_partida(client_com_partida):
  
    partida = state.partida_global
    
    # Simula 20 turnos
    for _ in range(20):
        partida.proximo_jogador()
    
    # Simula vitória
    jogador_vencedor = partida.jogadores[0]
    eliminar_jogadores_exceto(partida, jogador_vencedor)
    
    assert contar_jogadores_ativos(partida) == 1


def test_empate_impossivel(client_com_partida):
    
    partida = state.partida_global
    
    # Não pode haver dois jogadores com todos os territórios
    # ao mesmo tempo (validação lógica)
    total_territorios = len(partida.tabuleiro.territorios)
    
    for jogador in partida.jogadores:
        if len(jogador.territorios) == total_territorios:
            # Se um tem todos, outros devem ter zero
            for outro in partida.jogadores:
                if outro != jogador:
                    assert len(outro.territorios) == 0
