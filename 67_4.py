import os
import random
import subprocess
import time
from datetime import datetime

# Parâmetros base
start_range = int("58888888888888889", 16)
end_range = int("5ffffffffffffffff", 16)
initial_total_subranges = 100000
address = "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9"
output_file = "viva.txt"
log_file = "saveit.tsv"

# Função para carregar subranges já escaneados do arquivo
def carregar_subranges_salvos():
    subranges_escaneados = set()
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            for linha in f:
                # Ignora linhas que não contêm ranges (como linhas de início/fim de ciclo)
                if not linha.startswith("20"):  # Assume que linhas de data começam com ano
                    continue
                try:
                    partes = linha.strip().split('\t')
                    if len(partes) >= 3:
                        subrange_start = partes[1]
                        subrange_end = partes[2]
                        subranges_escaneados.add((subrange_start, subrange_end))
                except Exception as e:
                    print(f"Erro ao processar linha do log: {e}")
    return subranges_escaneados

# Função para calcular o tamanho do subrange
def calcular_subrange_size(total_subranges):
    return (end_range - start_range) // total_subranges

# Função para gerar um subrange aleatório
def gerar_subrange(subrange_size):
    subrange_start = random.randint(start_range, end_range - subrange_size)
    subrange_end = subrange_start + subrange_size
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
    # Carrega subranges já escaneados do arquivo
    subranges_escaneados = carregar_subranges_salvos()
    print(f"Carregados {len(subranges_escaneados)} subranges já escaneados")
    
    total_subranges = initial_total_subranges
    try:
        while True:
            subranges_verificados = 0
            with open(log_file, 'a') as f:
                f.write(f"Início do ciclo de {total_subranges} subranges:\t{datetime.now()}\n")
            
            while subranges_verificados < total_subranges:
                subrange_size = calcular_subrange_size(total_subranges)
                # Gera um novo subrange
                subrange_start, subrange_end = gerar_subrange(subrange_size)
                
                if ja_escaneado(subrange_start, subrange_end, subranges_escaneados):
                    continue  # Pula se já foi escaneado
                
                salvar_subrange(subrange_start, subrange_end, subranges_escaneados)
                print(f"Escaneando range {subrange_start}:{subrange_end}")
                
                processo = executar_keyhunt(subrange_start, subrange_end)
                # Aguarda 60 segundos, então mata o processo e inicia o próximo subrange
                time.sleep(600)
                processo.terminate()  # Finaliza o processo atual
                processo.wait()  # Aguarda o término completo do processo
                
                # Incrementa o contador de subranges verificados
                subranges_verificados += 1
                print(f"Subranges verificados: {subranges_verificados}/{total_subranges}")
            
            # Aumenta o total de subranges se não encontrar
            total_subranges += 1
            print(f"Todos os {total_subranges - 1} subranges verificados. Adicionando mais um subrange e reiniciando o processo...")
    
    except KeyboardInterrupt:
        print("\nEncerrando, aguarde...")
        time.sleep(2)
        print("Processo interrompido com sucesso.")
    
    # Registro do horário de finalização
    with open(log_file, 'a') as f:
        f.write(f"Finalizado em:\t{datetime.now()}\n")

if __name__ == "__main__":
    gerenciar_busca()
