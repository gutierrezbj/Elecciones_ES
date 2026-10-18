# Instrucciones para Codex y otros agentes

Misión: desarrollar herramientas reproducibles para auditar los resultados de las elecciones generales españolas de 2023, sin asumir fraude ni ausencia de fraude.

## Primera entrega
1. Confirmar enlaces oficiales, licencia, formatos, desglose y disponibilidad de los datasets.
2. Implementar un catálogo de fuentes versionado (CSV o JSON) con organismo, URL, fecha de publicación, fecha de recuperación, nivel geográfico, tipo de escrutinio, licencia y estado.
3. Implementar una CLI Python para descargar con reintentos razonables, timeouts, manifest SHA-256 y logs. Nada de eludir restricciones ni recopilar datos personales.
4. Conservar archivos originales sin alteración; no subir grandes archivos al repositorio.
5. Añadir pruebas unitarias con fixtures sintéticos para sumas, claves compuestas, duplicados y discrepancias.
6. Producir informe de cobertura de municipios y mesas, con denominador explícito y datos faltantes.

## Restricciones
- No inferir fraude de participaciones, desviaciones o patrones estadísticos.
- No inventar fuentes, actas, cifras o resultados.
- Distinguir nivel mesa / municipio / provincia y provisional / definitivo.
- No tratar cifras agregadas de voto por correo como recuento separado por partido o mesa.
- No registrar ni publicar información personal.
- No modificar archivos fuente en bruto; llevar trazabilidad de cada transformación.
- Usar commits pequeños y PR con descripción, pruebas y limitaciones.
- Si una descarga falla, registrar el fallo sin simular datos.

## Definición de terminado del primer hito
Pipeline documentado que ejecuta tests, registra fuentes, descarga al menos una fuente auténtica legalmente accesible, verifica hash y muestra cobertura y faltantes; si la descarga no es viable, documentar el bloqueo verificable.
