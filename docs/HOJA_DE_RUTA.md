# Hoja de ruta y criterios de aceptación — 18 octubre 2026

## Norte del proyecto
Auditoría independiente, reproducible y no partidista de las elecciones generales españolas del 23J de 2023. No demostrar una hipótesis prefijada: contrastar datos, actas y procedimientos; explicar coincidencias, errores y discrepancias sin atribuciones precipitadas.

## Alcance irrenunciable
- Congreso y Senado son escrutinios distintos; modelarlos por separado.
- Cubrir todas las mesas y municipios que permitan las fuentes, sin descartar municipios pequeños ni priorizarlos por una presunción de fraude.
- Registrar por separado los resultados provisionales de la noche electoral, los resultados definitivos del escrutinio general y las actas.
- Examinar el voto por correo hasta el nivel permitido por las estadísticas y la ley. El voto por correo depositado en urna se mezcla con el presencial: no inventar resultados separados por candidatura.
- Verificar discrepancias entre actas y transmisión provisional cuando haya evidencia disponible.
- Revisar reclamaciones y resoluciones oficiales con referencias exactas.

## Orden de ejecución y puertas
### Puerta 0: Fuentes
Entregar data/sources/catalog.csv con URL directa validada, organismo, licencia, nivel, elección, provisional/definitivo, fecha, cobertura y método de acceso. Marcar enlaces rotos y bloqueos. No iniciar inferencias.

### Puerta 1: Integridad
CLI que descarga originales a almacenamiento excluido de Git, calcula SHA-256 y genera manifest con timestamp, URL, código HTTP, bytes, hash y estado. Pruebas con fixtures sintéticos.

### Puerta 2: Esquema y cobertura
Esquema canónico con códigos oficiales, provincia, municipio, distrito, sección, mesa, candidatura, tipo de elección, escrutinio, fuente y votos. Control de claves únicas, censo, participación, votos válidos, blancos y nulos según definiciones de la fuente. Informe de mesas cubiertas y faltantes con denominador conocido.

### Puerta 3: Conciliación
Comparar solo magnitudes equivalentes y períodos compatibles. Discrepancias con severidad de revisión técnica, no puntuación de fraude. Guardar evidencia, explicación, estado y revisor humano.

### Puerta 4: Correo y actas
Matriz de estadísticas por organismo y granularidad; solicitudes, aceptaciones, depósitos, entregas, admisiones: no confundir. Catálogo de actas y método de autenticación; registro de derechos de acceso y limitaciones.

### Puerta 5: Informe
Generar reporte con reproducibilidad, cobertura, hallazgos explicados, pendientes y limitaciones. Ninguna acusación personal ni afirmación de fraude sin documentación comprobable y revisión humana.

## Convenciones de hallazgos
Estados: detected, awaiting_evidence, explained, confirmed_data_error, documented_irregularity, dismissed. Separar observación, hipótesis, evidencia y conclusión. Un outlier estadístico solo genera tarea de revisión.

## Primera demo útil
Una provincia con datos reales y pipeline de extremo a extremo, seguido de extensión nacional. No construir dashboard hasta tener fuente y validaciones.
