"""
Simple SSE client for testing `/ia/stream` and initializing a 3-player match.
This script:
 - POSTs form data to /inicializar_partida to create a match (1 human + 2 IAs)
 - GETs /partida/estado_atual to find current jogador
 - If the current player is IA, opens SSE to /ia/stream with acao=turno_completo
 - Logs each received SSE event with a timestamp

Run: python tests/ia_sse_client.py
"""
import time
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

BASE = 'http://127.0.0.1:5000'


def now():
    return datetime.now().isoformat()


def post_inicializar():
    url = BASE + '/inicializar_partida'
    data = {
        'acao': 'iniciar',
        'qtd_humanos': '1',
        'qtd_ai': '2',
        'duracao_turno': '30',
        # players: 1 human + 2 IA
        'nome_player_1': 'Human', 'cor_player_1': 'red',
        'nome_player_2': 'IA1', 'cor_player_2': 'blue',
        'nome_player_3': 'IA2', 'cor_player_3': 'green'
    }
    body = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    print(now(), 'POST', url)
    with urllib.request.urlopen(req, timeout=10) as r:
        status = r.getcode()
        print(now(), 'status', status)
        if status != 200:
            txt = r.read().decode('utf-8', errors='ignore')
            print(txt)
            raise SystemExit('Failed to initialize partida')


def get_estado():
    url = BASE + '/partida/estado_atual'
    print(now(), 'GET', url)
    with urllib.request.urlopen(url, timeout=10) as r:
        status = r.getcode()
        txt = r.read().decode('utf-8')
        print(now(), 'status', status)
        if status != 200:
            print(txt)
            raise SystemExit('Failed to get estado_atual')
        return json.loads(txt)


def parse_sse_lines(iterable):
    """Yield complete data blobs parsed from SSE lines (simple parser)."""
    buffer = []
    for raw in iterable:
        if not raw:
            # keepalive or empty
            continue
        line = raw.decode('utf-8') if isinstance(raw, bytes) else raw
        line = line.strip('\r')
        if line == '':
            if buffer:
                yield '\n'.join(buffer)
                buffer = []
            continue
        if line.startswith('data:'):
            buffer.append(line[len('data:'):].strip())
        # skip other SSE fields
    if buffer:
        yield '\n'.join(buffer)


def open_ia_stream(jogador_id, acao='turno_completo', agressividade=0.0, timeout=120):
    url = BASE + '/ia/stream'
    params = {'jogador_id': jogador_id, 'acao': acao, 'agressividade': str(agressividade)}
    print(now(), 'Opening SSE', url, 'params=', params)
    q = urllib.parse.urlencode(params)
    full = url + '?' + q
    req = urllib.request.Request(full)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            start = time.time()
            buff = []
            while True:
                line = r.readline()
                if not line:
                    # stream ended
                    break
                if isinstance(line, bytes):
                    line = line.decode('utf-8')
                line = line.strip('\r\n')
                if line == '':
                    if buff:
                        data_blob = '\n'.join(buff)
                        buff = []
                        ts = now()
                        try:
                            obj = json.loads(data_blob)
                        except Exception:
                            print(ts, 'Invalid JSON in SSE data:', data_blob[:200])
                            continue
                        print(ts, 'SSE_EVENT:', obj)
                        tipo = obj.get('tipo') if isinstance(obj, dict) else None
                        if tipo in ('turno_finalizado', 'erro'):
                            print(now(), 'Stream ended by event type', tipo)
                            return
                    # continue reading
                    if time.time() - start > timeout:
                        print(now(), 'Stream timeout exceeded')
                        return
                    continue
                if line.startswith('data:'):
                    buff.append(line[len('data:'):].strip())
                # ignore other sse fields
    except Exception as e:
        print(now(), 'Failed to open SSE stream:', e)


def main():
    # allow server some startup time
    for _ in range(6):
        try:
            with urllib.request.urlopen('http://127.0.0.1:5000/', timeout=2) as r:
                if r.getcode() == 200:
                    break
        except Exception:
            pass
        print(now(), 'waiting for server...')
        time.sleep(1)

    # initialize partida
    post_inicializar()
    time.sleep(0.5)
    estado = get_estado()
    jogador_id = estado['turno']['jogador_id']
    fase = estado['turno']['fase']
    print(now(), 'turno-> jogador_id=', jogador_id, 'fase=', fase)

    # if current player is IA, open stream
    # otherwise, find next IA player in /partida/jogadores
    # open stream for current player if IA-looking, otherwise find first IA player
    nome = estado['turno'].get('jogador_nome','').lower()
    if nome.startswith('ia') or estado['turno']['jogador_id'] in ['blue','green']:
        open_ia_stream(jogador_id)
        return

    # try to detect first IA in /partida/jogadores
    try:
        with urllib.request.urlopen(BASE + '/partida/jogadores', timeout=5) as r:
            txt = r.read().decode('utf-8')
            data = json.loads(txt)
    except Exception:
        print(now(), 'Failed to fetch jogadores')
        return
    ia_player = None
    for j in data.get('jogadores', []):
        if j.get('ia'):
            ia_player = j.get('jogador_id')
            break
    if ia_player:
        print(now(), 'Opening stream for first IA player found:', ia_player)
        open_ia_stream(ia_player)
    else:
        print(now(), 'No IA player found in jogadores')


if __name__ == '__main__':
    main()
