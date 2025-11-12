import json
from pathlib import Path


def carregar_territorios_json():
    """
    Carrega os dados dos territórios do arquivo JSON.
    """
    # Encontra o arquivo JSON em back/data/
    caminho_arquivo = Path(__file__).resolve().parent.parent / "data" / "de-para-territorios.json"
    
    if not caminho_arquivo.exists():
        raise FileNotFoundError(
            f"Arquivo de territórios não encontrado em: {caminho_arquivo}\n"
            f"Caminho procurado: {caminho_arquivo.absolute()}"
        )
    
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)
        return dados['territorios']
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Erro ao decodificar JSON: {e}", e.doc, e.pos)


def obter_territorios_como_lista():
    """
    Converte o JSON para o formato de lista usado anteriormente.
    """
    territorios_json = carregar_territorios_json()
    
    resultado = []
    for t in territorios_json:
        resultado.append([
            t['nome'],
            t['regiao'],
            t['fronteiras']
        ])
    
    return resultado


def validar_territorios():
    """
    Valida a integridade dos dados de territórios:
    - Verifica se todas as fronteiras existem
    - Verifica se as fronteiras são bidirecionais (se A->B, então B->A)
    """
    territorios = carregar_territorios_json()
    nomes_territorios = {t['nome'] for t in territorios}
    erros = []
    
    # Verifica se todas as fronteiras existem
    for territorio in territorios:
        for fronteira in territorio['fronteiras']:
            if fronteira not in nomes_territorios:
                erros.append(
                    f"Território '{territorio['nome']}' referencia fronteira inexistente: '{fronteira}'"
                )
    
    # Verifica se as fronteiras são bidirecionais
    mapa_territorios = {t['nome']: t for t in territorios}
    for territorio in territorios:
        for fronteira_nome in territorio['fronteiras']:
            territorio_fronteira = mapa_territorios.get(fronteira_nome)
            if territorio_fronteira:
                if territorio['nome'] not in territorio_fronteira['fronteiras']:
                    erros.append(
                        f"Fronteira não-bidirecional: '{territorio['nome']}' -> '{fronteira_nome}', "
                        f"mas '{fronteira_nome}' não contém '{territorio['nome']}'"
                    )
    
    return {
        'valido': len(erros) == 0,
        'erros': erros
    }


def obter_territorio_por_nome(nome):
    """
    Busca um território específico pelo nome.
    """
    territorios = carregar_territorios_json()
    for t in territorios:
        if t['nome'].lower() == nome.lower():
            return t
    return None


def obter_territorios_por_regiao(regiao):
    """
    Retorna todos os territórios de uma região específica.
    """
    territorios = carregar_territorios_json()
    return [t for t in territorios if t['regiao'] == regiao]


def obter_todas_as_regioes():
    """
    Retorna uma lista de todas as regiões.
    """
    territorios = carregar_territorios_json()
    regioes = set()
    for t in territorios:
        regioes.add(t['regiao'])
    return sorted(list(regioes))