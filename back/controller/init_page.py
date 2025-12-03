import os
from flask import Blueprint, redirect, render_template, request
from ..model.Partida import Partida
from .. import state
from flask import jsonify

init_page_bp = Blueprint('init_page', __name__)

class PaginaIndex:

    @init_page_bp.route('/inicializar_partida', methods=['POST'])
    def inicializar_partida():
        if request.method == 'POST':
            # Suporta tanto JSON (para testes/API) quanto form data (para frontend)
            if request.is_json:
                dados = request.get_json()
                qtd_humanos = dados.get('qtd_humanos', 0)
                qtd_ai = dados.get('qtd_ai', 0)
                duracao_turno = dados.get('duracao_turno', 60)
                
                # Suporta dois formatos de payload:
                # 1. 'jogadores': [{'nome': 'X', 'cor': 'Y', 'tipo': 'Z'}]
                # 2. 'nomes': ['Alice', 'Bob', 'Charlie']
                if 'jogadores' in dados:
                    jogadores = dados.get('jogadores', [])
                    tupla_jogadores = []
                    for jogador in jogadores:
                        nome = jogador.get('nome')
                        cor = jogador.get('cor')
                        tipo = jogador.get('tipo', 'humano')
                        tupla_jogadores.append((nome, cor, tipo))
                else:
                    # Formato simplificado com apenas nomes
                    nomes = dados.get('nomes', [])
                    cores = ['vermelho', 'azul', 'verde', 'amarelo', 'preto', 'branco']
                    tupla_jogadores = []
                    
                    for i, nome in enumerate(nomes):
                        cor = cores[i % len(cores)]
                        tipo = 'humano' if i < qtd_humanos else 'ai'
                        tupla_jogadores.append((nome, cor, tipo))
                
                state.partida_global = Partida(qtd_humanos, qtd_ai, duracao_turno, tupla_jogadores, shuffle_jogadores=False)
                
                return jsonify({
                    'status': 'ok',
                    'mensagem': 'Partida inicializada com sucesso',
                    'jogadores': [{'nome': j.nome, 'cor': j.cor, 'tipo': j.tipo} for j in state.partida_global.jogadores]
                })
            
            # Form data (original)
            if request.form.get('acao') == 'iniciar':
                qtd_humanos = int(request.form.get('qtd_humanos'))
                qtd_ai = int(request.form.get('qtd_ai'))
                duracao_turno = request.form.get('duracao_turno')

                tupla_jogadores = []
                for i in range(qtd_humanos+qtd_ai):
                    nome = request.form.get(f'nome_player_{i+1}')
                    cor = request.form.get(f'cor_player_{i+1}')
                    tipo = 'humano' if i < qtd_humanos else 'ai'
                    tupla_jogadores.append((nome, cor, tipo))

                if not os.path.exists(state.ARQUIVO):
                    state.partida_global = Partida(qtd_humanos, qtd_ai, duracao_turno, tupla_jogadores)
                else: 
                    state.partida_global = state.carregar_partida()
                return render_template('mapa.html', partida=state.partida_global)
            
            return redirect('/')