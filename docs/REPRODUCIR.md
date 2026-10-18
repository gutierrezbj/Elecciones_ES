# Reproducción del hito 1

Requiere Python 3.12 o posterior y conexión HTTPS para adquirir las fuentes. Desde la raíz del repositorio:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
python -m scripts.reproduce --output work/reproduction-01
```

El script ejecuta las pruebas sin red, descarga los tres recursos fijados en `data/sources/checksums.json`, exige sus hashes, verifica los originales, ejecuta Soria (42) y solo después amplía a nivel nacional. No sobrescribe ejecuciones previas. Un hash nuevo requiere revisar la nueva versión, no actualizar automáticamente el pin. Los valores fijados son observaciones de esta recuperación, no firmas ni hashes publicados por el organismo.

El resultado nacional puede ser `completed_with_findings`: la ejecución se completó y tiene observaciones técnicas pendientes. El script termina correctamente tras generar ese informe; esto **no** equivale a declarar que todos los datos cuadran. Soria debe pasar sin observaciones para abrir la ejecución nacional en este script.

## Comandos individuales

```sh
python -m pytest -q
python -m elecciones.cli download interior_congress_mesa interior_senate_mesa ine_geography_23j
python -m elecciones.cli verify
python -m elecciones.cli pipeline --province 42 --output data/processed/soria-01
python -m elecciones.cli pipeline --output data/processed/national-01
```

Para exigir un hash en una descarga individual:

```sh
python -m elecciones.cli download interior_congress_mesa --expected-sha256 e78fc231326a03cf67bbec87b7100ea0c8c46859daa1b2a631c06daaaf1717f8
```

La CLI usa catálogo CSV configurable (`--catalog` antes del subcomando). `--raw-dir`, `--manifest`, `--timeout` y `--attempts` están documentados en `--help`. Timeout limita operaciones de socket y duración del streaming, no es un planificador de tareas. Hay 1–5 intentos, pausas exponenciales acotadas, límite de 256 MiB, comprobación de Content-Length si existe y log por intento. No se desactiva TLS ni se emplea la autenticación embebida de la API del sitio.

Salidas CLI: 0 = descarga/verificación correcta o pipeline sin observaciones; 1 = descarga fallida/hash distinto o pipeline completado con observaciones; 2 = entrada inválida o error de integridad/formato. En particular, un pipeline nacional con salida 1 puede tener un informe completo y útil. Una excepción después de abrir las salidas deja `FAILED.json`, sin informe completo. Una verificación de inputs fallida no abre el directorio de salida.

## Artefactos

- `data/downloads/manifest.jsonl`: registro histórico versionado de esta adquisición (incluye fallos TLS de los XLSX exploratorios). Nuevas reproducciones usan otro manifest bajo `work/`.
- `data/raw/<source_id>-<sha256>.raw`: bytes originales inmutables; excluidos de Git. Un cambio del servidor produce otra ruta. Se detecta corrupción local antes de reutilizar un archivo.
- `{congress,senate}-{totals,results,published}.parquet`: esquema canónico, registros fuente 09, resultados 10 y agregados publicados 07. Procesamiento de resultados por lotes.
- `report.json`: cobertura, hallazgos, conciliaciones, límites, timestamps, hashes y revisión de código. `code_dirty` hace explícito si el código local estaba modificado.
- `artifacts.json`: SHA-256 de cada salida, excepto del propio índice. Los timestamps hacen que dos informes no sean idénticos byte a byte: contrastar también entradas, conteos, conciliaciones y hallazgos.

`reports/` publica los informes JSON y resúmenes pequeños. No incluye ZIP, Parquet, nombres personales ni archivos grandes. La CI usa fixtures sintéticos; no depende de la disponibilidad del servidor oficial ni sustituye a la reproducción real.

## Comprobar una observación

Buscar su `source_id` en el manifest y el catálogo; verificar el SHA-256; abrir exclusivamente los miembros y líneas de `source_locators`. Los ficheros son de ancho fijo: usar las posiciones de [ESQUEMA.md](ESQUEMA.md), conservando ceros iniciales y el espacio de sección. En conciliaciones provinciales, `published_source_locators` señala la fila 07; las filas 09 de la provincia y su CERA permiten reconstruir la suma. El informe no cambia datos ni adjudica explicaciones sin evidencia documental.
