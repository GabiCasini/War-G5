class Partida():
    def __init__(
        self,
        qtd_humanos: int, # qtd de jogadores humanos
        qtd_ai: int, # qtd de jogadores artificiais
        duracao_turno: int, # segundos
    ):
        assert 6 >= qtd_humanos + qtd_ai >= 3
        self.qtd_humanos = qtd_humanos
        self.qtd_ai = qtd_ai
        self.qtd_jogadores = qtd_humanos + qtd_ai
        self.duracao_turno = duracao_turno
