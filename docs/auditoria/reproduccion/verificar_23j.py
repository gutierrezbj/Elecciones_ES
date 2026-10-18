import argparse
import collections
import re
from pathlib import Path


def leer(ruta):
    with open(ruta, encoding="latin-1") as f:
        return [l.rstrip("\r\n") for l in f if l.strip()]


def n(r, a, b):
    return int(r[a - 1:b])


def es_cera(r):
    return r[13:16] == "999"


def es_total_cera(r):
    return es_cera(r) and (r[9:11] == "99" or r[11:13] == "99")


def es_cera_insular_duplicado(r, tipo):
    return tipo == "03" and es_cera(r) and r[11:13] in ("07", "35", "38") and r[16:18] == "09"


def globales_mesa(r):
    return n(r, 31, 37), n(r, 66, 72), n(r, 73, 79), n(r, 80, 86)


def controles_mesa(filas, tipo):
    mesas = [r for r in filas if not es_cera(r)]
    claves = collections.Counter(r[11:23] for r in mesas)
    cera = [r for r in filas if es_cera(r)]
    oficiales = collections.Counter(r[100:101] for r in filas)
    exceso, iguales, cero, pequenas = [], 0, 0, 0
    for r in mesas:
        censo, b, nu, c = globales_mesa(r)
        v = b + nu + c
        if v > censo:
            exceso.append((r[11:23], n(r, 24, 30), censo, v))
        elif v == censo:
            iguales += 1
        if v == 0:
            cero += 1
        if censo < 50:
            pequenas += 1
    print(f"[{tipo}] registros={len(filas)} mesas={len(mesas)} cera={len(cera)} "
          f"municipios={len({r[11:16] for r in mesas})} provincias={len({r[11:13] for r in mesas})} "
          f"claves_duplicadas={sum(1 for v in claves.values() if v > 1)} datos_oficiales={dict(oficiales)}")
    print(f"[{tipo}] votantes>censo={len(exceso)} votantes==censo={iguales} votantes==0={cero} censo<50={pequenas}")
    for e in exceso:
        print(f"[{tipo}]   exceso mesa={e[0]} censo_ine={e[1]} censo_escrutinio={e[2]} votantes={e[3]}")
    sin_filtro = sum(globales_mesa(r)[0] for r in cera)
    con_filtro = sum(globales_mesa(r)[0] for r in cera if not es_total_cera(r) and not es_cera_insular_duplicado(r, tipo))
    print(f"[{tipo}] censo_cera_sumando_todo={sin_filtro} censo_cera_filtrado={con_filtro}")


def mesas_vs_municipios(d, tipo):
    m5 = {}
    for r in leer(d / f"05{tipo}2307.DAT"):
        if r[16:18] == "99":
            m5[r[11:16]] = (n(r, 137, 141), n(r, 150, 157), n(r, 190, 197), n(r, 198, 205), n(r, 206, 213))
    m9 = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
    for r in leer(d / f"09{tipo}2307.DAT"):
        if es_cera(r):
            continue
        t = m9[r[11:16]]
        censo, b, nu, c = globales_mesa(r)
        t[0] += 1
        t[1] += censo
        t[2] += b
        t[3] += nu
        t[4] += c
    dif = [k for k in set(m5) | set(m9) if tuple(m9.get(k, ())) != m5.get(k)]
    print(f"[{tipo}] municipios 05 vs suma 09: {len(m5)} municipios, {len(dif)} con diferencias {sorted(dif)[:10]}")


def mesas_vs_provincias(d, tipo):
    suma = collections.defaultdict(lambda: [0, 0, 0, 0])
    for r in leer(d / f"09{tipo}2307.DAT"):
        if es_total_cera(r) or es_cera_insular_duplicado(r, tipo):
            continue
        t = suma[r[11:13]]
        for i, x in enumerate(globales_mesa(r)):
            t[i] += x
    oficial = {}
    for r in leer(d / f"07{tipo}2307.DAT"):
        if r[11:13] != "99" and r[13] == "9":
            oficial[r[11:13]] = (r[14:64].strip(), [n(r, 86, 93), n(r, 126, 133), n(r, 134, 141), n(r, 142, 149)])
    dif = 0
    for p, (nombre, o) in sorted(oficial.items()):
        dd = [suma[p][i] - o[i] for i in range(4)]
        if any(dd):
            dif += 1
            print(f"[{tipo}]   provincia={p} {nombre} dif(censo,blancos,nulos,candidaturas)={dd}")
    print(f"[{tipo}] suma 09 vs 07 provincial: {len(oficial)} provincias, {dif} con diferencias")
    return oficial


def candidaturas_vs_provincia(d, tipo, provincia):
    siglas = {r[8:14]: r[14:64].strip() for r in leer(d / f"03{tipo}2307.DAT")}
    s = collections.Counter()
    for r in leer(d / f"10{tipo}2307.DAT"):
        if r[11:13] == provincia and not es_total_cera(r):
            s[r[23:29]] += int(r[29:37])
    o = {r[14:20]: int(r[20:28]) for r in leer(d / f"08{tipo}2307.DAT") if r[11:13] == provincia and r[13] == "9"}
    for k in sorted(set(s) | set(o)):
        if s[k] != o.get(k, 0):
            print(f"[{tipo}]   provincia={provincia} {siglas.get(k, k)} mesas={s[k]} provincial={o.get(k, 0)} dif={s[k] - o.get(k, 0):+}")


def provincial_vs_boe(oficial, boe):
    texto = Path(boe).read_text(encoding="utf-8").split("Total estatal")[0]
    filas = {}
    for l in texto.splitlines():
        m = re.match(r"\s+(\S.*?\S)\s{2,}([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$", l)
        if m:
            v = [int(x.replace(".", "")) for x in m.groups()[1:]]
            filas[v[0]] = (m.group(1), [v[0], v[4], v[5], v[3]])
    dif = 0
    for p, (nombre, o) in sorted(oficial.items()):
        b = filas.get(o[0])
        if not b or b[1] != o:
            dif += 1
            print(f"[02]   provincia={p} {nombre} 07={o} boe={b}")
    print(f"[02] 07 provincial vs BOE Cuadro I: {len(filas)} filas BOE, {dif} con diferencias")


def votantes_por_mesa(d, tipo):
    salida = {}
    for r in leer(d / f"09{tipo}2307.DAT"):
        if not es_cera(r):
            _, b, nu, c = globales_mesa(r)
            salida[r[11:23]] = b + nu + c
    return salida


def senado_vs_congreso(dc, ds):
    c, s = votantes_por_mesa(dc, "02"), votantes_por_mesa(ds, "03")
    tramos = collections.Counter()
    for k in c:
        d = abs(s.get(k, 0) - c[k])
        tramos["0" if d == 0 else "1-2" if d <= 2 else "3-10" if d <= 10 else "11-50" if d <= 50 else ">50"] += 1
    print(f"[02/03] |votantes Senado - votantes Congreso| por mesa: {dict(sorted(tramos.items()))}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("congreso", type=Path)
    ap.add_argument("senado", type=Path)
    ap.add_argument("--boe-txt")
    a = ap.parse_args()
    for d, tipo in ((a.congreso, "02"), (a.senado, "03")):
        controles_mesa(leer(d / f"09{tipo}2307.DAT"), tipo)
        mesas_vs_municipios(d, tipo)
        oficial = mesas_vs_provincias(d, tipo)
        if tipo == "02":
            for p in ("39", "45"):
                candidaturas_vs_provincia(d, tipo, p)
            if a.boe_txt:
                provincial_vs_boe(oficial, a.boe_txt)
    senado_vs_congreso(a.congreso, a.senado)
    candidaturas_vs_globales(a.congreso, "02")
    papeletas_senado(a.senado)
    if a.boe_txt:
        senado_candidatos_vs_boe(a.senado, a.boe_txt)


def candidaturas_vs_globales(d, tipo):
    globales = {r[9:23]: n(r, 80, 86) for r in leer(d / f"09{tipo}2307.DAT")}
    suma = collections.Counter()
    for r in leer(d / f"10{tipo}2307.DAT"):
        suma[r[9:23]] += int(r[29:37])
    dif = sum(1 for k, v in globales.items() if suma.get(k) != v)
    print(f"[{tipo}] suma de candidaturas (10) vs votos a candidaturas (09): {len(globales)} registros, {dif} con diferencias")


def papeletas_senado(d):
    votos = collections.Counter()
    for r in leer(d / "10032307.DAT"):
        if not es_cera(r):
            votos[r[11:23]] += int(r[29:37])
    imposibles = 0
    for r in leer(d / "09032307.DAT"):
        if es_cera(r) or r[11:13] in ("07", "35", "38"):
            continue
        maximo = 2 if r[11:13] in ("51", "52") else 3
        papeletas = n(r, 80, 86)
        if papeletas and votos[r[11:23]] > maximo * papeletas:
            imposibles += 1
    print(f"[03] mesas peninsulares con más votos a candidatos que el máximo legal por papeleta (art. 96.3): {imposibles}")


def senado_candidatos_vs_boe(d, boe):
    texto = Path(boe).read_text(encoding="utf-8")
    texto = texto[texto.find("Relación de Senadores proclamados electos"):]
    boe_votos = collections.Counter()
    for l in texto.splitlines():
        m = re.match(r"^\s*(Don|Doña)\s.*\s([\d.]+)\s*$", l)
        if m:
            boe_votos[int(m.group(2).replace(".", ""))] += 1
    interior = collections.Counter()
    for r in leer(d / "08032307.DAT"):
        if r[11:13] == "99" or (r[13] == "9" and r[11:13] in ("07", "35", "38")):
            continue
        interior[int(r[20:28])] += 1
    print(f"[03] votos por candidato BOE vs Interior: {sum(boe_votos.values())} y {sum(interior.values())} candidatos; "
          f"solo BOE={sorted((boe_votos - interior).elements())} solo Interior={sorted((interior - boe_votos).elements())}")


if __name__ == "__main__":
    main()
