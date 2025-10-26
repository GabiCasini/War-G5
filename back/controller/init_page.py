from flask import Blueprint, redirect, render_template, request

from ..model.Partida import Partida

from .. import state

init_page_bp = Blueprint('init_page', __name__)

class PaginaIndex:

    @init_page_bp.route('/inicializar_partida', methods=['POST'])
    def inicializar_partida():

        if request.method == 'POST':
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

                state.partida_global = Partida(qtd_humanos, qtd_ai, duracao_turno, tupla_jogadores)
                return render_template('mapa.html', partida= state.partida_global)
            
            return redirect('/')