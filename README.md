# Elecciones_ES — Auditoría documental del 23J

Proyecto abierto para reconstruir y contrastar los resultados de las elecciones generales españolas del 23 de julio de 2023 a partir de fuentes verificables.

## Objetivo
Auditar todas las mesas con datos disponibles, sin excluir municipios por tamaño. Diferenciar escrutinio provisional, escrutinio general definitivo, actas de mesa y estadísticas agregadas del voto por correo. Identificar errores de datos, discrepancias documentadas, límites de cobertura y posibles incidencias que requieran investigación adicional. **Ninguna anomalía estadística constituye por sí sola prueba de fraude.**

## Principios
- Neutralidad política y ausencia de conclusiones preconcebidas.
- Conservar originales, URL, fecha de descarga, licencia, versión y SHA-256.
- No publicar datos personales ni intentar conocer el sentido del voto individual.
- Mantener resultados de Congreso y Senado separados.
- No confundir voto por correo solicitado, admitido, entregado y finalmente escrutado.
- Documentar cada transformación y su prueba automatizada.
- Publicar también resultados que cuadren y limitaciones que impidan verificar.
- Priorizar la cobertura nacional, sin ignorar municipios pequeños.

## Fuentes de partida (requieren validación de ficheros)
- [Catálogo de resultados electorales — datos.gob.es](https://datos.gob.es/es/catalogo/e00003801-resultados-electorales)
- [Resultados definitivos — BOE-A-2023-18907](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-18907)
- [Instituto Nacional de Estadística](https://www.ine.es/)
- [Junta Electoral Central](https://www.juntaelectoralcentral.es/)
- [Correos](https://www.correos.es/)

## Fases
1. Inventario de fuentes y evaluación de acceso.
2. Descarga verificable, preservación de originales y catálogo de cobertura.
3. Normalización por provincia, municipio, distrito, sección, mesa, elección y candidatura.
4. Validación de sumas, claves, duplicados, ausencias y cruces provisional/definitivo.
5. Verificación documental con actas, revisión humana y registro de evidencias.
6. Auditoría de estadísticas del voto por correo dentro de su granularidad real.
7. Informe reproducible de hallazgos y limitaciones.

## Estado
**Inicio de proyecto.** No hay conjuntos descargados o auditados, ni hallazgos verificados todavía. No publicar conclusiones hasta ejecutar los controles.

## Colaboración con agentes
Leer [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md) y [docs/PLAN.md](docs/PLAN.md). Trabajar por ramas y pull requests, sin modificar datos originales.
