# Matriz de fuentes

Verificado el 18/10/2026. "Autenticidad" indica cómo se comprueba que el fichero es el publicado por el organismo; "Oficialidad" indica si la ley lo considera resultado oficial.

## Resultados

| ID propuesto | Organismo | URL directa | Granularidad | Escrutinio | Oficialidad | Autenticidad | Licencia | Acceso | Estado |
|---|---|---|---|---|---|---|---|---|---|
| mir_02_mesa | Ministerio del Interior | https://infoelectoral.interior.gob.es/estaticos/docxl/apliextr/02202307_MESA.zip | Mesa + CERA por provincia | General (marca "Datos oficiales = S") | Reproducción de Interior; la propia especificación dice que solo son oficiales los datos publicados por las Juntas | HTTPS + SHA-256 del manifest; no hay firma | por_verificar | Libre, HTTP 200 | verificado |
| mir_02_muni | Ministerio del Interior | …/apliextr/02202307_MUNI.zip | Municipio, distrito municipal | General | Igual que arriba | Igual | por_verificar | Libre | verificado |
| mir_02_tota | Ministerio del Interior | …/apliextr/02202307_TOTA.zip | Circunscripción, CA, nacional | General | Igual | Igual | por_verificar | Libre | verificado |
| mir_03_mesa | Ministerio del Interior | …/apliextr/03202307_MESA.zip | Mesa + CERA por distrito electoral | General | Igual | Igual | por_verificar | Libre | verificado |
| mir_03_muni | Ministerio del Interior | …/apliextr/03202307_MUNI.zip | Municipio | General | Igual | Igual | por_verificar | Libre | verificado |
| mir_03_tota | Ministerio del Interior | …/apliextr/03202307_TOTA.zip | Circunscripción, CA, nacional | General | Igual | Igual | por_verificar | Libre | verificado |
| boe_jec_resumen | JEC (publicado en BOE) | https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-18907 (PDF: /boe/dias/2023/09/01/pdfs/BOE-A-2023-18907.pdf) | Circunscripción y candidatura; Senado por candidato | Definitivo (actas de escrutinio general y proclamación) | **Oficial** | PDF con código cve y leyenda "Verificable en https://www.boe.es" | por_verificar | Libre | verificado |
| boe_jec_correccion | JEC (BOE) | https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-19537 | Un candidato de Senado (Madrid) | Corrección | Oficial | Igual | por_verificar | Libre | verificado |
| datos_gob_catalogo | datos.gob.es | https://datos.gob.es/es/catalogo/e00003801-resultados-electorales | Catálogo, no datos | — | — | — | por_verificar | HTTP 503 y luego timeout el 18/10/2026 | bloqueado_temporal |
| provisional_mesa | Ministerio del Interior | no localizada | Mesa | Provisional (noche electoral) | No oficial (art. 98.2 LOREG) | — | — | — | no_localizado |
| actas_mesa | Juntas Electorales / juzgados | no publicadas | Mesa | Acta de sesión y de escrutinio | Base del escrutinio general | Original firmado; ver ACTAS.md | — | Restringido | restringido |
| actas_jep | Juntas Electorales Provinciales | no publicadas en línea | Circunscripción | Acta de escrutinio general (art. 108) | Oficial | — | — | Restringido / solicitud | restringido |
| loreg | BOE | https://www.boe.es/datosabiertos/api/legislacion-consolidada/id/BOE-A-1985-11672/texto | Norma | — | Oficial | Versión vigente el 23/07/2023 por `fecha_vigencia` | por_verificar | API abierta | verificado |

### Contenido real de los ZIP de Interior

Formato de longitud fija, ANSI, descrito en `FICHEROS.doc` dentro de cada ZIP (versión de 2010). Ficheros por elección (`xx` = 02 Congreso, 03 Senado):

| Fichero | Contenido | Registros 23J Congreso |
|---|---|---|
| 01xx2307 | Control | 1 |
| 02xx2307 | Identificación del proceso (fecha, horas de apertura y cierre) | 1 |
| 03xx2307 | Candidaturas y cabeceras de acumulación | — |
| 04xx2307 | Candidatos | — |
| 05xx2307 | Datos globales municipales | 8.131 municipios |
| 06xx2307 | Candidaturas por municipio | — |
| 07xx2307 | Datos globales por circunscripción, CA y nacional | — |
| 08xx2307 | Candidaturas por ámbito superior al municipio | — |
| 09xx2307 | Datos globales por mesa y CERA | 60.314 mesas + 72 registros CERA |
| 10xx2307 | Candidaturas por mesa y CERA | — |

Ningún fichero tiene un campo de voto por correo. El registro de mesa trae: censo INE, censo de escrutinio, CERE, dos avances de participación, blancos, nulos, votos a candidaturas y la marca "Datos oficiales".

### Clave de mesa

`provincia(2) + municipio(3) + distrito(2) + sección(4, alfanumérica) + mesa(1)`. Sin duplicados en 09 de Congreso ni de Senado. La sección es alfanumérica ("001 " con espacio final): no se puede convertir a entero.

Códigos especiales que no son mesas:

- Municipio `999` = CERA. Sección `0000`, mesa `U`.
- Provincia `99` = total autonómico o nacional del CERA. CA `99` = total nacional del CERA.
- En el Senado, el CERA de Baleares, Las Palmas y Santa Cruz de Tenerife viene por isla (distrito 1-7) **y** por provincia (distrito 09).

## Fuentes añadidas por el PR #5 (Codex) y comprobadas por el auditor

| Fuente | URL | Comprobación del auditor (18/10/2026) |
|---|---|---|
| Nota de Correos, 22/07/2023 | https://www.correos.com/ca/sala-prensa/exito-en-la-gestion-del-voto-por-correo-que-marca-record-historico-con-2-471-935-votos-admitidos-para-las-elecciones-generales/ | HTTP 200; contiene 2.471.935 votos admitidos y 2.622.808 solicitudes admitidas |
| INE 59763, voto por correo por fecha de recepción | https://www.ine.es/jaxiPx/files/tpx/es/csv_bdsc/59763.csv | HTTP 200; total 2.604.386 |
| INE 59766, voto por correo por provincia de inscripción y remisión | https://www.ine.es/jaxiPx/files/tpx/es/csv_bdsc/59766.csv | HTTP 200; total 2.604.386 |
| INE 59781, municipios y mesas | https://www.ine.es/jaxiPx/files/tpx/es/csv_bdsc/59781.csv | Usada en el PR #5 como denominador; 8.131 municipios y 60.314 mesas coinciden con Interior |
| Aviso legal de infoelectoral | https://infoelectoral.interior.gob.es/es/aviso-legal/ | No revisado por el auditor; el PR #5 lo resume como reutilización con atribución |

## Propuesta de columnas para `data/sources/catalog.csv`

```
id,organismo,url,url_documentacion,eleccion,camara,nivel_geografico,tipo_escrutinio,oficialidad,formato,licencia,fecha_publicacion,fecha_recuperacion,bytes,sha256,metodo_acceso,estado,notas
```

Valores de `estado`: `verificado`, `pendiente_validacion`, `bloqueado_temporal`, `restringido`, `no_localizado`, `secundaria_institucional`, `secundaria_prensa`.

Las filas `ine` y `correos` del PR #3 deben pasar a `no_localizado` y `secundaria_institucional`. Ver [VOTO_POR_CORREO.md](VOTO_POR_CORREO.md).
