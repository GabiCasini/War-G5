from flask import Blueprint, request, jsonify, Response, stream_with_context
import json
import time

from .. import state
import traceback

ia_bp = Blueprint('ia', __name__, url_prefix='/ia')


@ia_bp.route('/acao', methods=['POST'])
def ia_acao():
    """
    Executa uma ação da IA para o jogador indicado.
    Payload esperado (JSON):
      {
        "jogador_id": "cor_do_jogador",
        "acao": "posicionamento" | "ataque" | "turno_completo",
        "agressividade": 0.0  # opcional, float
      }

    Retorna JSON com o resultado da ação.
    """
    if not state.partida_global:
        return jsonify({"status": "erro", "mensagem": "Partida não iniciada"}), 400

    dados = request.get_json() or {}
    jogador_id = dados.get('jogador_id')
    acao = dados.get('acao')
    try:
        agressividade = float(dados.get('agressividade', 0.0))
    except Exception:
        agressividade = 0.0

    if not jogador_id:
        return jsonify({"status": "erro", "mensagem": "Campo 'jogador_id' é obrigatório"}), 400
    if not acao:
        return jsonify({"status": "erro", "mensagem": "Campo 'acao' é obrigatório"}), 400

    jogador = state.partida_global.get_jogador_por_cor(jogador_id)
    if not jogador:
        return jsonify({"status": "erro", "mensagem": "Jogador não encontrado"}), 400

    if jogador.tipo != 'ai':
        return jsonify({"status": "erro", "mensagem": "Jogador não é IA"}), 400

    partida = state.partida_global

    try:
        resultado = {"status": "ok"}

        if acao == 'posicionamento':
            # garante que o jogador tenha exércitos a receber calculados
            if getattr(jogador, 'exercitos_reserva', 0) <= 0:
                partida.tabuleiro.calcula_exercitos_a_receber(jogador)

            distribuicao = jogador.distribuir_exercitos(partida.tabuleiro, jogador.exercitos_reserva)
            # após distribuir, zera a reserva (assume que a função já aplicou)
            jogador.remover_exercitos_para_posicionamento(jogador.exercitos_reserva)
            resultado['distribuicao'] = distribuicao

            # construir lista de eventos de posicionamento (um evento por exército posicionado)
            eventos = []
            # ordenar por quantidade descendente para mostrar primeiro reforços maiores
            for nome, qtd in sorted(distribuicao.items(), key=lambda x: -x[1]):
                for i in range(int(qtd)):
                    eventos.append({"tipo": "posicionar", "territorio": nome, "qtd": 1})
            resultado['events'] = eventos

        elif acao == 'ataque':
            # usar o gerador da IA para construir eventos (compatível com streaming)
            eventos_ataque = []
            ataques = 0
            try:
                for ev in jogador.executar_ataques_generator(partida, rng=None, agressividade=agressividade, max_ataques=50):
                    eventos_ataque.append(ev)
                    if ev.get('tipo') == 'ataque_resultado':
                        ataques += 1
            except Exception:
                # fallback para API síncrona
                try:
                    ataques, lista = jogador.executar_ataques(partida, rng=None, agressividade=agressividade, max_ataques=50)
                    eventos_ataque.extend(lista or [])
                except Exception:
                    pass
            resultado['ataques_efetuados'] = ataques
            resultado['events'] = eventos_ataque

        elif acao == 'turno_completo':
            # posicionamento
            if getattr(jogador, 'exercitos_reserva', 0) <= 0:
                partida.tabuleiro.calcula_exercitos_a_receber(jogador)
            distribuicao = jogador.distribuir_exercitos(partida.tabuleiro, jogador.exercitos_reserva)
            jogador.remover_exercitos_para_posicionamento(jogador.exercitos_reserva)

            # construir eventos de posicionamento
            eventos = []
            for nome, qtd in sorted(distribuicao.items(), key=lambda x: -x[1]):
                for i in range(int(qtd)):
                    eventos.append({"tipo": "posicionar", "territorio": nome, "qtd": 1})

            # ataque (coletar eventos via gerador)
            try:
                for ev in jogador.executar_ataques_generator(partida, rng=None, agressividade=agressividade, max_ataques=50):
                    eventos.append(ev)
            except Exception:
                try:
                    ataques, eventos_ataque = jogador.executar_ataques(partida, rng=None, agressividade=agressividade, max_ataques=50)
                    eventos.extend(eventos_ataque or [])
                except Exception:
                    pass

            # reposicionamento
            repos = []
            if hasattr(jogador, 'executar_reposicionamento'):
                repos = jogador.executar_reposicionamento(partida, max_movimentos=10)
                # cada movimento é um evento
                for m in repos:
                    eventos.append({"tipo": "reposicionar", "origem": m.get('origem'), "destino": m.get('destino'), "qtd": m.get('qtd')})

            resultado.update({
                'distribuicao': distribuicao,
                'ataques_efetuados': ataques,
                'reposicionamento': repos,
                'events': eventos,
            })

            # Ao finalizar o turno da IA, avançar fases/turno até passar a vez para o próximo jogador.
            # Faz até 4 tentativas para evitar loop infinito caso algo raro aconteça.
            try:
                jogador_cor_atual = jogador.cor
                tentativas = 0
                # enquanto o jogador atual for o mesmo, avançar fases
                while tentativas < 4 and partida.jogadores[partida.jogador_atual_idx].cor == jogador_cor_atual:
                    partida.avancar_fase_ou_turno()
                    tentativas += 1
                # se após as tentativas ainda for o mesmo jogador, forçar passagem para o próximo jogador
                if partida.jogadores[partida.jogador_atual_idx].cor == jogador_cor_atual:
                    partida.proximo_jogador()
            except Exception:
                # não bloquear a resposta ao cliente por falhas de avanço; apenas tentar seguir o fluxo
                try:
                    partida.proximo_jogador()
                except Exception:
                    pass

        else:
            return jsonify({"status": "erro", "mensagem": "Ação inválida"}), 400

        return jsonify(resultado)

    except Exception as e:
        tb = traceback.format_exc()
        # print stack to server console for debugging
        print(tb)
        return jsonify({"status": "erro", "mensagem": str(e), "traceback": tb}), 500


@ia_bp.route('/stream', methods=['GET'])
def ia_stream():
    """Stream SSE que emite eventos da IA em tempo real.

    Query params esperados: jogador_id, acao (posicionamento|ataque|turno_completo), agressividade (opcional)
    """
    if not state.partida_global:
        return jsonify({"status": "erro", "mensagem": "Partida não iniciada"}), 400

    jogador_id = request.args.get('jogador_id')
    acao = request.args.get('acao')
    try:
        agressividade = float(request.args.get('agressividade', 0.0))
    except Exception:
        agressividade = 0.0

    if not jogador_id or not acao:
        return jsonify({"status": "erro", "mensagem": "Parâmetros 'jogador_id' e 'acao' obrigatórios"}), 400

    jogador = state.partida_global.get_jogador_por_cor(jogador_id)
    if not jogador or jogador.tipo != 'ai':
        return jsonify({"status": "erro", "mensagem": "Jogador IA não encontrado"}), 400

    partida = state.partida_global

    def gen():
        try:
            # POSICIONAMENTO
            if acao in ('posicionamento', 'turno_completo'):
                if getattr(jogador, 'exercitos_reserva', 0) <= 0:
                    partida.tabuleiro.calcula_exercitos_a_receber(jogador)
                distribuicao = jogador.distribuir_exercitos(partida.tabuleiro, jogador.exercitos_reserva)
                try:
                    jogador.remover_exercitos_para_posicionamento(jogador.exercitos_reserva)
                except Exception:
                    pass

                # emitir um evento por exército posicionado
                for nome, qtd in sorted(distribuicao.items(), key=lambda x: -x[1]):
                    for _ in range(int(qtd)):
                        ev = {"tipo": "posicionar", "fase": "posicionamento", "territorio": nome, "qtd": 1}
                        yield f"data: {json.dumps(ev)}\n\n"
                        # delay unificado para 1s entre ações
                        time.sleep(1.0)

            # ATAQUE: usar o gerador de ataques da IA para emitir eventos em tempo real
            if acao in ('ataque', 'turno_completo'):
                try:
                    for ev in jogador.executar_ataques_generator(partida, rng=None, agressividade=agressividade, max_ataques=50):
                        # garantir que eventos de ataque venham com 'fase' definido pelo gerador
                        yield f"data: {json.dumps(ev)}\n\n"
                        # delay unificado para 1s entre ações
                        time.sleep(1.0)
                except Exception:
                    # se o gerador falhar por algum motivo, apenas continuar
                    pass

            # REPOSICIONAMENTO
            if acao in ('reposicionamento', 'turno_completo'):
                repos = []
                if hasattr(jogador, 'executar_reposicionamento'):
                    repos = jogador.executar_reposicionamento(partida, max_movimentos=10)
                    for m in repos:
                        ev = {"tipo": "reposicionar", "fase": "reposicionamento", "origem": m.get('origem'), "destino": m.get('destino'), "qtd": m.get('qtd')}
                        yield f"data: {json.dumps(ev)}\n\n"
                        # delay unificado para 1s entre ações
                        time.sleep(1.0)

            # Ao finalizar, avançar fases/turno como antes
            try:
                jogador_cor_atual = jogador.cor
                tentativas = 0
                while tentativas < 4 and partida.jogadores[partida.jogador_atual_idx].cor == jogador_cor_atual:
                    partida.avancar_fase_ou_turno()
                    tentativas += 1
                if partida.jogadores[partida.jogador_atual_idx].cor == jogador_cor_atual:
                    partida.proximo_jogador()
            except Exception:
                try:
                    partida.proximo_jogador()
                except Exception:
                    pass

            # envia evento final indicando conclusão
            yield f"data: {json.dumps({"tipo": "turno_finalizado", "status": "ok"})}\n\n"

        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            err = {"tipo": "erro", "mensagem": str(e)}
            yield f"data: {json.dumps(err)}\n\n"

    return Response(stream_with_context(gen()), mimetype='text/event-stream', headers={"Cache-Control": "no-cache"})
