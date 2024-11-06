import os
import random
import subprocess
import time
from datetime import datetime

# Parâmetros base
start_range = int("40000000000000000", 16)
end_range = int("7ffffffffffffffff", 16)

initial_total_subranges = 100000
address = "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9"
output_file = "FOUNDFOUNDFOUND.txt"
log_file = "67-Aleatorio.tsv"

# Conjunto para armazenar subranges já escaneados
subranges_escaneados = set()

# Função para calcular o tamanho do subrange
def calcular_subrange_size(total_subranges):
    return (end_range - start_range) // total_subranges

# Função para gerar um subrange aleatório
def gerar_subrange(subrange_size):
    subrange_start = random.randint(start_range, end_range - subrange_size)
    subrange_end = subrange_start + subrange_size
    return hex(subrange_start)[2:], hex(subrange_end)[2:]

# Função para verificar se o subrange já foi escaneado
def ja_escaneado(subrange_start, subrange_end):
    return (subrange_start, subrange_end) in subranges_escaneados

# Função para salvar o subrange no conjunto e no arquivo de log
def salvar_subrange(subrange_start, subrange_end):
    subranges_escaneados.add((subrange_start, subrange_end))
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()}\t{subrange_start}\t{subrange_end}\n")

# Função para executar o KeyHunt
def executar_keyhunt(subrange_start, subrange_end):
    comando = [
        "./KeyHunt", "--gpu", "-m", "address", address,
        "--range", f"{subrange_start}:{subrange_end}",
        "--coin", "BTC", "-o", output_file,
    ]
    processo = subprocess.Popen(comando)
    return processo

# Função principal
def gerenciar_busca():
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

                if ja_escaneado(subrange_start, subrange_end):
                    continue  # Pula se já foi escaneado

                salvar_subrange(subrange_start, subrange_end)

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
