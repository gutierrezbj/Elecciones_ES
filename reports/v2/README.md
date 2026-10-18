# Revisión v2 del hito 1 — 18 de octubre de 2026

Se repitió el procesamiento con las entradas originales verificadas y fijadas por SHA-256, primero Soria y después el país. Esta ejecución fue **offline**: reutiliza los recibos HTTP del 18/10/2026 11:03 UTC sin modificar sus fechas ni simular nuevas descargas. El código es `68b03cc0d6c47ba092aa5c17487df7d8ad5de4ee`, con `code_dirty=false` en ambos informes. Pasan **63 pruebas**, además de CI en Python 3.12 y 3.13.

Origen de los datos: Ministerio del Interior. Elaboración propia con datos extraídos del sitio web del INE para los denominadores; sin patrocinio de esos organismos.

| Ámbito | Municipios por cámara / INE | Mesas físicas por cámara / INE | Registros CERA Congreso / Senado | Observaciones de reglas |
|---|---:|---:|---:|---:|
| Soria (42) | 183 / 183 | 256 / 256 | 1 / 1 | 0 |
| Nacional | 8.131 / 8.131 | 60.314 / 60.314 | 52 / 59 | 506 |

La cobertura sigue siendo una comparación de cardinalidades, no una prueba de identidad de conjuntos de mesas. Los registros CERA no cuentan como mesas físicas ni municipios. El Senado conserva ahora las diez circunscripciones insulares, en lugar de sustituirlas por tres agregados provinciales; se excluyen esos tres rollups para no duplicar votos. Los diez cruces insulares contra el fichero 07 concilian en los seis campos comparados.

El país produce 1.986.144 resultados, 120.739 registros de mesa/CERA y 114 agregados publicados (104 provinciales y 10 insulares). El número de resultados no cambia respecto a v1; se recupera el contexto de circunscripción del CERA y se añade `constituency_code` a las claves. Por ello cambian los IDs y hashes de salidas v2; los originales y la evidencia v1 se conservan.

## Observaciones y límites

| Regla | Número | Alcance |
|---|---:|---|
| voters_exceed_electors | 61 | Igual observación que v1: votantes derivados mayores que censo publicado |
| published_total_mismatch | 9 | Iguales diferencias por campo de Cantabria y Toledo del Congreso |
| candidate_votes_exceed_ballots | 26 | Igual observación que v1: voto de un candidato mayor que papeletas publicadas de su mesa |
| senate_marks_exceed_capacity | 410 | Suma de marcas mayor que papeletas publicadas × máximo de selecciones; 388 en el ámbito no insular y 22 en islas |

**506 observaciones no son 506 mesas distintas ni irregularidades confirmadas.** Las reglas se solapan. Se mantienen como revisión técnica sin revisor, explicación causal o diagnóstico de fraude. El nuevo control incluye el caso de cero papeletas publicadas. Las inconsistencias pueden requerir revisar el significado y calidad de los campos de papeletas del Senado, no solo sus votos a candidatos.

El informe contiene también **596 diagnósticos descriptivos** de mesas con diferencia absoluta de votantes derivados entre cámaras superior a 50. Se separan de las observaciones de reglas: los votantes de ambas cámaras no tienen por qué coincidir. El umbral es de exploración, no una condición legal.

Las identidades `valid_plus_null` y `candidacy_plus_blank` se registran expresamente como estructurales para DAT, porque válidos y votantes se derivan de sus componentes. No se presentan como comprobaciones independientes superadas.

## Respuesta a la revisión del PR #5

| Observación | Tratamiento |
|---|---|
| Pines solo en el script de reproducción | Corregido: `pipeline` exige los SHA-256 fijados antes de abrir salidas. Una excepción deliberada requiere `--allow-unpinned`, aviso y registro en el informe |
| CERA del Senado insular | Corregido: conservar islas en 09/10, asignar mesas físicas por campo electoral 119 de 05 y conciliar los diez ámbitos en 07 |
| Falta el límite de marcas | Añadido para las 59 circunscripciones del Senado, con límites 3/2/1 según ámbito. No es una determinación de nulidad de papeletas individuales |
| N interpretado como provisional | Corregido a unknown; S conserva el mapeo explícito a definitivo según el documento de formato |
| Identidades derivadas | Marcadas como estructurales y excluidas de los controles independientes DAT |
| Timeout de socket y tiempo total iguales | Separados: `--timeout` para socket y `--max-seconds` para duración total por intento, por defecto 300 s |
| Cruce INE por nombres | Pendiente de fuente con códigos verificados. La exportación CSV fijada 59781 no trae código provincial. Se mantiene el cruce unívoco y se falla ante denominación desconocida; no se inventa una correspondencia por posición |
| Conciliación con BOE | Pendiente de implementación identificada y pruebas. El verificador independiente compara multiconjuntos de cifras en Senado, no pares candidato-código/votos. Eso no basta para afirmar coincidencia individual de 1.152 candidatos. En el XML recuperado, el Cuadro I del Congreso está incluido como imagen: la mera lectura del XML no proporciona sus celdas. El resumen no se etiqueta como conciliado con BOE |

No se han cerrado hilos de revisión ni asignado estados de aceptación humana. La revisión independiente y sus fuentes son evidencia que debe contrastarse, no una orden de cambiar las conclusiones. La referencia normativa del control de marcas está en [ESQUEMA.md](../../docs/ESQUEMA.md), art. 96.3 LOREG, redacción aplicable sin inferir causalidad.

## Evidencia

- [Soria](soria.json) y [hashes de sus salidas](soria-artifacts.json).
- [Nacional](national.json) y [hashes de sus salidas](national-artifacts.json).
- [Observaciones CSV](findings.csv); los diagnósticos separados están en `national.json`.
- [Recibos originales reutilizados](inputs-manifest.jsonl).
- [Índice SHA-256 de esta entrega](checksums.json).

Reproducción desde la raíz del repositorio, con dependencias instaladas y originales locales disponibles:

```sh
python -m scripts.reproduce --offline-manifest data/downloads/reproduction-20261018.jsonl --output work/reproduction-v2
```

Para descargar otra vez, omitir `--offline-manifest`: se exigirán los mismos pines. La ausencia de actas de mesa y de instantánea provisional, y la conciliación BOE pendiente, siguen siendo límites expresos. Ninguno de estos controles determina fraude.
