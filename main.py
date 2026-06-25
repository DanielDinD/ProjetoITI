import argparse
import time
import os
from compressor import comprimir_arquivo
from descompressor import descomprimir_arquivo
import filecmp


def main():
    opcao = 2
    print("="*50)
    print(" Compressor e Descompressor PPM-C (Projeto ITI) ")
    print("="*50)

    while True:
        # Menu de opções
        print("\nEscolha a ação desejada:")
        print("1 - Comprimir")
        print("2 - Descomprimir")
        print("4 - Comparar Arquivos")
        print("0 - Sair")
        
        opcao = input("Digite o número da opção: ").strip()
        
        if opcao == '0':
            print("\nEncerrando o programa...")
            break
        elif opcao not in ['1', '2', '4']:
            print("\nErro: Opção inválida! Tente novamente.")
            continue

        # Comparação binária entre os arquivos    
        if opcao == '4':
            # Leitura e validação da entrada
            arquivo1 = input("\nCaminho do primeiro arquivo a ser comparado (ex: dados/arquivo.txt): ").strip()
            if not os.path.exists(arquivo1):
                print(f"Erro: O arquivo de entrada '{arquivo1}' não foi encontrado!")
                continue
            arquivo2 = input("Caminho do segundo arquivo (ex: dados/arquivo.txt): ").strip()
            if not os.path.exists(arquivo2):
                print(f"Erro: O arquivo de entrada '{arquivo2}' não foi encontrado!")
                continue
            if(filecmp.cmp(arquivo1, arquivo2, False)):
                print("Todos os bits dos arquivos são iguais.")
                continue
            else:
                print("Há alguma diferença entre os arquivos!")
                continue

        acao = "comprimir" if opcao == '1' else "descomprimir"

        # Menu de opções
        print("\nEscolha o modo desejado:")
        print("1 - Sem reset e sem poda")
        print("2 - Com reset")
        print("3 - Com poda")
        opcao = input("Digite a opção desejada: ").strip()

        if opcao == 1:
            modo = 1
        elif opcao == 2:
            modo = 2
        else:
            modo = 3
        
        # Leitura e validação da entrada
        entrada = input("\nCaminho do arquivo de entrada (ex: dados/arquivo.txt): ").strip()
        if not os.path.exists(entrada):
            print(f"Erro: O arquivo de entrada '{entrada}' não foi encontrado!")
            continue
            
        # Leitura da saída
        saida = input("Caminho do arquivo de saída (ex: saidas/arquivo.bin): ").strip()
        
        # Leitura do kmax com valor padrão
        kmax_input = input("Ordem máxima do contexto PPM-C [Pressione ENTER para o Padrão: 3]: ").strip()
        kmax = int(kmax_input) if kmax_input.isdigit() else 3

        # Início da execução
        print("\n" + "="*50)
        print(f"Iniciando operação de {acao.upper()}...")
        print(f"Ordem do Modelo (K_max): {kmax}")
        print("="*50)

        # Inicia o cronômetro para medir o tempo de execução
        tempo_inicio = time.time()

        # Redireciona para o orquestrador correto
        if acao == "comprimir":
            comprimir_arquivo(entrada, saida, kmax, modo)
            pass 
        elif acao == "descomprimir":
            descomprimir_arquivo(entrada, saida, kmax, modo)
            pass

        tempo_fim = time.time()
        tempo_total = tempo_fim - tempo_inicio
        
        print("-" * 50)
        print(f"Operação finalizada com sucesso em {tempo_total:.2f} segundos.")
        print("=" * 50)

if __name__ == "__main__":
    main()
