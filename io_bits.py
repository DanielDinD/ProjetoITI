class EscritorDeBits:
    def __init__(self, arquivo):
        self.arquivo = arquivo
        self.buffer = 0          
        self.bits_no_buffer = 0  

    def escrever_bit(self, bit):
        #desloca os bits atuais para a esquerda (<< 1) e insere o novo bit à direita (| bit)
        self.buffer = (self.buffer << 1) | bit
        self.bits_no_buffer += 1

        #quando a caixa encher com 8 bits (1 Byte), despachamos para o arquivo
        if self.bits_no_buffer == 8:
            # Converte o número inteiro para o formato de bytes e escreve
            self.arquivo.write(bytes([self.buffer]))
            # Esvazia a caixa para o próximo byte
            self.buffer = 0
            self.bits_no_buffer = 0

    def flush(self):
        #chamado no final da compressão. Se sobrou algo na caixa que não formou 8 bits,
        #empurramos zeros para a direita até completar 1 byte e gravamos.
        if self.bits_no_buffer > 0:
            self.buffer = self.buffer << (8 - self.bits_no_buffer)
            self.arquivo.write(bytes([self.buffer]))
            self.buffer = 0
            self.bits_no_buffer = 0


class LeitorDeBits:
    def __init__(self, arquivo):
        self.arquivo = arquivo
        self.buffer = 0
        self.bits_no_buffer = 0

    def ler_bit(self):
        #se a nossa caixa está vazia, pegamos o próximo byte (8 bits) do arquivo
        if self.bits_no_buffer == 0:
            byte_lido = self.arquivo.read(1)
            
            #se não tem mais nada para ler, chegamos ao fim do arquivo
            if not byte_lido:
                return None 
                
            self.buffer = ord(byte_lido) #transforma o byte lido em um número inteiro
            self.bits_no_buffer = 8

        #extrai o bit mais à esquerda do nosso buffer
        self.bits_no_buffer -= 1
        bit = (self.buffer >> self.bits_no_buffer) & 1
        return bit