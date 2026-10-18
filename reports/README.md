# Ejecución verificable del hito 1 — 18 de octubre de 2026

Se ejecutaron las 42 pruebas sintéticas, se recuperaron de nuevo los tres recursos oficiales con los SHA-256 fijados y se procesó **Soria primero y el país después**. Ambos informes registran el código `33073c17cc19066c102188a27083d1e7a3164726`, sin modificaciones locales (`code_dirty=false`). El commit posterior solo añade esta evidencia de ejecución.

Origen de los datos: Ministerio del Interior. Elaboración propia con datos extraídos del sitio web del INE para los denominadores. No hay patrocinio de los organismos.

| Ámbito | Municipios observados / INE, por cámara | Mesas físicas observadas / INE, por cámara | CERA provincial, por cámara | Observaciones técnicas |
|---|---:|---:|---:|---:|
| Soria (42) | 183 / 183 | 256 / 256 | 1, fuera del denominador de mesas | 0 |
| Nacional, 52 provincias/ciudades autónomas | 8.131 / 8.131 | 60.314 / 60.314 | 52, fuera del denominador de mesas | 96 |

Los denominadores proceden de la tabla INE 59781. No se han encontrado diferencias de **cardinalidad** en ninguna provincia/cámara. No existe aquí una lista independiente de IDs del INE: igualdad de conteos no demuestra por sí sola identidad de conjuntos, y los IDs concretos ausentes no se pueden determinar. Los campos `missing_keys`/`unexpected_keys` son null.

Soria produce 7.453 resultados de candidatura/candidato, 514 registros de mesa/CERA entre ambas cámaras y 2 agregados provinciales. Sus sumas físicas + CERA concilian con 07. El país produce 1.986.144 resultados, 120.732 registros de mesa/CERA y 104 agregados provinciales. Los resultados de Congreso y Senado permanecen separados.

## Observaciones pendientes

| Regla | Congreso | Senado | Total | Interpretación permitida |
|---|---:|---:|---:|---|
| voters_exceed_electors | 4 | 57 | 61 | Votantes derivados de los componentes publicados mayores que censo de escrutinio publicado; revisar datos, definición y actas |
| published_total_mismatch | 9 | 0 | 9 | Diferencias por campo entre suma de 09 (mesas + CERA) y 07 del mismo ZIP |
| candidate_votes_exceed_ballots | 0 | 26 | 26 | Votos de un candidato superiores a papeletas a candidaturas del registro 09 correspondiente; no se suman marcas entre candidatos |

Son **96 observaciones de reglas, no 96 mesas distintas ni irregularidades confirmadas**. Se mantienen en `detected`, severidad `technical_review`, con revisor null. No se atribuye fraude, error confirmado o explicación causal. Los 26 registros de la última regla pueden compartir mesa. Deben revisarse también definiciones, transcripción y calidad del adaptador antes de cualquier conclusión.

Las diferencias provinciales están en Congreso:

| Provincia | Campo | Suma 09 física + CERA | Publicado 07 | Diferencia |
|---|---|---:|---:|---:|
| Cantabria (39) | votantes derivados | 355.161 | 355.145 | +16 |
| Cantabria (39) | válidos derivados | 350.154 | 350.150 | +4 |
| Cantabria (39) | blancos | 3.266 | 3.262 | +4 |
| Cantabria (39) | nulos | 5.007 | 4.995 | +12 |
| Toledo (45) | votantes derivados | 393.178 | 392.988 | +190 |
| Toledo (45) | válidos derivados | 387.380 | 387.200 | +180 |
| Toledo (45) | blancos | 2.616 | 2.611 | +5 |
| Toledo (45) | nulos | 5.798 | 5.788 | +10 |
| Toledo (45) | papeletas a candidaturas | 384.764 | 384.589 | +175 |

Votantes y válidos se calculan con los componentes del formato, no son dos medidas independientes adicionales. En Congreso concilian los seis campos de 50 de las 52 provincias; en Senado concilian los de las 52. Esta conciliación interna no reemplaza el cotejo con actas o BOE.

## Evidencia y reproducción

- [Soria: informe completo](soria.json), [hashes de sus salidas](soria-artifacts.json).
- [Nacional: informe completo](national.json), [hashes de sus salidas](national-artifacts.json).
- [Observaciones en CSV](findings.csv): IDs, claves, valores y ubicaciones de fuente.
- [Manifest de la reproducción](../data/downloads/reproduction-20261018.jsonl): tres HTTPS 200, hashes exigidos y comprobados, fechas, bytes y metadatos.
- [Manifest exploratorio](../data/downloads/manifest.jsonl): incluye el inventario y errores TLS de los XLSX, que no se usan en la normalización.
- [Instrucciones para reproducir](../docs/REPRODUCIR.md) y [esquema/posiciones](../docs/ESQUEMA.md).

Los tres SHA-256 fijados están en [checksums.json](../data/sources/checksums.json). En esta reproducción los ZIP informaron Last-Modified 27/12/2023 10:30:54 GMT; los mismos bytes en una respuesta anterior informaron 10:30:01 GMT. Se conserva cada valor de servidor sin usarlo como identidad de versión; la identidad se fija por hash. Fecha de publicación de ZIP no establecida.

Los informes y manifiestos pequeños se versionan. ZIP, documentos de candidaturas, Parquet y nombres personales quedan fuera del PR. No se han adquirido actas de mesa ni la instantánea provisional del 23J, y no se ha efectuado conciliación de indicadores de correo. Esos límites permanecen explícitos en los informes e inventario.
