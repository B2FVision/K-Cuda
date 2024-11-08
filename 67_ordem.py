import os
import subprocess
import time
from datetime import datetime

# Parâmetros base
start_range = int("40000000000000000", 16)
end_range = int("40ce4c1861c5fb2ff", 16)
initial_total_subranges = 100000
address = "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9"
output_file = "viva.txt"
log_file = "saveit.tsv"

# Função para carregar subranges já escaneados e encontrar o último valor escaneado
def carregar_subranges_salvos():
    subranges_escaneados = set()
    ultimo_valor = start_range
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            for linha in f:
                if not linha.startswith("20"):
                    continue
                try:
                    partes = linha.strip().split('\t')
                    if len(partes) >= 3:
                        subrange_start = int(partes[1], 16)
                        subrange_end = int(partes[2], 16)
                        subranges_escaneados.add((partes[1], partes[2]))
                        if subrange_end > ultimo_valor:
                            ultimo_valor = subrange_end
                except Exception as e:
                    print(f"Erro ao processar linha do log: {e}")
    
    return subranges_escaneados, ultimo_valor

# Função para calcular o tamanho do subrange
def calcular_subrange_size(total_subranges):
    return (end_range - start_range) // total_subranges

# Função para gerar o próximo subrange sequencial
def gerar_proximo_subrange(valor_atual, subrange_size):
    if valor_atual >= end_range:
        return None, None
    
    subrange_start = valor_atual
    subrange_end = min(subrange_start + subrange_size, end_range)
    
    return hex(subrange_start)[2:], hex(subrange_end)[2:]

# Função para verificar se o subrange já foi escaneado
def ja_escaneado(subrange_start, subrange_end, subranges_escaneados):
    return (subrange_start, subrange_end) in subranges_escaneados

# Função para salvar o subrange no conjunto e no arquivo de log
def salvar_subrange(subrange_start, subrange_end, subranges_escaneados):
    subranges_escaneados.add((subrange_start, subrange_end))
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()}\t{subrange_start}\t{subrange_end}\n")

# Função para executar o KeyHunt
def executar_keyhunt(subrange_start, subrange_end):
    comando = [
        "./KeyHunt", "--gpu", "--gpui", "0,1,2,3,4,5,6,7", "-m", "address", address,
        "--range", f"{subrange_start}:{subrange_end}",
        "--coin", "BTC", "-o", output_file,
    ]
    processo = subprocess.Popen(comando)
    return processo

# Função principal
def gerenciar_busca():
    # Carrega subranges já escaneados e último valor do arquivo
    subranges_escaneados, valor_atual = carregar_subranges_salvos()
    print(f"Carregados {len(subranges_escaneados)} subranges já escaneados")
    print(f"Iniciando busca a partir de: {hex(valor_atual)[2:]}")
    
    total_subranges = initial_total_subranges
    try:
        while True:
            subrange_size = calcular_subrange_size(total_subranges)
            
            # Gera o próximo subrange sequencial
            subrange_start, subrange_end = gerar_proximo_subrange(valor_atual, subrange_size)
            
            # Verifica se chegamos ao fim do range total
            if subrange_start is None or subrange_end is None:
                print("Busca completa! Alcançado o fim do range.")
                break
            
            if ja_escaneado(subrange_start, subrange_end, subranges_escaneados):
                valor_atual = int(subrange_end, 16)
                continue
            
            salvar_subrange(subrange_start, subrange_end, subranges_escaneados)
            print(f"Escaneando range {subrange_start}:{subrange_end}")
            
            processo = executar_keyhunt(subrange_start, subrange_end)
            # Aguarda 60 segundos (600 segundos = 10 minutos)
            time.sleep(600)
            processo.terminate()
            processo.wait()
            
            # Atualiza o valor atual para o próximo range
            valor_atual = int(subrange_end, 16)
            
            print(f"Progresso: {((valor_atual - start_range) / (end_range - start_range)) * 100:.2f}%")
    
    except KeyboardInterrupt:
        print("\nEncerrando, aguarde...")
        time.sleep(2)
        print("Processo interrompido com sucesso.")
        print(f"Último valor escaneado: {hex(valor_atual)[2:]}")
    
    # Registro do horário de finalização
    with open(log_file, 'a') as f:
        f.write(f"Finalizado em:\t{datetime.now()}\n")

if __name__ == "__main__":
    gerenciar_busca()
