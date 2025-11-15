from flask import Blueprint, request, jsonify, Response, stream_with_context
import json
import time

from .. import state
import traceback

ia_bp = Blueprint('ia', __name__, url_prefix='/ia')

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
            if (partida.libera_ataque is True) and acao in ('ataque', 'turno_completo'):
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
            if acao in ('reposicionamento', 'turno_completo') and (partida.libera_ataque is True):
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
                while tentativas < 3 and partida.jogadores[partida.jogador_atual_idx].cor == jogador_cor_atual:
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
            dados = {"tipo": "turno_finalizado", "status": "ok"}
            yield f"data: {json.dumps(dados)}\n\n"

        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            err = {"tipo": "erro", "mensagem": str(e)}
            yield f"data: {json.dumps(err)}\n\n"

    return Response(stream_with_context(gen()), mimetype='text/event-stream', headers={"Cache-Control": "no-cache"})
