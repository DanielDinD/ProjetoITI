# ==========================================
# 1. ALFABETO E SÍMBOLOS DE CONTROLE
# ==========================================
# Um arquivo binário é composto por bytes, que variam de 0 a 255.
TAMANHO_ALFABETO_BASE = 256 

# Como os bytes de 0 a 255 já representam os dados reais do arquivo,
# precisamos usar números acima de 255 para representar nossas "flags" secretas.
# Assim, o descompressor nunca vai confundir um controle com um dado do arquivo.
SIMBOLO_ESC = 256     # Cai para o contexto menor (Mecanismo de Exclusão)
SIMBOLO_RESET = 257   # Limpa todas as tabelas e reinicia o aprendizado
SIMBOLO_EOF = 258     # Fim do Arquivo (End of File)

# O total de símbolos que o nosso modelo matemático e o codificador aritmético
# precisam conhecer para dividir a "pizza" de probabilidades: 
# (256 bytes + 3 controles = 259 símbolos possíveis)
TOTAL_SIMBOLOS = 259

# ==========================================
# 2. REGRAS DE NEGÓCIO DO PROJETO
# ==========================================
# Parâmetros definidos para a estratégia de adaptação e monitoramento
TAMANHO_JANELA = 1000      # A janela j de observação da taxa local [cite: 10]
GATILHO_PIORA_TAXA = 1.25  # Se o comprimento médio piorar 

# ==========================================
# 3. LIMITES DO CODIFICADOR ARITMÉTICO
# ==========================================
# Trabalharemos com inteiros de 32 bits para a matemática do codificador.
# Isso garante precisão suficiente para as fatias de probabilidade sem 
# estourar a memória (overflow).
PRECISAO_BITS = 32
VALOR_MAXIMO = (1 << PRECISAO_BITS) - 1            # O topo da nossa régua matemática
UM_QUARTO = VALOR_MAXIMO // 4 + 1                  # 25% da régua
MEIO = VALOR_MAXIMO // 2 + 1                       # 50% da régua
TRES_QUARTOS = UM_QUARTO * 3                       # 75% da régua

# ==========================================
# 4. LIMITE DE FREQUÊNCIA (PROTEÇÃO CONTRA OVERFLOW)
# ==========================================
# Se a soma das frequências de um contexto ultrapassar esse limite,
# todas as frequências serão divididas por 2 (rescaling).
LIMITE_FREQUENCIA = 1 << 24