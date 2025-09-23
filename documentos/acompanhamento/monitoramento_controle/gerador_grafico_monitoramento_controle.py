import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

try:
    df = pd.read_csv('documentos/acompanhamento/monitoramento_controle/valores_agregados_histórico.txt', parse_dates=['Data'])
except FileNotFoundError:
    print("Arquivo 'valores_agregados_histórico.txt' não encontrado. Verifique o nome e o local do arquivo.")
    exit()

versao = date.today().strftime('%Y-%m-%d')

# Calcula os índices SPI e CPI se eles não existirem
if 'SPI' not in df.columns or 'CPI' not in df.columns:
    df['SPI'] = df['EV'] / df['PV']
    df['CPI'] = df['EV'] / df['AC']

df['DataString'] = df['Data'].dt.strftime('%d/%m/%Y')

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
fig.suptitle('Análise de Valor Agregado (EVA)', fontsize=16)

# Gráfico 1: PV, EV, AC
ax1.plot(df['DataString'], df['PV'], marker='o', linestyle='-', label='VP (Valor Planejado)')
ax1.plot(df['DataString'], df['EV'], marker='o', linestyle='-', label='VA (Valor Agregado)')
ax1.plot(df['DataString'], df['AC'], marker='o', linestyle='-', label='CR (Custo Real)')
ax1.set_ylabel('Custo (R$)')
ax1.set_title('Custos ao Longo do Tempo')
ax1.legend()
ax1.grid(True)

# Gráfico 2: SPI, CPI
ax2.plot(df['DataString'], df['SPI'], marker='o', linestyle='-', label='IDP (Índice de Desempenho de Prazo)')
ax2.plot(df['DataString'], df['CPI'], marker='o', linestyle='-', label='IDC (Índice de Desempenho de Custo)')
ax2.axhline(y=1.0, color='r', linestyle='--', label='Linha de Base (1.0)')
ax2.set_ylabel('Índice')
ax2.set_title('Índices de Desempenho')
ax2.legend()
ax2.grid(True)

ax2.set_xlabel('Data')
plt.xticks(rotation=45, ha='right')

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(f'documentos/acompanhamento/monitoramento_controle/analise_valor_agregado_atualizada_{versao}.png')

print("Gráfico 'analise_valor_agregado_atualizada.png' foi salvo com sucesso!")