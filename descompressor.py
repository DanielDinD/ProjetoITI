import os
from constantes import (
    SIMBOLO_ESC, SIMBOLO_RESET, SIMBOLO_EOF
)
from io_bits import LeitorDeBits
from codificador_aritmetico import Decoder
from modelo_ppm import ModeloPPMC

def descomprimir_arquivo(caminho_entrada, caminho_saida, k_max):
    print(f"Iniciando descompressão: {caminho_entrada} (Kmax: {k_max})")

    with open(caminho_entrada, 'rb') as f_in, open(caminho_saida, 'wb') as f_out:
        #lê o k_max armazenado no header do arquivo comprimido
        k_max_header = ord(f_in.read(1))
        if k_max_header != k_max:
            print(f"  [Info] Usando K_max={k_max_header} do header (ignorando K_max={k_max} informado)")
        k_max = k_max_header

        leitor = LeitorDeBits(f_in)
        decoder = Decoder(leitor)
        modelo = ModeloPPMC(k_max)

        #Reconstrói a pizza de probabilidades, atira o dardo
        #para descobrir o símbolo e lida com os loops de <ESC> internamente
        def decodificar_simbolo():
            contexto_busca = modelo.contexto_atual
            excluidos = set()

            while True:
                #se o contexto não existe, desce para o nível inferior
                if contexto_busca not in modelo.tabelas:
                    if len(contexto_busca) > 0:
                        contexto_busca = contexto_busca[1:]
                    else:
                        contexto_busca = (-1,)
                    continue

                frequencias_neste_contexto = modelo.tabelas[contexto_busca]
                
                #aplica o Mecanismo de Exclusão idêntico ao do compressor
                simbolos_validos = [s for s in frequencias_neste_contexto.keys() if s not in excluidos]
                #na ordem -1, não há escape (todos os símbolos já existem)
                freq_escape = 0 if contexto_busca == (-1,) else len(simbolos_validos)

                #se todos os símbolos foram excluídos, desce sem ler bits (espelho do obter_intervalo)
                if not simbolos_validos and contexto_busca != (-1,):
                    if len(contexto_busca) > 0:
                        contexto_busca = contexto_busca[1:]
                    else:
                        contexto_busca = (-1,)
                    continue

                #reconstrói o "Total" da pizza
                total = freq_escape
                for s in simbolos_validos:
                    total += frequencias_neste_contexto[s]
                
                #verifica qual fatia foi atingida, obtendo o símbolo alvo
                alvo = decoder.obter_frequencia_alvo(total)
                
                #varre as fatias para encontrar a dona do "alvo"
                low = 0
                simbolo_encontrado = SIMBOLO_ESC
                peso_encontrado = freq_escape
                
                for s in sorted(simbolos_validos):
                    peso = frequencias_neste_contexto[s]
                    if low + peso > alvo:
                        simbolo_encontrado = s
                        peso_encontrado = peso
                        break
                    low += peso
                
                #se o dardo acertou a fatia do <ESC>
                if simbolo_encontrado == SIMBOLO_ESC:
                    low_esc = total - freq_escape
                    decoder.remover_frequencia_alvo(low_esc, total, total)
                    
                    #adiciona à lista de exclusão e desce a Ordem do K
                    excluidos.update(simbolos_validos)
                    if len(contexto_busca) > 0:
                        contexto_busca = contexto_busca[1:]
                    else:
                        contexto_busca = (-1,)
                else:
                    #acertou um símbolo real (Byte, RESET ou EOF)!
                    high = low + peso_encontrado
                    decoder.remover_frequencia_alvo(low, high, total)
                    return simbolo_encontrado

        #loop principal de descompressão
        while True:
            #descobre qual é o símbolo atual
            simbolo = decodificar_simbolo()

            if simbolo == SIMBOLO_EOF:
                #fim do arquivo, encerra o loop
                break
                
            elif simbolo == SIMBOLO_RESET:
                #a taxa lá no compressor estourou, limpa o modelo para não piorar mais a compressão
                print("  [!] Flag <RESET> detectada. Limpando tabelas...")
                modelo.limpar_tabelas()
                
            else:
                #escreve o byte descomprimido no arquivo de saída
                f_out.write(bytes([simbolo]))
                
                #atualiza o contexto e as frequências para aprender
                modelo.atualizar_contexto_e_frequencia(simbolo)

    print(f"Descompressão Concluída! Salvo em: {caminho_saida}")