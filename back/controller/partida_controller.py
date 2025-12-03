from flask import Blueprint, jsonify, request

from .. import state

partida_bp = Blueprint('partida', __name__, url_prefix='/partida')

@partida_bp.route("/salvar_partida", methods=["POST", "GET"])
def salvar_partida_route():
    state.salvar_partida(state.partida_global)
    return ("Partida Salva", 204)

@partida_bp.route("/resetar_partida", methods=["POST", "GET"])
def resetar_partida_route():
    state.apagar_partida()
    return ("Partida Resetada", 204)

# Retorna lista de jogadores da partida e suas informacoes
@partida_bp.route("/jogadores", methods=["GET"])
def get_jogadores():
    
    if not state.partida_global:
        return jsonify({"status": "erro", "mensagem": "Partida não iniciada"}), 400
    
    jogadores_json = []

    for i, jogador in enumerate(state.partida_global.jogadores):
        jogadores_json.append({
            "jogador_id": jogador.cor,
            "nome": jogador.nome,
            "cor": jogador.cor,
            "ia": jogador.tipo == 'ai',
            "objetivo": jogador.objetivo,
            "ordem": i + 1,
            "exercitos_reserva": jogador.exercitos_reserva
        })

    return jsonify({"jogadores": jogadores_json})

# Retorna lista de territorios do tabuleiro
@partida_bp.route("/territorios", methods=["GET"])
def get_territorios():
    if not state.partida_global:
        return jsonify({"status": "erro", "mensagem": "Partida não iniciada"}), 400

    territorios_json = []
    
    for territorio in state.partida_global.tabuleiro.territorios:

        jogador_dono = next((j for j in state.partida_global.jogadores if j.cor == territorio.cor), None)
        
        territorios_json.append({
            "nome": territorio.nome,
            "regiao": territorio.regiao,
            "jogador_id": jogador_dono.cor,
            "cor_jogador": jogador_dono.cor,
            "exercitos": territorio.exercitos,
            "fronteiras": [f.nome for f in territorio.fronteiras]
        })

    return jsonify({"territorios": territorios_json})


@partida_bp.route('/debug_jogadores', methods=['GET'])
def debug_jogadores():
    if not state.partida_global:
        return jsonify({"status": "erro", "mensagem": "Partida não iniciada"}), 400

    lista = []
    for j in state.partida_global.jogadores:
        lista.append({
            'nome': j.nome,
            'cor': j.cor,
            'tipo': j.tipo,
            'class': j.__class__.__name__
        })
    return jsonify({'jogadores': lista})

# Retorna o estado atual da partida - fase atual, jogador atual e seus dados 
@partida_bp.route("/estado_atual", methods=["GET"])
def get_estado_atual():

    if not state.partida_global:
        return jsonify({"status": "erro", "mensagem": "Partida não iniciada"}), 400

    jogador_atual = state.partida_global.jogadores[state.partida_global.jogador_atual_idx]

    fase_atual = state.partida_global.fase_do_turno 
    
    exercitos_disp_total = jogador_atual.exercitos_reserva

    territorios_do_jogador_obj = jogador_atual.territorios
   
    territorios_jogador_json = []
    for t in territorios_do_jogador_obj:
        territorios_jogador_json.append({"nome": t.nome, "regiao": t.regiao, "exercitos": t.exercitos})

    # JSON final
    estado_json = {
        "turno": {
            "jogador_id": jogador_atual.cor,
            "jogador_nome": jogador_atual.nome,
            "jogador_cor": jogador_atual.cor,
            "fase": fase_atual,
            "tempo_turno": int(state.partida_global.duracao_turno)
        },
    
        "exercitos_disponiveis": {
            "jogador_id": jogador_atual.cor,
            "total" : exercitos_disp_total, 
        },
        "territorios_jogador": {
            "jogador_id": jogador_atual.cor,
            "nome": jogador_atual.nome,
            "territorios": territorios_jogador_json
        }
    }
    return jsonify(estado_json)

# Faz os cálculos da regra de negócio e retorna a quantidade de tropas restantes após um posicionamento  
@partida_bp.route("/posicionamento", methods=["POST"])
def post_posicionamento():
    if not state.partida_global:
        return jsonify({"status": "erro", "mensagem": "Partida não iniciada"}), 400
    if state.partida_global.finalizado:
        return jsonify({"status": "finalizado", "mensagem": f"Partida finalizada. Vencedor: {state.partida_global.vencedor}"}), 400

    dados = request.get_json() 
    
    jogador_cor = dados.get("jogador_id")
    territorio_nome = dados.get("territorio")
    exercitos = int(dados.get("exercitos"))

    jogador_obj = state.partida_global.get_jogador_por_cor(jogador_cor)

    try:
        exercitos_restantes = state.partida_global.fase_de_posicionamento(jogador_cor, territorio_nome, exercitos)
        objetivo_finalizado = state.partida_global.manager_de_objetivos.verifica_objetivo_de_todos_os_jogadores(
            jogador_obj,
            state.partida_global.get_jogadores_vivos(),
            state.partida_global.get_jogadores_eliminados(),
            state.partida_global.get_tabuleiro()
        )
        print(f"[DEBUG] Resultado da verificação de objetivo no posicionamento: {objetivo_finalizado}")
        if objetivo_finalizado:
            print(f"[DEBUG] Finalizando partida! Vencedor: {objetivo_finalizado}")
            state.partida_global.finalizar_partida(objetivo_finalizado)
            return jsonify({
                "status": "finalizado",
                "mensagem": f"Partida finalizada. Vencedor: {objetivo_finalizado}",
                "objetivo_finalizado": objetivo_finalizado
            })
        print("Exércitos restantes após posicionamento:", exercitos_restantes)
        return jsonify({"status": "ok", "objetivo_finalizado": objetivo_finalizado, "exercitos_restantes": exercitos_restantes })
    except Exception as e:
        print(f"[ERRO] Exception no posicionamento: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 400

# Faz os cálculos da regra de ataque do jogo e retorna o resultado dos dados e a atualização da batalha
@partida_bp.route("/ataque", methods=["POST"])
def post_ataque():
    if not state.partida_global:
        return jsonify({"status": "erro", "mensagem": "Partida não iniciada"}), 400
    if state.partida_global.finalizado:
        return jsonify({"status": "finalizado", "mensagem": f"Partida finalizada. Vencedor: {state.partida_global.vencedor}"}), 400

    dados = request.get_json()

    jogador_id = dados.get("jogador_id")
    nome_territorio_origem = dados.get("territorio_origem")
    nome_territorio_ataque = dados.get("territorio_ataque")

    atacante = state.partida_global.get_jogador_por_cor(jogador_id)
    territorio_origem = state.partida_global.get_territorio_por_nome(nome_territorio_origem)
    territorio_alvo = state.partida_global.get_territorio_por_nome(nome_territorio_ataque)
    
    # Validação de território alvo
    if not territorio_alvo:
        return jsonify({"status": "erro", "mensagem": "Território de ataque não encontrado"}), 400
    
    defensor = state.partida_global.get_jogador_por_cor(territorio_alvo.cor)
    
    try:
        resultado = state.partida_global.resolver_combate(atacante, defensor, territorio_origem, territorio_alvo)
        objetivo_finalizado = state.partida_global.manager_de_objetivos.verifica_objetivo_de_todos_os_jogadores(atacante, state.partida_global.get_jogadores_vivos(), state.partida_global.get_jogadores_eliminados(), state.partida_global.get_tabuleiro())
        if objetivo_finalizado:
            print(f"[DEBUG] Finalizando partida! Vencedor: {objetivo_finalizado}")
            state.partida_global.finalizar_partida(objetivo_finalizado)
            return jsonify({
                "status": "finalizado",
                "mensagem": f"Partida finalizada. Vencedor: {objetivo_finalizado}",
                "objetivo_finalizado": objetivo_finalizado,
                **resultado
            })
        return jsonify({"status": "ok", "objetivo_finalizado": objetivo_finalizado, **resultado})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 400

@partida_bp.route("/reposicionamento", methods=["POST"])
def post_reposicionamento():
    if not state.partida_global:
        return jsonify({"status": "erro", "mensagem": "Partida não iniciada"}), 400
    if state.partida_global.finalizado:
        return jsonify({"status": "finalizado", "mensagem": f"Partida finalizada. Vencedor: {state.partida_global.vencedor}"}), 400

    dados = request.get_json()

    jogador_cor = dados.get("jogador_id")
    nome_origem = dados.get("territorio_origem")
    nome_destino = dados.get("territorio_destino")
    exercitos = int(dados.get("exercitos"))

    jogador_obj = state.partida_global.get_jogador_por_cor(jogador_cor)
    
    try:
        resultado = state.partida_global.fase_de_reposicionamento(jogador_cor, nome_origem, nome_destino, exercitos)
        objetivo_finalizado = state.partida_global.manager_de_objetivos.verifica_objetivo_de_todos_os_jogadores(
            jogador_obj,
            state.partida_global.get_jogadores_vivos(),
            state.partida_global.get_jogadores_eliminados(),
            state.partida_global.get_tabuleiro()
        )
        print(f"[DEBUG] Resultado da verificação de objetivo no reposicionamento: {objetivo_finalizado}")
        if objetivo_finalizado:
            print(f"[DEBUG] Finalizando partida! Vencedor: {objetivo_finalizado}")
            state.partida_global.finalizar_partida(objetivo_finalizado)
            return jsonify({
                "status": "finalizado",
                "mensagem": f"Partida finalizada. Vencedor: {objetivo_finalizado}",
                "objetivo_finalizado": objetivo_finalizado,
                **resultado
            })
        return jsonify({"status": "ok", "objetivo_finalizado": objetivo_finalizado, **resultado})
    except Exception as e:
        print(f"[ERRO] Exception no reposicionamento: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 400

@partida_bp.route("/finalizar_turno", methods=["POST"])
def post_finalizar_turno():
    if not state.partida_global:
        return jsonify({"status": "erro", "mensagem": "Partida não iniciada"}), 400
    try:
        proximo_jogador, nova_fase = state.partida_global.finalizar_turno_atual()
        
        resposta = {
            "status": "ok",
            "proximo_jogador": {
                "jogador_id": proximo_jogador.cor,
                "nome": proximo_jogador.nome,
                "cor": proximo_jogador.cor,
                "fase": nova_fase 
            }
        }
        return jsonify(resposta)
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 400

@partida_bp.route("/avancar_turno", methods=["POST"])
def post_avancar_turno():
    if not state.partida_global:
        return jsonify({"status": "erro", "mensagem": "Partida não iniciada"}), 400

    try:
        proximo_jogador, nova_fase = state.partida_global.avancar_fase_ou_turno()

        resposta = {
            "status": "ok",
            "proximo_jogador": {
                "jogador_id": proximo_jogador.cor,
                "nome": proximo_jogador.nome,
                "cor": proximo_jogador.cor,
                "fase": nova_fase 
            }
        }

        # Não executar turnos da IA de forma síncrona aqui — isso faz com que
        # as ações da IA ocorram instantaneamente no cliente. Em vez disso,
        # o cliente deve detectar que o próximo jogador é IA (via /partida/estado_atual)
        # e abrir a stream SSE (`/ia/stream`) para receber ações em tempo real.
        partida = state.partida_global
        proximo = partida.jogadores[partida.jogador_atual_idx]
        resposta['proximo_e_ia'] = (proximo.tipo == 'ai')
        # Nota: mantemos a informação do próximo jogador em `resposta['proximo_jogador']`.

        return jsonify(resposta)
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 400