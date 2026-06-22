from constantes import SIMBOLO_ESC

#codifica um símbolo usando o modelo PPM-C com mecanismo de exclusão
def codificar_simbolo_ppm(simbolo_alvo, modelo, encoder):
    contexto_busca = modelo.contexto_atual
    excluidos = set()

    while True:
        resultado = modelo.obter_intervalo(simbolo_alvo, contexto_busca, excluidos)

        if resultado is not None:
            low, high, total = resultado
            encoder.codificar(low, high, total)
            break

        resultado_esc = modelo.obter_intervalo(SIMBOLO_ESC, contexto_busca, excluidos)

        if resultado_esc is not None:
            low_esc, high_esc, total_esc = resultado_esc
            encoder.codificar(low_esc, high_esc, total_esc)
            excluidos.update(modelo.tabelas[contexto_busca].keys())

        if len(contexto_busca) > 0:
            contexto_busca = contexto_busca[1:]
        else:
            contexto_busca = (-1,)
