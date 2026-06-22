import os
import time
import matplotlib.pyplot as plt
from constantes import SIMBOLO_EOF, TAMANHO_JANELA
from io_bits import EscritorDeBits
from codificador_aritmetico import Encoder
from modelo_ppm import ModeloPPMC
from codificador_ppm import codificar_simbolo_ppm

#simula a compressão para coletar dados, sem gerar um arquivo real
class ArquivoFalso:
    def __init__(self):
        self.tamanho = 0
    def write(self, byte_array):
        self.tamanho += len(byte_array)
    def tell(self):
        return self.tamanho

def coletar_dados_progressivos(caminho_entrada, k_max):
    print(f"  -> Coletando dados para K_max = {k_max}...")
    
    arquivo_saida_falso = ArquivoFalso()
    escritor = EscritorDeBits(arquivo_saida_falso)
    encoder = Encoder(escritor)
    modelo = ModeloPPMC(k_max)

    historico_x = [] #eixo X: Quantidade de símbolos processados
    historico_y = [] #eixo Y: Comprimento Médio (Bits/Símbolo)

    simbolos_processados = 0

    def obter_bits_totais():
        return arquivo_saida_falso.tell() * 8 + escritor.bits_no_buffer

    with open(caminho_entrada, 'rb') as f_in:
        while True:
            bloco = f_in.read(4096)
            if not bloco:
                break

            for simbolo in bloco:
                codificar_simbolo_ppm(simbolo, modelo, encoder)
                modelo.atualizar_contexto_e_frequencia(simbolo)
                simbolos_processados += 1

                #a cada janela, anotamos a taxa global para o gráfico
                if simbolos_processados % TAMANHO_JANELA == 0:
                    bits_gerados = obter_bits_totais()
                    comprimento_medio = bits_gerados / simbolos_processados
                    
                    historico_x.append(simbolos_processados)
                    historico_y.append(comprimento_medio)

    codificar_simbolo_ppm(SIMBOLO_EOF, modelo, encoder)
    encoder.finalizar()
    
    bits_finais = obter_bits_totais()
    tamanho_final_bytes = bits_finais / 8
    print(f"     [Concluído] Tamanho final simulado: {tamanho_final_bytes:.2f} bytes")
    
    return historico_x, historico_y

def gerar_grafico(caminho_entrada, lista_kmax):
    nome_arquivo = os.path.basename(caminho_entrada)
    print(f"=== Iniciando Análise do Arquivo: {nome_arquivo} ===")
    
    plt.figure(figsize=(10, 6))
    
    for k in lista_kmax:
        tempo_inicio = time.time()
        x, y = coletar_dados_progressivos(caminho_entrada, k)
        tempo_fim = time.time()
        
        #plota a linha deste K no gráfico
        plt.plot(x, y, label=f'K = {k} ({tempo_fim - tempo_inicio:.1f}s)')
        
    plt.title(f'Comprimento Médio Progressivo PPM-C\nArquivo: {nome_arquivo}')
    plt.xlabel('Símbolos Processados (Bytes)')
    plt.ylabel('Comprimento Médio (Bits/Símbolo)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    #salva a imagem
    os.makedirs('saidas/graficos', exist_ok=True)
    caminho_imagem = f'saidas/graficos/analise_{nome_arquivo}.png'
    plt.savefig(caminho_imagem)
    print(f"\nGráfico salvo com sucesso em: {caminho_imagem}")
    plt.show()

if __name__ == "__main__":
    arquivo_teste = "Silesia/dickens" 
    
    #lista de valores para K_max
    ordens_para_testar = [0, 1, 2, 3] 
    
    if os.path.exists(arquivo_teste):
        gerar_grafico(arquivo_teste, ordens_para_testar)
    else:
        print(f"Erro: Arquivo '{arquivo_teste}' não encontrado. Ajuste o caminho no final do script.")