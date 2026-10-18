# Plan técnico v0.1 — Auditoría electoral 23J

## Alcance
Todas las provincias y ciudades autónomas; todos los municipios y mesas alcanzables. El foco no depende del tamaño de municipio. Congreso y Senado por separado.

## Entidades mínimas
source(id, organismo, url, versión, licencia, retrieved_at, sha256, estado)
geography(provincia, municipio, distrito, sección, mesa)
result(election_type, scrutiny_type, geography_key, candidacy_code, votes, source_id)
evidence(document_id, source_id, geography_key, kind, verification_status)
finding(id, geography_key, rule, observed, expected, evidence_ids, status, reviewer)

## Controles
- Clave única por proceso, tipo de escrutinio, geografía y candidatura.
- Recuentos numéricos no negativos y sumas coherentes según definición oficial.
- Detección de filas duplicadas y mesas ausentes.
- Coincidencia entre agregados derivados y totales publicados comparables.
- Comparación de actas con transcripciones humanas y resultados publicados.
- Incidencias explicadas, pendientes o documentadas; no etiqueta automática de fraude.

## Voto por correo
Crear matriz de indicadores: solicitudes aceptadas, documentación tramitada, votos depositados, entregas y admitidos. Anotar unidad, fecha, organismo y alcance. No sumar indicadores diferentes ni inferir reparto por candidatura.

## Arquitectura inicial
Python 3.12+, pytest, scripts CLI, ficheros brutos fuera de Git, Parquet para datos normalizados y DuckDB para exploración reproducible. Posponer PostgreSQL y la interfaz web hasta validar adquisición y calidad.

## División del trabajo
Codex: ingesta, validaciones, tests, CI, pipeline e informes reproducibles.
Claude: revisión cruzada de fuentes, esquema, sesgos, privacidad, falsos positivos y PRs de auditoría.
Lorenzo/usuario: alcance, aceptación de evidencia y conclusiones públicas.

## Primeras tareas
- Auditar disponibilidad real de los enlaces oficiales.
- Diseñar manifest de descargas con SHA-256.
- Construir ingestión inicial de resultados desagregados.
- Validar denominadores de cobertura geográfica.
- Elaborar tabla de accesibilidad de actas.
