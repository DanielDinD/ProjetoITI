import os
from constantes import (
    SIMBOLO_RESET, SIMBOLO_EOF,
    TAMANHO_JANELA, GATILHO_PIORA_TAXA,
    INTERVALO_PODA
)
from io_bits import EscritorDeBits
from codificador_aritmetico import Encoder
from modelo_ppm import ModeloPPMC
from codificador_ppm import codificar_simbolo_ppm

def comprimir_arquivo(caminho_entrada, caminho_saida, k_max, opcao):
    tamanho_original = os.path.getsize(caminho_entrada)
    print(f"Iniciando compressão: {caminho_entrada} (Tamanho: {tamanho_original} bytes | Kmax: {k_max})")

    with open(caminho_entrada, 'rb') as f_in, open(caminho_saida, 'wb') as f_out:
        #grava o k_max no header para o descompressor saber a ordem usada
        f_out.write(bytes([k_max]))

        escritor = EscritorDeBits(f_out)
        encoder = Encoder(escritor)
        modelo = ModeloPPMC(k_max)

        simbolos_processados = 0
        taxa_anterior = 0.0
        bits_marco_anterior = 0

        def obter_bits_escritos_ate_agora():
            #conta os bytes físicos gravados + os bits pendentes no buffer
            return f_out.tell() * 8 + escritor.bits_no_buffer

        #loop principal de leitura e compressão do arquivo
        while True:
            bloco = f_in.read(4096)
            if not bloco:
                break

            for simbolo in bloco:
                #envia a probabilidade para o conversor
                codificar_simbolo_ppm(simbolo, modelo, encoder)

                #atualiza contexto e probabilidades
                modelo.atualizar_contexto_e_frequencia(simbolo)

                #o gatilho do Reset
                simbolos_processados += 1

                # --- GATILHO DA PODA ---
                # A cada X símbolos processados, chamamos a rotina de limpeza do modelo
                if (opcao == 3) and (simbolos_processados % INTERVALO_PODA == 0):
                    # print(f"  [~] Realizando poda de contextos no byte {simbolos_processados}...")
                    modelo.podar_tabelas()

                if (opcao == 2) and (simbolos_processados % TAMANHO_JANELA == 0):
                    bits_agora = obter_bits_escritos_ate_agora()
                    bits_nesta_janela = bits_agora - bits_marco_anterior
                    taxa_atual = bits_nesta_janela / TAMANHO_JANELA

                    #se a taxa anterior existe e a nova taxa estourou o limite de piora...
                    if taxa_anterior > 0 and (taxa_atual > taxa_anterior * GATILHO_PIORA_TAXA):
                        print(f"  [!] Pico de entropia no byte {simbolos_processados}. Disparando <RESET>...")
                        
                        #reseta o descompressor, as tabelas e a janela de monitoramento
                        codificar_simbolo_ppm(SIMBOLO_RESET, modelo, encoder)
                        modelo.limpar_tabelas()
                        taxa_anterior = 0.0
                        bits_marco_anterior = obter_bits_escritos_ate_agora()
                    else:
                        #senão, atualiza as marcações para a próxima janela
                        taxa_anterior = taxa_atual
                        bits_marco_anterior = bits_agora

        #manda a flag final de EOF e dá o flush para ejetar os últimos bits presos
        codificar_simbolo_ppm(SIMBOLO_EOF, modelo, encoder)
        encoder.finalizar()
        
    tamanho_final = os.path.getsize(caminho_saida)
    print(f"Compressão Concluída! Tamanho final: {tamanho_final} bytes.")