import time
import json
import random
import sys
import os
from datetime import datetime

# garantir que o diretório do projeto esteja no sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from back.model.Partida import Partida


def now():
    return datetime.now().isoformat()


def simulate_turn(partida: Partida, jogador):
    events = []
    print(now(), '=== Iniciando simulação de turno para IA', jogador.nome)

    # POSICIONAMENTO
    partida.tabuleiro.calcula_exercitos_a_receber(jogador)
    total_reserva = getattr(jogador, 'exercitos_reserva', 0)
    print(now(), 'Exércitos na reserva:', total_reserva)
    distribuicao = jogador.distribuir_exercitos(partida, jogador.exercitos_reserva)
    # refletir consumo da reserva (como faz o controller)
    try:
        jogador.remover_exercitos_para_posicionamento(total_reserva)
    except Exception:
        pass

    # emitir eventos de posicionamento (um por exército)
    for nome, qtd in sorted(distribuicao.items(), key=lambda x: -x[1]):
        for _ in range(int(qtd)):
            ev = {"tipo": "posicionar", "fase": "posicionamento", "territorio": nome, "qtd": 1}
            print(now(), 'EVENTO', json.dumps(ev))
            events.append(ev)
            time.sleep(1.0)

    # ATAQUES (usando generator)
    for ev in jogador.executar_ataques_generator(partida, rng=random.Random(), agressividade=0.0, max_ataques=10):
        print(now(), 'EVENTO', json.dumps(ev))
        events.append(ev)
        # após resultado de ataque, checar consistência de exércitos
        if ev.get('tipo') == 'ataque_resultado':
            # checar se algum territorio ficou com 0
            zeros = [t.nome for t in partida.tabuleiro.territorios if t.exercitos == 0]
            if zeros:
                print(now(), 'ERRO: territórios com 0 exércitos detectados após ataque:', zeros)
        time.sleep(1.0)

    # REPOSICIONAMENTO
    repos = []
    if hasattr(jogador, 'executar_reposicionamento'):
        repos = jogador.executar_reposicionamento(partida, max_movimentos=10)
        for m in repos:
            ev = {"tipo": "reposicionar", "fase": "reposicionamento", "origem": m.get('origem'), "destino": m.get('destino'), "qtd": m.get('qtd')}
            print(now(), 'EVENTO', json.dumps(ev))
            events.append(ev)
            # checar zeros após movimento
            zeros = [t.nome for t in partida.tabuleiro.territorios if t.exercitos == 0]
            if zeros:
                print(now(), 'ERRO: territórios com 0 exércitos detectados após reposicionamento:', zeros)
            time.sleep(1.0)

    # resumo final: verificar novamente
    zeros_final = [t.nome for t in partida.tabuleiro.territorios if t.exercitos == 0]
    if zeros_final:
        print(now(), 'FAIL - territórios com 0 exércitos:', zeros_final)
    else:
        print(now(), 'PASS - nenhum território com 0 exércitos')

    print(now(), 'Eventos totais gerados:', len(events))
    return events


def main():
    random.seed(0)
    # cria partida 1 humano + 2 IA
    tupla = [('Human', 'red', 'humano'), ('IA1', 'blue', 'ai'), ('IA2', 'green', 'ai')]
    partida = Partida(1, 2, 30, tupla)

    # escolher primeira IA que aparecer na ordem dos jogadores
    ia = next((j for j in partida.jogadores if getattr(j, 'tipo', None) == 'ai'), None)
    if not ia:
        print('Nenhuma IA encontrada na partida')
        return

    events = simulate_turn(partida, ia)


if __name__ == '__main__':
    main()
