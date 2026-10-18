# Esquema canónico v2 — 23J

Los originales permanecen en `data/raw/`, fuera de Git. Los Parquet son transformaciones; ninguna corrección se escribe en el original. El informe enlaza versión de código, hash del catálogo, manifest, ZIP y documento de formato. Cada registro conserva `source_id` y `source_locators` (`miembro.DAT:line:N`, líneas desde 1).

## Tipos y clave

| Campo | Tipo / definición |
|---|---|
| election_date | ISO date, `2023-07-23`, validada con fichero 02 |
| election_type | `congress` o `senate`; nunca se mezclan |
| scrutiny_type | `definitive` si flag Datos oficiales = S; `unknown` si N (no oficial no significa necesariamente provisional) |
| geography_level | `table`, `cera`, `province` o `constituency` |
| province_code | Código INE, texto de 2 dígitos |
| constituency_code | Texto de 1 dígito: 9 para ámbito provincial; 1–7 para islas del Senado, asignado con el campo 119 del fichero 05 a cada municipio físico |
| municipality_code | Texto de 3 dígitos; `999` es CERA, no municipio físico; null en provincia |
| district_code | Texto de 2 dígitos; CERA provincial `09`; null en provincia |
| section_code | Texto **de 4 caracteres**: 3 dígitos y espacio/letra/dígito. No eliminar el espacio final. CERA `0000` |
| table_code | Letra de mesa, U para única; null en provincia |
| population_scope | `cer` en mesas físicas, `cera` en registro exterior, `total` en agregados provinciales |
| candidacy_code / candidacy_key | Código oficial de 6 dígitos en Congreso; null en Senado |
| candidate_code | Código oficial de 6 dígitos en Senado, provincia + distrito electoral + orden. Null en Congreso; no se leen nombres |
| votes | Entero int64 no negativo; votos a candidatura en Congreso, marcas de un candidato en Senado |
| source_id | FK al catálogo versionado |
| source_locators | Lista de ubicaciones exactas en el original |

Clave de resultado: fecha, cámara, escrutinio, nivel, provincia, municipio, distrito municipal, sección, mesa, ámbito censal, circunscripción y candidatura/candidato. `source_id` es procedencia, no una forma de ocultar duplicados. Clave de totales: la misma sin candidatura/candidato. En una futura comparación de versiones, conservar cada snapshot separado.

`electors` usa censo **de escrutinio**, no necesariamente el censo INE inicial (`electors_ine`). `blank_votes`, `null_votes` y `candidacy_ballots` vienen de 09 o 07. `valid_votes = candidacy_ballots + blank_votes` y `voters = valid_votes + null_votes` son derivados: el formato no trae votantes ni válidos independientes. Sus identidades aritméticas no prueban consistencia externa.

## Contrato del adaptador DAT

Se usa `FICHEROS.doc` incluido en cada ZIP; su SHA-256 se registra. Ambos documentos con extensión doc/rtf son OLE Word en esta descarga, no texto RTF. No es necesario convertirlos para ejecutar el pipeline.

| Miembro | Campos (posiciones inclusivas desde 1) |
|---|---|
| 02 | Proceso 1–9; fecha día/mes/año 13–20; ancho 40 |
| 05 (Senado insular) | Provincia 12–13; municipio 14–16; total municipal 17–18 = 99; distrito electoral 119; ancho 233. No se usa el distrito municipal como isla |
| 09 | CCAA 10–11; provincia 12–13; municipio 14–16; distrito 17–18; sección 19–22; mesa 23; censo INE 24–30; escrutinio 31–37; blancos 66–72; nulos 73–79; papeletas a candidaturas 80–86; oficial 101; ancho 101 |
| 10 | Misma geografía hasta 23; candidatura o candidato 24–29; votos 30–36; ancho 36 |
| 07 | Provincia 12–13; distrito electoral 14 (9 = provincia); nombre 15–64; mesas 73–77; censo INE 78–85; escrutinio 86–93; blancos 126–133; nulos 134–141; papeletas a candidaturas 142–149; oficial 172; ancho 172 |

Decodificación Latin-1, líneas LF o CRLF, posiciones sobre caracteres de un byte. Se rechazan cambios de ancho, elección o fecha, duplicados de miembros requeridos, registros 10 sin 09 y códigos de candidatura no numéricos. El indicador oficial de 10 se hereda del 09 correspondiente. La definición de datos oficiales del documento se refiere a publicaciones de Juntas Electorales; el mapeo a definitive es una convención explícita del adaptador, no una firma de autenticidad.

No se abre el miembro 04 de nombres de candidatos. Los ZIP públicos completos pueden incluir esos nombres: quedan sin extraer, privados y excluidos de Git. No se recopilan datos de electores.

## CERA, Senado y agregación

Los registros CERA con provincia 99 son rollups autonómicos/nacionales y se omiten. En Senado insular se conservan los registros CERA por isla (07: 1/2/3, 35: 1/2/3, 38: 4/5/6/7) y se excluye el agregado provincial 09. Congreso mantiene el CERA provincial 09. Las exclusiones quedan registradas; no se suman los dos niveles.

Las mesas físicas insulares reciben `constituency_code` del campo 119 de los totales municipales 05. Si falta una correspondencia, se detiene la ingesta. Las diez circunscripciones insulares se concilian por separado contra 07, además de mantener la conciliación provincial.

La suma provincial de 09 incorpora mesas físicas CER más los registros CERA del ámbito: uno provincial en Congreso y Senado no insular; uno por isla en Senado insular; se contrasta con 07, distrito electoral 9, del mismo ZIP. Se exige mismo escrutinio en todos los términos. Nunca se suman los totales de Congreso y Senado, ni marcas de candidatos al Senado como si fueran papeletas. Cada marca individual del Senado se contrasta con el número de papeletas a candidaturas de su geografía, sin sumar marcas entre candidatos.

## Hallazgos, evidencia y cobertura

Un hallazgo tiene ID estable, regla, observado, esperado, severidad `technical_review`, estado `detected`, revisor null y procedencia. Las diferencias de agregados añaden referencias de evidencia. No hay puntuación de fraude ni diagnóstico causal. El esquema del plan para actas/evidence permanece reservado: no se crean actas, revisiones humanas ni explicaciones ficticias.

La cobertura cuenta claves distintas de municipios y mesas físicas, contra la tabla INE 59781 del proceso 23J. Su denominador no procede de las filas descargadas. CERA no cuenta como municipio ni mesa física. La tabla aporta **cardinalidades**, no un inventario independiente de IDs: `missing` es diferencia de conteos; `missing_keys` y `unexpected_keys` son null. Incluso cuando ambos conteos coinciden, no se afirma identidad demostrada de conjuntos. La función de cobertura admite inventarios de IDs y detecta faltantes concretos cuando estén disponibles.

## Controles añadidos tras revisión independiente

El pipeline exige que los tres originales seleccionados coincidan con `checksums.json`, incluso fuera de `scripts.reproduce`. `--allow-unpinned` permite exploración explícita: produce aviso y registra hashes esperados/observados y la excepción en el informe. Nunca se actualizan los pines automáticamente.

Las identidades de valores derivados se registran como `structural_identities`, no como pruebas independientes de la fuente. Para filas DAT no se cuentan `valid_plus_null` y `candidacy_plus_blank` como controles independientes. Se conservan para otras entradas que traigan esas cifras independientes.

En Senado se comprueba también `suma de marcas <= papeletas a candidaturas × máximo de selecciones`. El máximo es 3 para provincias no insulares, 2 en Mallorca (07/1), Gran Canaria (35/1), Tenerife (38/4), Ceuta y Melilla, y 1 en las demás islas; referencia: [artículo 96.3 LOREG, redacción de 1994](https://www.boe.es/eli/es/lo/1994/03/30/13). Un exceso es una discrepancia entre campos publicados, no prueba de papeletas nulas reales ni de su causa. Se controla también el límite cuando la fuente da cero papeletas.

`chamber_diagnostics` enumera diferencias absolutas de votantes derivados >50 entre cámaras para la misma mesa física y escrutinio. Es un diagnóstico descriptivo con umbral explícito: votar en una cámara no obliga a votar en la otra. No se suma al número de hallazgos ni se interpreta como infracción legal.
