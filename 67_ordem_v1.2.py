import os
import subprocess
import time
from datetime import datetime

# Parâmetros base
start_range = "462c481bbd83cca06"  # Defina seu range inicial aqui
end_range = "46e67f6004ff990e6"    # Defina seu range final aqui
address = "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9"
output_file = "viva.txt"
log_file = "saveit.tsv"

def carregar_ultima_chave():
    """Carrega a última chave testada do arquivo de log"""
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            linhas = f.readlines()
            for linha in reversed(linhas):
                if not linha.startswith("20"):  # Ignora linhas que não começam com data
                    continue
                try:
                    chave = linha.strip().split('\t')[1]
                    return chave
                except:
                    continue
    return None

def salvar_progresso(chave_atual, status="em_andamento"):
    """Salva o progresso atual no arquivo de log"""
    with open(log_file, 'a') as f:
        if status == "em_andamento":
            f.write(f"{datetime.now()}\t{chave_atual}\n")
        elif status == "concluido":
            f.write(f"{datetime.now()}\t{chave_atual}\tRANGE COMPLETO\n")
            print(f"\nRange completo! Última chave testada: {chave_atual}")
            print(f"Timestamp de conclusão: {datetime.now()}")

def executar_keyhunt():
    """Executa o KeyHunt com o range especificado"""
    comando = [
        "./KeyHunt",
        "--gpu",
        "-m", "address",
        address,
        "--range", f"{start_range}:{end_range}",
        "--coin", "BTC",
        "-o", output_file,
    ]
    
    try:
        processo = subprocess.Popen(comando)
        
        while processo.poll() is None:  # Enquanto o processo estiver rodando
            # Salva o progresso atual a cada 10 minutos
            salvar_progresso(start_range)
            time.sleep(600)  # Aguarda 10 minutos
        
        # Verifica se o processo terminou normalmente (retorno 0)
        if processo.returncode == 0:
            # Salva o progresso final indicando conclusão do range
            salvar_progresso(end_range, "concluido")
        else:
            print(f"\nProcesso terminou com código de erro: {processo.returncode}")
            
    except KeyboardInterrupt:
        print("\nEncerrando o processo...")
        processo.terminate()
        processo.wait()
        print("Processo finalizado por interrupção do usuário.")
        # Salva o estado no momento da interrupção
        salvar_progresso(start_range, "interrompido")
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        if processo:
            processo.terminate()
            processo.wait()
    finally:
        # Registra a finalização
        with open(log_file, 'a') as f:
            f.write(f"Sessão finalizada em:\t{datetime.now()}\n")
            f.write("-" * 50 + "\n")  # Linha separadora para melhor visualização

if __name__ == "__main__":
    # Verifica se existe progresso anterior
    ultima_chave = carregar_ultima_chave()
    if ultima_chave:
        print(f"Última chave testada: {ultima_chave}")
    
    print(f"Iniciando busca no range: {start_range}:{end_range}")
    print(f"Iniciado em: {datetime.now()}")
    print("Progresso será salvo a cada 10 minutos em:", log_file)
    executar_keyhunt()