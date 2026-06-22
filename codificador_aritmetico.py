from constantes import VALOR_MAXIMO, UM_QUARTO, MEIO, TRES_QUARTOS

class Encoder:
    def __init__(self, escritor_bits):
        self.escritor = escritor_bits
        self.low = 0
        self.high = VALOR_MAXIMO
        self.underflow_bits = 0  #contador de bits que estão "presos" no meio da régua

    def codificar(self, low_count, high_count, total):
        #calcula o tamanho atual da régua
        range_atual = self.high - self.low + 1
        
        #dá o "zoom" ajustando o novo High e o novo Low baseados na fatia do PPM-C
        self.high = self.low + (range_atual * high_count) // total - 1
        self.low = self.low + (range_atual * low_count) // total
        
        #renormalização: checa se já podemos ejetar bits para o arquivo
        self._renormalizar()

    def _renormalizar(self):
        while True:
            if self.high < MEIO:
                #o intervalo inteiro está na metade inferior (começa com 0)
                self._escrever_bit_e_underflow(0)
            elif self.low >= MEIO:
                #o intervalo inteiro está na metade superior (começa com 1)
                self._escrever_bit_e_underflow(1)
                self.low -= MEIO
                self.high -= MEIO
            elif self.low >= UM_QUARTO and self.high < TRES_QUARTOS:
                #o intervalo está estrangulado no meio (Underflow / E2 condition)
                self.underflow_bits += 1
                self.low -= UM_QUARTO
                self.high -= UM_QUARTO
            else:
                #o intervalo ainda está largo, precisamos ler o próximo símbolo
                break
            
            #desloca 1 bit para a esquerda, esticando a régua novamente
            self.low = (self.low << 1)
            self.high = (self.high << 1) + 1

    def _escrever_bit_e_underflow(self, bit):
        self.escritor.escrever_bit(bit)
        #se tínhamos bits presos no underflow, ejetamos o inverso do bit atual
        while self.underflow_bits > 0:
            self.escritor.escrever_bit(1 - bit)
            self.underflow_bits -= 1

    def finalizar(self):
        #no fim do arquivo, ejeta o último bit preso e dá o comando de flush no IO
        self.underflow_bits += 1
        if self.low < UM_QUARTO:
            self._escrever_bit_e_underflow(0)
        else:
            self._escrever_bit_e_underflow(1)
        self.escritor.flush()


class Decoder:
    def __init__(self, leitor_bits):
        self.leitor = leitor_bits
        self.low = 0
        self.high = VALOR_MAXIMO
        self.value = 0
        self._inicializar_valor()

    def _inicializar_valor(self):
        #preenche a variável "value" sugando os primeiros 32 bits do arquivo
        for _ in range(32):
            bit = self.leitor.ler_bit()
            if bit is None:
                bit = 0 #fim do arquivo virtual
            self.value = (self.value << 1) | bit

    def obter_frequencia_alvo(self, total):
        range_atual = self.high - self.low + 1
        return ((self.value - self.low + 1) * total - 1) // range_atual

    def remover_frequencia_alvo(self, low_count, high_count, total):
        #após o PPM-C descobrir o símbolo, o Decoder foca a régua nessa fatia exata
        range_atual = self.high - self.low + 1
        self.high = self.low + (range_atual * high_count) // total - 1
        self.low = self.low + (range_atual * low_count) // total
        self._renormalizar()

    def _renormalizar(self):
        while True:
            if self.high < MEIO:
                pass #começa com 0, não faz nada com value
            elif self.low >= MEIO:
                self.low -= MEIO
                self.high -= MEIO
                self.value -= MEIO
            elif self.low >= UM_QUARTO and self.high < TRES_QUARTOS:
                self.low -= UM_QUARTO
                self.high -= UM_QUARTO
                self.value -= UM_QUARTO
            else:
                break
                
            self.low = (self.low << 1)
            self.high = (self.high << 1) + 1
            
            #puxa o próximo bit do arquivo para repor o Valor
            bit = self.leitor.ler_bit()
            if bit is None:
                bit = 0
            self.value = (self.value << 1) | bit