
import os
import subprocess
from datetime import datetime

# Parâmetros base
start_range = int("567c0000000000000", 16)  # Converte para inteiro
end_range = int("567cfffffffffffff", 16)    # Converte para inteiro
address = "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9"
output_file = "viva.txt"
log_file = "saveit.tsv"

# Tamanho do subrange (44 bits)
SUBRANGE_SIZE = 2**45

def carregar_ultimo_subrange():
    """Carrega o último subrange processado do arquivo de log"""
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            linhas = f.readlines()
            for linha in reversed(linhas):
                if not linha.startswith("20"):  # Ignora linhas que não começam com data
                    continue
                try:
                    partes = linha.strip().split('\t')
                    if len(partes) >= 3:  # Verifica se tem start e end range
                        subrange_end = int(partes[2], 16)
                        return subrange_end
                except:
                    continue
    return start_range

def salvar_progresso(subrange_start, subrange_end, status="subrange_completo"):
    """Salva o progresso no arquivo de log"""
    with open(log_file, 'a') as f:
        start_hex = hex(subrange_start)[2:]  # Remove o '0x' do início
        end_hex = hex(subrange_end)[2:]      # Remove o '0x' do início
        
        if status == "subrange_completo":
            f.write(f"{datetime.now()}\t{start_hex}\t{end_hex}\n")
        elif status == "busca_completa":
            f.write(f"{datetime.now()}\t{start_hex}\t{end_hex}\tBUSCA COMPLETA\n")
        
        print(f"\nSubrange completo: {start_hex} até {end_hex}")
        print(f"Timestamp: {datetime.now()}")

def gerar_proximo_subrange(valor_atual):
    """Gera o próximo subrange de 44 bits"""
    if valor_atual >= end_range:
        return None, None
    
    subrange_start = valor_atual
    subrange_end = min(subrange_start + SUBRANGE_SIZE, end_range)
    
    return subrange_start, subrange_end

def get_gpu_count():
    try:
        output = subprocess.check_output(["nvidia-smi", "--query-gpu=index", "--format=csv,noheader"], universal_newlines=True)
        gpu_ids = [line.strip() for line in output.split("\n") if line.strip().isdigit()]
        return len(gpu_ids)
    except Exception as e:
        print(f"Erro ao detectar GPUs: {e}")
        return 1  # Valor padrão

num_gpus = get_gpu_count()

def executar_keyhunt(subrange_start, subrange_end):
    """Executa o KeyHunt para um subrange específico"""
    start_hex = hex(subrange_start)[2:]
    end_hex = hex(subrange_end)[2:]
    
    comando = [
        "./KeyHunt",
        "--gpu",
        "-m", "address",
        address,
        "--range", f"{start_hex}:{end_hex}",
        "--coin", "BTC",
        "--gpui", ",".join(str(i) for i in range(num_gpus)),
        "-o", output_file,
    ]
    
    try:
        processo = subprocess.Popen(comando)
        processo.wait()  # Aguarda a conclusão do processo
        
        # Verifica se o processo terminou normalmente
        if processo.returncode == 0:
            salvar_progresso(subrange_start, subrange_end)
            return True
        else:
            print(f"\nProcesso terminou com código de erro: {processo.returncode}")
            return False
            
    except KeyboardInterrupt:
        print("\nEncerrando o processo...")
        processo.terminate()
        processo.wait()
        print("Processo finalizado por interrupção do usuário.")
        return False
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        if processo:
            processo.terminate()
            processo.wait()
        return False

def gerenciar_busca():
    """Gerencia a busca completa usando subranges"""
    # Carrega o último valor processado
    valor_atual = carregar_ultimo_subrange()
    print(f"Iniciando a partir de: {hex(valor_atual)[2:]}")
    
    try:
        while True:
            # Gera o próximo subrange
            subrange_start, subrange_end = gerar_proximo_subrange(valor_atual)
            
            if subrange_start is None or subrange_end is None:
                print("\nBusca completa! Alcançado o fim do range total.")
                salvar_progresso(start_range, end_range, "busca_completa")
                break
            
            print(f"\nIniciando subrange: {hex(subrange_start)[2:]} até {hex(subrange_end)[2:]}")
            
            # Executa o KeyHunt para este subrange
            sucesso = executar_keyhunt(subrange_start, subrange_end)
            
            if not sucesso:
                break
            
            # Atualiza o valor atual para o próximo subrange
            valor_atual = subrange_end
            
            # Calcula e mostra o progresso total
            progresso = (valor_atual - start_range) / (end_range - start_range) * 100
            print(f"Progresso total: {progresso:.2f}%")
            
    except KeyboardInterrupt:
        print("\nEncerrando o programa...")
    finally:
        # Registra a finalização da sessão
        with open(log_file, 'a') as f:
            f.write(f"Sessão finalizada em:\t{datetime.now()}\n")
            f.write("-" * 50 + "\n")

if __name__ == "__main__":
    print(f"Iniciando gerenciador de busca")
    print(f"Range total: {hex(start_range)[2:]} até {hex(end_range)[2:]}")
    print(f"Tamanho do subrange: 44 bits ({SUBRANGE_SIZE} chaves por subrange)")
    print(f"Iniciado em: {datetime.now()}")
    print("Progresso será salvo em:", log_file)
    
    gerenciar_busca()
