def gerar_bracket_duplas(ranking, pontos_por_rodada):

    times = ranking[:]
    fases = []

    fase_atual = times
    rodada_index = 0

    while len(fase_atual) > 1:

        confrontos = []
        vencedores = []

        total = len(fase_atual)

        # pegar pontos da rodada (se existir)
        rodada_pontos = []
        if rodada_index < len(pontos_por_rodada):
            rodada_pontos = pontos_por_rodada[rodada_index]

        mapa_pontos = {r[0]: r[2] for r in rodada_pontos}

        for i in range(total // 2):

            a = fase_atual[i]
            b = fase_atual[total - 1 - i]

            pa = mapa_pontos.get(a[0])
            pb = mapa_pontos.get(b[0])

            if pa is None or pb is None:
                vencedor = None
            else:
                vencedor = a if pa >= pb else b

            confrontos.append({
                "ordem": i + 1,
                "a": a,
                "b": b,
                "pa": pa,
                "pb": pb,
                "vencedor": vencedor
            })

            if vencedor:
                vencedores.append(vencedor)

        fases.append(confrontos)

        if not vencedores:
            break

        fase_atual = vencedores
        rodada_index += 1

    campeao = fase_atual[0] if len(fase_atual) == 1 else None

    return fases, campeao