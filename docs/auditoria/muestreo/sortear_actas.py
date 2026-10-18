import argparse
import collections
import csv
import hashlib
import random
import sys
from zipfile import ZipFile

VERSION = "elecciones_es-muestreo-actas-v1"
PINES = {
    "congreso": "e78fc231326a03cf67bbec87b7100ea0c8c46859daa1b2a631c06daaaf1717f8",
    "senado": "f1da7a1d079c663a4163910634a6813f048b932a7de77c64c764fb96ec60b3de",
}
TAMANO_GENERAL = 300
MINIMO_PROVINCIA = 2
TAMANO_H002 = 30
UMBRAL_H002 = 50
INSULARES = ("07", "35", "38")


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def lineas(ruta_zip, nombre):
    with ZipFile(ruta_zip) as z, z.open(nombre) as f:
        for raw in f:
            linea = raw.rstrip(b"\r\n").decode("latin-1")
            if linea:
                yield linea


def clave(r):
    return r[11:13], r[13:16], r[16:18], r[18:22], r[22:23]


def globales(ruta_zip, tipo):
    salida = {}
    for r in lineas(ruta_zip, f"09{tipo}2307.DAT"):
        if r[13:16] == "999":
            continue
        salida[clave(r)] = (int(r[65:72]), int(r[72:79]), int(r[79:86]))
    return salida


def votos_candidatos(ruta_zip):
    suma = collections.Counter()
    for r in lineas(ruta_zip, "10032307.DAT"):
        if r[13:16] != "999":
            suma[clave(r)] += int(r[29:37])
    return suma


def comprobar_pines(zip_congreso, zip_senado):
    for nombre, ruta in (("congreso", zip_congreso), ("senado", zip_senado)):
        obtenido = sha256(ruta)
        if obtenido != PINES[nombre]:
            sys.exit(f"SHA-256 de {nombre} no coincide con el pin: {obtenido}")


def asignar(mesas_por_provincia, total, minimo):
    provincias = sorted(mesas_por_provincia)
    asignacion = {p: minimo for p in provincias}
    resto = total - minimo * len(provincias)
    universo = sum(mesas_por_provincia.values())
    cuotas = {p: resto * mesas_por_provincia[p] / universo for p in provincias}
    for p in provincias:
        asignacion[p] += int(cuotas[p])
    pendientes = total - sum(asignacion.values())
    for p in sorted(provincias, key=lambda p: (-(cuotas[p] - int(cuotas[p])), p))[:pendientes]:
        asignacion[p] += 1
    return asignacion


def marco_h002(congreso, senado, votos):
    marco = set()
    for k, (b, nu, c) in senado.items():
        vc = sum(congreso[k])
        if abs((b + nu + c) - vc) > UMBRAL_H002:
            marco.add(k)
        elif k[0] not in INSULARES:
            maximo = 2 if k[0] in ("51", "52") else 3
            if c and votos[k] > maximo * c:
                marco.add(k)
    return marco


def semilla(commit):
    texto = f"{VERSION}|{PINES['congreso']}|{PINES['senado']}|{commit}"
    return hashlib.sha256(texto.encode()).hexdigest()


def sortear(args):
    if len(args.commit) != 40 or any(c not in "0123456789abcdef" for c in args.commit):
        sys.exit("--commit debe ser un SHA-1 completo de 40 caracteres en minúscula")
    comprobar_pines(args.zip_congreso, args.zip_senado)
    congreso = globales(args.zip_congreso, "02")
    senado = globales(args.zip_senado, "03")
    if set(congreso) != set(senado):
        sys.exit("Las mesas de Congreso y Senado no coinciden")
    s = semilla(args.commit)
    rng = random.Random(int(s, 16))
    por_provincia = collections.defaultdict(list)
    for k in sorted(congreso):
        por_provincia[k[0]].append(k)
    asignacion = asignar({p: len(v) for p, v in por_provincia.items()}, TAMANO_GENERAL, MINIMO_PROVINCIA)
    filas, principal = [], set()
    for p in sorted(por_provincia):
        orden = por_provincia[p][:]
        rng.shuffle(orden)
        n = asignacion[p]
        for i, k in enumerate(orden[:2 * n], 1):
            tipo = "principal" if i <= n else "reserva"
            if tipo == "principal":
                principal.add(k)
            filas.append(("E1_general", p, i, tipo, *k))
    marco = sorted(marco_h002(congreso, senado, votos_candidatos(args.zip_senado)) - principal)
    rng.shuffle(marco)
    for i, k in enumerate(marco[:2 * TAMANO_H002], 1):
        filas.append(("E2_h002", k[0], i, "principal" if i <= TAMANO_H002 else "reserva", *k))
    with open(args.salida, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["estrato", "provincia", "orden", "tipo", "cod_provincia", "cod_municipio", "cod_distrito", "cod_seccion", "cod_mesa"])
        w.writerows(filas)
    print(f"semilla={s}")
    print(f"marco_general={len(congreso)} marco_h002={len(marco)} filas={len(filas)}")


def mostrar_asignacion(args):
    comprobar_pines(args.zip_congreso, args.zip_senado)
    congreso = globales(args.zip_congreso, "02")
    senado = globales(args.zip_senado, "03")
    conteo = collections.Counter(k[0] for k in congreso)
    a = asignar(conteo, TAMANO_GENERAL, MINIMO_PROVINCIA)
    marco = marco_h002(congreso, senado, votos_candidatos(args.zip_senado))
    for p in sorted(a):
        print(f"{p},{conteo[p]},{a[p]}")
    print(f"total,{sum(conteo.values())},{sum(a.values())}")
    print(f"marco_h002,{len(marco)}")


def binomial_cdf(k, n, p):
    return sum(_comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def _comb(n, k):
    r = 1
    for i in range(1, k + 1):
        r = r * (n - k + i) // i
    return r


def _buscar(f, objetivo, creciente):
    bajo, alto = 0.0, 1.0
    for _ in range(100):
        medio = (bajo + alto) / 2
        if (f(medio) < objetivo) == creciente:
            bajo = medio
        else:
            alto = medio
    return (bajo + alto) / 2


def intervalo(args):
    n, k, alfa = args.n, args.k, 1 - args.confianza
    if not 0 <= k <= n:
        sys.exit("Se requiere 0 <= k <= n")
    inferior = 0.0 if k == 0 else _buscar(lambda p: 1 - binomial_cdf(k - 1, n, p), alfa / 2, True)
    superior = 1.0 if k == n else _buscar(lambda p: binomial_cdf(k, n, p), alfa / 2, False)
    print(f"n={n} k={k} proporcion={k / n:.4f} ic{int(args.confianza * 100)}=[{inferior:.4f}, {superior:.4f}]")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="orden", required=True)
    for nombre in ("asignacion", "sortear"):
        p = sub.add_parser(nombre)
        p.add_argument("--zip-congreso", required=True)
        p.add_argument("--zip-senado", required=True)
        if nombre == "sortear":
            p.add_argument("--commit", required=True)
            p.add_argument("--salida", required=True)
    p = sub.add_parser("intervalo")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--k", type=int, required=True)
    p.add_argument("--confianza", type=float, default=0.95)
    a = ap.parse_args()
    {"asignacion": mostrar_asignacion, "sortear": sortear, "intervalo": intervalo}[a.orden](a)


if __name__ == "__main__":
    main()
