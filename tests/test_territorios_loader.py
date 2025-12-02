import pytest
import json
from pathlib import Path
from back.utils.territorios_loader import (
    carregar_territorios_json,
    obter_territorios_como_lista,
    validar_territorios,
    obter_territorio_por_nome,
    obter_territorios_por_regiao,
    obter_todas_as_regioes
)

def contar_territorios():
    
    return len(carregar_territorios_json())


def obter_nome_primeiro_territorio():
    
    territorios = carregar_territorios_json()
    return territorios[0]['nome'] if territorios else None


def obter_todas_as_fronteiras():
    
    territorios = carregar_territorios_json()
    fronteiras = set()
    for t in territorios:
        fronteiras.update(t['fronteiras'])
    return fronteiras

def test_carregar_territorios_json_retorna_lista():
    
    territorios = carregar_territorios_json()
    assert isinstance(territorios, list)

def test_carregar_territorios_json_nao_vazio():
    
    territorios = carregar_territorios_json()
    assert len(territorios) > 0

def test_carregar_territorios_json_quantidade():
    
    territorios = carregar_territorios_json()
    # Ajuste o número conforme a quantidade real no seu JSON
    assert len(territorios) >= 40

def test_cada_territorio_tem_nome():
    
    territorios = carregar_territorios_json()
    for t in territorios:
        assert 'nome' in t
        assert isinstance(t['nome'], str)
        assert len(t['nome']) > 0

def test_cada_territorio_tem_regiao():
    
    territorios = carregar_territorios_json()
    for t in territorios:
        assert 'regiao' in t
        assert isinstance(t['regiao'], str)
        assert t['regiao'].startswith('Regiao_')

def test_cada_territorio_tem_fronteiras():
    
    territorios = carregar_territorios_json()
    for t in territorios:
        assert 'fronteiras' in t
        assert isinstance(t['fronteiras'], list)

def test_nomes_territorios_unicos():
    
    territorios = carregar_territorios_json()
    nomes = [t['nome'] for t in territorios]
    assert len(nomes) == len(set(nomes))

def test_validar_territorios_retorna_dict():
    
    resultado = validar_territorios()
    assert isinstance(resultado, dict)
    assert 'valido' in resultado
    assert 'erros' in resultado

def test_validar_territorios_valido():
    
    resultado = validar_territorios()
    assert resultado['valido'] is True

def test_validar_territorios_sem_erros():
    
    resultado = validar_territorios()
    assert len(resultado['erros']) == 0

def test_validar_fronteiras_existem():
    
    territorios = carregar_territorios_json()
    nomes_validos = {t['nome'] for t in territorios}
    
    for t in territorios:
        for fronteira in t['fronteiras']:
            assert fronteira in nomes_validos, \
                f"Fronteira '{fronteira}' de '{t['nome']}' não existe"

def test_validar_fronteiras_bidirecionais():
    
    territorios = carregar_territorios_json()
    mapa = {t['nome']: t for t in territorios}
    
    for t in territorios:
        for fronteira_nome in t['fronteiras']:
            vizinho = mapa[fronteira_nome]
            assert t['nome'] in vizinho['fronteiras'], \
                f"Fronteira não-bidirecional: {t['nome']} -> {fronteira_nome}"

def test_obter_territorios_como_lista_retorna_lista():
    
    resultado = obter_territorios_como_lista()
    assert isinstance(resultado, list)

def test_obter_territorios_como_lista_nao_vazio():
    
    resultado = obter_territorios_como_lista()
    assert len(resultado) > 0

def test_obter_territorios_como_lista_formato():
    
    resultado = obter_territorios_como_lista()
    for item in resultado:
        assert isinstance(item, list)
        assert len(item) == 3
        assert isinstance(item[0], str)  # nome
        assert isinstance(item[1], str)  # regiao
        assert isinstance(item[2], list)  # fronteiras

def test_obter_territorio_por_nome_existente():
    
    primeiro_nome = obter_nome_primeiro_territorio()
    resultado = obter_territorio_por_nome(primeiro_nome)
    
    assert resultado is not None
    assert resultado['nome'] == primeiro_nome

def test_obter_territorio_por_nome_inexistente():
    
    resultado = obter_territorio_por_nome("TERRITORIO_INEXISTENTE_12345")
    assert resultado is None

def test_obter_territorio_por_nome_case_insensitive():
    
    primeiro_nome = obter_nome_primeiro_territorio()
    resultado_lower = obter_territorio_por_nome(primeiro_nome.lower())
    resultado_upper = obter_territorio_por_nome(primeiro_nome.upper())
    
    assert resultado_lower is not None
    assert resultado_upper is not None
    assert resultado_lower['nome'] == resultado_upper['nome']

def test_obter_territorio_por_nome_retorna_dict():
    
    primeiro_nome = obter_nome_primeiro_territorio()
    resultado = obter_territorio_por_nome(primeiro_nome)
    
    assert isinstance(resultado, dict)
    assert 'nome' in resultado
    assert 'regiao' in resultado
    assert 'fronteiras' in resultado

def test_obter_territorios_por_regiao_retorna_lista():
    
    resultado = obter_territorios_por_regiao("Regiao_1")
    assert isinstance(resultado, list)

def test_obter_territorios_por_regiao_nao_vazio():
    
    regioes = obter_todas_as_regioes()
    for regiao in regioes:
        resultado = obter_territorios_por_regiao(regiao)
        assert len(resultado) > 0

def test_obter_territorios_por_regiao_filtrado_corretamente():
    
    resultado = obter_territorios_por_regiao("Regiao_1")
    for t in resultado:
        assert t['regiao'] == "Regiao_1"

def test_obter_territorios_por_regiao_inexistente():
    
    resultado = obter_territorios_por_regiao("Regiao_INEXISTENTE")
    assert resultado == []

def test_obter_todas_as_regioes_retorna_lista():
    
    resultado = obter_todas_as_regioes()
    assert isinstance(resultado, list)

def test_obter_todas_as_regioes_nao_vazio():
    
    resultado = obter_todas_as_regioes()
    assert len(resultado) > 0

def test_obter_todas_as_regioes_sao_strings():
    
    resultado = obter_todas_as_regioes()
    for regiao in resultado:
        assert isinstance(regiao, str)

def test_obter_todas_as_regioes_ordenadas():
    
    resultado = obter_todas_as_regioes()
    assert resultado == sorted(resultado)

def test_obter_todas_as_regioes_unicas():
    
    resultado = obter_todas_as_regioes()
    assert len(resultado) == len(set(resultado))

def test_obter_todas_as_regioes_quantidade():
    
    resultado = obter_todas_as_regioes()
    assert len(resultado) == 6

def test_integracao_todos_territorios_em_alguma_regiao():
    
    territorios = carregar_territorios_json()
    regioes = set(obter_todas_as_regioes())
    
    for t in territorios:
        assert t['regiao'] in regioes

def test_integracao_cobertura_completa_regioes():
    
    territorios = carregar_territorios_json()
    regioes_dict = {regiao: [] for regiao in obter_todas_as_regioes()}
    
    for t in territorios:
        regioes_dict[t['regiao']].append(t)
    
    # Cada região deve ter territórios
    for regiao, territorios_regiao in regioes_dict.items():
        assert len(territorios_regiao) > 0

def test_integracao_busca_por_nome_em_regiao():
    
    primeiro_territorio = carregar_territorios_json()[0]
    nome = primeiro_territorio['nome']
    regiao = primeiro_territorio['regiao']
    
    # Busca por nome
    resultado_nome = obter_territorio_por_nome(nome)
    assert resultado_nome is not None
    
    # Busca por região
    resultado_regiao = obter_territorios_por_regiao(regiao)
    assert any(t['nome'] == nome for t in resultado_regiao)