import argparse
import time
import os
from compressor import comprimir_arquivo
from descompressor import descomprimir_arquivo


def main():
    print("="*50)
    print(" Compressor e Descompressor PPM-C (Projeto ITI) ")
    print("="*50)

    while True:
        # Menu de opções
        print("\nEscolha a ação desejada:")
        print("1 - Comprimir")
        print("2 - Descomprimir")
        print("0 - Sair")
        
        opcao = input("Digite o número da opção: ").strip()
        
        if opcao == '0':
            print("\nEncerrando o programa...")
            break
        elif opcao not in ['1', '2']:
            print("\nErro: Opção inválida! Tente novamente.")
            continue
            
        acao = "comprimir" if opcao == '1' else "descomprimir"
        
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
            comprimir_arquivo(entrada, saida, kmax)
            pass 
        elif acao == "descomprimir":
            descomprimir_arquivo(entrada, saida, kmax) # Descomente sua função
            pass

        tempo_fim = time.time()
        tempo_total = tempo_fim - tempo_inicio
        
        print("-" * 50)
        print(f"Operação finalizada com sucesso em {tempo_total:.2f} segundos.")
        print("=" * 50)

if __name__ == "__main__":
    main()