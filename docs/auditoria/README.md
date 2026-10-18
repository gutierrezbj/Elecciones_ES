# Auditoría independiente — Issue #2

Revisión metodológica de fuentes, granularidad, voto por correo, acceso a actas, trazabilidad y falsos positivos para el 23J (Congreso y Senado). Fecha de verificación: 18 de octubre de 2026. Revisor: Claude (agente), pendiente de aceptación humana.

Este documento no contiene conclusiones sobre fraude ni sobre ausencia de fraude. Recoge lo que se ha podido comprobar, cómo se ha comprobado y lo que no se puede comprobar con fuentes públicas.

## Documentos

| Documento | Contenido |
|---|---|
| [MATRIZ_FUENTES.md](MATRIZ_FUENTES.md) | Fuentes por granularidad, autenticidad, licencia y acceso; correcciones propuestas a `data/sources/catalog.csv` del PR #3 |
| [VOTO_POR_CORREO.md](VOTO_POR_CORREO.md) | Matriz solicitado / aceptado / depositado / entregado / admitido / escrutado, sin mezclar unidades |
| [ACTAS.md](ACTAS.md) | Cadena documental de las actas según la LOREG vigente el 23J y procedimiento de verificación |
| [HALLAZGOS_Y_FALSOS_POSITIVOS.md](HALLAZGOS_Y_FALSOS_POSITIVOS.md) | Criterios de revisión humana, clasificación, trampas conocidas y hallazgos detectados |
| [evidencia/manifest_2026-10-18.csv](evidencia/manifest_2026-10-18.csv) | URL, fecha, bytes y SHA-256 de cada original consultado |
| [reproduccion/verificar_23j.py](reproduccion/verificar_23j.py) | Script del auditor (solo biblioteca estándar) que reproduce los controles de este informe |

## Conclusiones de la revisión

1. **Hay datos por mesa públicos, oficiales y descargables sin restricciones.** El Área de Descargas de infoelectoral (Ministerio del Interior) publica por elección un ZIP con 60.314 mesas en 8.131 municipios de las 52 circunscripciones, más el CERA en registros aparte. Todos los registros llevan la marca "Datos oficiales = S". Es la base que necesita el Issue #1 y no figura en el catálogo del PR #3.
2. **La trazabilidad mesa → municipio → provincia → BOE se puede reproducir y casi cuadra.** El agregado provincial de Interior coincide exactamente con el resumen de la JEC en el BOE en las 52 provincias (Congreso). La suma por mesas coincide en 50 de 52; **Toledo** (+175 votos a candidaturas, +5 blancos, +10 nulos) y **Cantabria** (+4 blancos, +12 nulos) difieren. En el Senado cuadran las 52 provincias, y los 1.152 candidatos coinciden con el BOE uno a uno; la única diferencia es una errata que el propio BOE corrigió. Hallazgo H-001, en estado `awaiting_evidence`: hacen falta las actas de escrutinio general de las Juntas Provinciales para explicarlo. La diferencia no cambia el reparto de escaños de Toledo.
3. **No hay escrutinio provisional por mesa en las descargas.** No se ha localizado ningún fichero público por mesa del escrutinio provisional de la noche electoral. La comparación provisional/definitivo por mesa que pide la Puerta 3 de la hoja de ruta no es viable con fuentes públicas hasta que aparezca esa fuente.
4. **El voto por correo no se puede auditar por mesa ni por candidatura.** La ley manda introducir los sobres en la urna antes del recuento (art. 88.2 LOREG), y los ficheros oficiales no tienen ningún campo de voto por correo. Las cifras localizadas son agregados de unidades distintas: solicitudes admitidas (2.622.808) y votos admitidos (2.471.935), de la nota original de Correos, y 2.604.386 en las tablas INE 59763/59766, con la unidad por confirmar. Las tres fuentes primarias las localizó el PR #5.
5. **En el Senado por mesa, el campo de papeletas no es fiable; los votos a candidatos sí son coherentes.** En 596 mesas los votantes del Senado y del Congreso difieren en más de 50, y en 388 mesas habría más de 3 votos por papeleta. En las mesas infladas, los votos a candidatos guardan la proporción normal con los votantes del Congreso. El error está en los totales de papeletas, blancos o nulos, no en los votos que reparten escaños. Hallazgo H-002.
6. **Las papeletas no impugnadas se destruyen en la mesa** (art. 97.3). No es posible un recuento independiente: la evidencia máxima disponible es el acta, no la papeleta.
7. **La pista de Indra no tiene fuente primaria.** Lo localizado es secundario (verificadores y prensa). El marco legal sitúa la transmisión provisional en una copia del acta "a los solos efectos de facilitar la información provisional" (art. 98.2). El resultado oficial lo fijan las Juntas a partir de las actas (arts. 103-108). La pista sigue pendiente de fuente primaria, sin uso como hecho.

## Reproducción

```bash
unzip 02202307_MESA.zip -d congreso && unzip 03202307_MESA.zip -d senado
pdftotext -layout BOE-A-2023-18907.pdf boe.txt
python3 -I docs/auditoria/reproduccion/verificar_23j.py congreso senado --boe-txt boe.txt
```

Comprueba antes los SHA-256 contra el manifest. El script solo usa la biblioteca estándar de Python y no escribe ficheros. Es una herramienta de verificación del auditor; no sustituye al pipeline del Issue #1.

## Observaciones al PR #3

- `catalog.csv` no tiene las columnas que exige su propia Puerta 0: licencia, provisional/definitivo, fecha de publicación, fecha de recuperación, cobertura, método de acceso y SHA-256. Propuesta en [MATRIZ_FUENTES.md](MATRIZ_FUENTES.md).
- Falta la fuente primaria de resultados por mesa (infoelectoral). La ficha `interior_catalog` apunta a datos.gob.es, que el 18/10/2026 respondió HTTP 503 y luego timeout.
- `boe_2023` sí es el resultado definitivo (Resolución JEC de 30/08/2023), pero solo por circunscripción y candidatura. Tiene una corrección de errores posterior (BOE-A-2023-19537) que debe catalogarse.
- `ine` apunta a la portada del INE. Las tablas concretas (59763, 59766, 59781) las identificó el PR #5.
- `correos` no publica conjuntos de datos. Sus cifras salen en notas de prensa; la del 22/07/2023 está localizada (PR #5).
- `jec` no publica actas de mesa. Publica doctrina, acuerdos y el resumen en BOE. Ver [ACTAS.md](ACTAS.md).
- La hoja de ruta habla de "resultados provisionales de la noche electoral" como fuente separada, pero no se ha localizado su versión por mesa. Debe figurar como límite de cobertura.

## Límites de esta revisión

- Licencias: no se ha verificado el aviso legal de reutilización de infoelectoral ni del BOE. Están marcadas `por_verificar`.
- El Congreso se ha conciliado contra el BOE a nivel de circunscripción (Cuadro I), no candidatura por candidatura (Cuadros II y III), por los cortes de cifras del PDF. El Senado sí se ha conciliado candidato a candidato.
- El texto del BOE se ha extraído del PDF con `pdftotext`, que corta cifras en algunas tablas (por ejemplo "9.938." en el Cuadro III). Solo se han usado las cifras del Cuadro I, revisadas una a una contra el total estatal.
- No se ha consultado ninguna acta, ni de mesa ni de Junta.
- Los ficheros originales no se suben al repositorio (`.gitignore`). Se identifican por URL y SHA-256 en el manifest.
