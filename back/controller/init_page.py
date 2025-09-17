from flask import Blueprint, redirect, request

from model.Partida import Partida

init_page_bp = Blueprint('init_page', __name__)

class PaginaIndex:

    @init_page_bp.route('/inicializar_partida', methods=['POST'])
    def inicializar_partida():
        if request.method == 'POST':
            qtd_humanos = int(request.form.get('qtd_humanos'))
            qtd_ai = int(request.form.get('qtd_ai'))
            duracao_turno = request.form.get('duracao_turno')
            partida = Partida(qtd_humanos, qtd_ai, duracao_turno)

            return redirect('/') 
