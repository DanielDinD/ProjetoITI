from constantes import SIMBOLO_ESC, TOTAL_SIMBOLOS, LIMITE_FREQUENCIA

class ModeloPPMC:
    def __init__(self, k_max):
        self.k_max = k_max
        self.tabelas = {}          
        self.totais = {}           
        self.contexto_atual = ()   
        self.limpar_tabelas()      

    #executa a limpeza total das tabelas de frequências para reiniciar o aprendizado do modelo
    def limpar_tabelas(self):
        self.tabelas.clear()
        self.totais.clear()
        self.contexto_atual = ()
        
        #k = -1, é a ordem mais baixa, onde todos os símbolos são equiprováveis(freq = 1) e não há escape (freq_escape = 0)
        self.tabelas[(-1,)] = {s: 1 for s in range(TOTAL_SIMBOLOS)}
        self.totais[(-1,)] = TOTAL_SIMBOLOS

    #Adiciona +1 na frequência do símbolo lido para o contexto atual e para todos os subcontextos
    def atualizar_contexto_e_frequencia(self, simbolo):
        #atualiza as frequências em todos os níveis de K até 0
        tamanho_contexto = len(self.contexto_atual)
        for i in range(tamanho_contexto + 1):
            #pega um pedaço do contexto (do final para o começo)
            sub_contexto = self.contexto_atual[i:] 
            
            if sub_contexto not in self.tabelas:
                self.tabelas[sub_contexto] = {}
                self.totais[sub_contexto] = 0
                
            if simbolo not in self.tabelas[sub_contexto]:
                self.tabelas[sub_contexto][simbolo] = 0
                
            self.tabelas[sub_contexto][simbolo] += 1
            self.totais[sub_contexto] += 1

            #rescaling: se o total estourou o limite seguro, divide tudo por 2
            if self.totais[sub_contexto] > LIMITE_FREQUENCIA:
                self._rescalar(sub_contexto)

        #desliza a janela do contexto atual
        novo_contexto = list(self.contexto_atual) + [simbolo]
        #se passamos do limite K_max, jogamos fora o caractere mais antigo (o primeiro)
        if len(novo_contexto) > self.k_max:
            novo_contexto = novo_contexto[1:]
            
        self.contexto_atual = tuple(novo_contexto)

    #divide todas as frequências de um contexto por 2, removendo as que zerarem
    def _rescalar(self, contexto):
        tabela = self.tabelas[contexto]
        novo_total = 0
        remover = []
        for s in tabela:
            tabela[s] >>= 1
            if tabela[s] == 0:
                remover.append(s)
            else:
                novo_total += tabela[s]
        for s in remover:
            del tabela[s]
        self.totais[contexto] = novo_total

    #retorna (low, high, total) ou None se o símbolo não existir no contexto
    #aplicando o mecanismo de exclusão
    def obter_intervalo(self, simbolo_alvo, contexto_busca, excluidos):
        #se o contexto não existe na tabela, não temos como calcular
        if contexto_busca not in self.tabelas:
            return None
            
        frequencias_neste_contexto = self.tabelas[contexto_busca]
        
        #a frequência do <ESC> é igual ao número de símbolos ÚNICOS existentes no contexto
        simbolos_validos = [s for s in frequencias_neste_contexto.keys() if s not in excluidos]
        
        if not simbolos_validos and contexto_busca != (-1,):
            return None #contexto vazio após exclusão

        #na ordem -1, não há escape (todos os símbolos já existem)
        freq_escape = 0 if contexto_busca == (-1,) else len(simbolos_validos)
        
        low = 0
        high = 0
        total = freq_escape #o total já começa valendo o peso do Escape
        alvo_encontrado = False

        for s in sorted(simbolos_validos):
            peso = frequencias_neste_contexto[s]
            total += peso
            
            if s == simbolo_alvo:
                high = low + peso
                alvo_encontrado = True
            elif not alvo_encontrado:
                #se ainda não achamos o alvo, o peso desse símbolo soma no piso (Low)
                low += peso
                
        #se estamos procurando especificamente o <ESC>
        if simbolo_alvo == SIMBOLO_ESC:
            if freq_escape == 0:
                return None  #não há escape na ordem -1
            #o escape sempre fica no topo do intervalo
            low_esc = total - freq_escape
            return (low_esc, total, total)
            
        if alvo_encontrado:
            return (low, high, total)
            
        return None
    
    def podar_tabelas(self):
        """
        Reduz pela metade a frequência de todos os símbolos.
        Se a frequência chegar a zero, o símbolo é eliminado.
        Se um contexto ficar vazio após a eliminação, ele também é removido.
        """
        contextos_para_remover = []

        for contexto, frequencias in self.tabelas.items():
            # O contexto -1 (alfabeto base) geralmente nunca é podado para garantir o fallback
            if contexto == (-1,):
                continue
                
            simbolos_para_remover = []
            
            for simbolo in frequencias:
                # Divide a frequência pela metade (inteira)
                frequencias[simbolo] //= 2
                
                # Se zerou, marcamos para eliminação
                if frequencias[simbolo] == 0:
                    simbolos_para_remover.append(simbolo)
            
            # Remove os símbolos zerados do dicionário
            for simbolo in simbolos_para_remover:
                del frequencias[simbolo]
                
            # Se o contexto ficou sem nenhum símbolo, marcamos para remover o contexto inteiro
            if len(frequencias) == 0:
                contextos_para_remover.append(contexto)
                
        # Remove os contextos que ficaram vazios
        for contexto in contextos_para_remover:
            del self.tabelas[contexto]