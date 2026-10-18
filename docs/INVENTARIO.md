# Inventario comprobado — 18 de octubre de 2026

El catálogo [catalog.csv](../data/sources/catalog.csv) sustituye los puntos de partida pendientes del PR #3 por estados específicos. Una URL de portal no se considera una descarga validada. Una fecha de publicación vacía significa no establecida; no se confunden fecha electoral, Last-Modified HTTP y recuperación. Los intentos de recuperación, bytes y hashes están en [manifest.jsonl](../data/downloads/manifest.jsonl).

| Recurso | Disponibilidad comprobada y alcance |
|---|---|
| Interior, ZIP 02202307_MESA | HTTPS 200; DAT y formato Word incluidos. Congreso: mesa y CERA, agregados municipales y superiores. El pipeline interpreta 02, 07, 09 y 10; flags oficiales S |
| Interior, ZIP 03202307_MESA | HTTPS 200; mismo esquema; 10 contiene códigos de **candidato** al Senado. Incluye CERA insular y rollups que hay que excluir del total provincial |
| INE, tabla 59781 CSV | HTTPS 200; denominadores del proceso: 8.131 municipios y 60.314 mesas. Totales provinciales sin IDs individuales |
| BOE-A-2023-18907 XML | HTTPS 200; resolución publicada 01/09/2023. Resultados de escrutinio general por circunscripción; algunas tablas son imágenes. No son actas de mesa |
| BOE-A-2023-19537 XML | HTTPS 200; corrección publicada 16/09/2023, sobre Senado en Madrid. Referencia incluida en el inventario; no se publican nombres ni se afirma conciliación completa con BOE |
| Interior, XLSX históricos Congreso/Senado | Enlaces y CC-BY-4.0 confirmados en datos.gob.es. curl consiguió descargar los XLSX; la CLI urllib recibió error de certificado en este entorno. Exploración descartada del pipeline cuando se obtuvo el ZIP de mesas. No se desactiva la validación TLS |
| INE, tablas 59763 / 59766 | Selectores oficiales de información de correo por fecha de recepción y por provincia de inscripción/remisión. Identificados; exportación y semántica detallada no normalizadas en este hito |
| JEC, página específica Generales-julio2023 | HTTPS 200; índice de documentación del proceso. No se han localizado ni adquirido actas individuales de todas las mesas |
| Correos, nota 22/07/2023 | HTTPS 200; indicador nacional de admisión postal. No es admisión por mesas electorales, ni recuento por partido, ni sustituto de la fuente INE |

## Procedencia y condiciones

Origen de los datos: **Ministerio del Interior**. Los ZIP directos están bajo `https://infoelectoral.interior.gob.es/estaticos/docxl/apliextr/`. El área oficial de descargas y su JavaScript público se recuperaron para documentar el directorio de recursos; no se usa la API con autenticación embebida. Los nombres de los ZIP se comprueban mediante respuesta HTTPS, estructura, fecha interna y documento de formato; no solo por el patrón de URL.

El [aviso legal de Infoelectoral](https://infoelectoral.interior.gob.es/es/aviso-legal/) permite reutilización comercial y no comercial bajo sus condiciones generales: atribución, preservación de metadatos, fecha de actualización cuando conste y ausencia de atribución de patrocinio. Se recuperó la página y se fijó su hash en el manifest. No se extiende automáticamente la licencia CC-BY de las distribuciones XLSX a los ZIP.

Elaboración propia con datos extraídos del sitio web del **INE**: [tabla 59781](https://www.ine.es/jaxi/Tabla.htm?L=0&tpx=59781). Su [aviso legal](https://www.ine.es/dyngs/AYU/index.htm?cid=125), también recuperado con hash, indica CC-BY-4.0 para información estadística propia salvo excepción. Los Last-Modified observados de los ZIP fueron 27/12/2023; el CSV del INE devolvió 05/05/2026. Se guardan como metadatos de servidor, sin afirmar que sean fechas de publicación estadística.

El manifest documenta la recuperación efectiva del BOE y de las páginas de referencia. Las condiciones específicas no resueltas de BOE, JEC y Correos permanecen señaladas en catálogo; no se redistribuyen sus documentos completos.

Los primeros intentos con curl a Infoelectoral agotaron el timeout o recibieron un reset. La CLI urllib obtuvo después ambos ZIP con HTTPS 200 y validación TLS activa. No persiste un bloqueo de adquisición de mesas. Los errores TLS de los XLSX sí permanecen registrados. Los IDs exploratorios con sufijo `_candidate` se conservan como `superseded_id` para entender el historial, sin duplicar la contabilización de fuentes.

## Correo y actas: límites de verificabilidad

| Indicador / evidencia | Unidad y organismo | Estado |
|---|---|---|
| Recepción de correo, por fecha | Agregado OCE/INE; tabla 59763 | Identificado; no conciliado |
| Provincia de inscripción y remisión | Agregado OCE/INE; tabla 59766 | Identificado; no conciliado |
| Admisión postal comunicada el 22/07 | Agregado nacional Correos | Página recuperada; no equivale a votos admitidos/escrutados por las mesas |
| Solicitudes aceptadas, documentación, entregas y admisión por mesa | Indicadores con etapas y organismos diferentes | Matriz cuantitativa pendiente; no sumar categorías ni inventar equivalencias |
| Actas de escrutinio general | Publicación resumen JEC/BOE | Referencia recuperada; no cotejada mesa por mesa |
| Actas individuales y transcripción humana | Mesa | No adquiridas; autenticación y cobertura pendientes |

No se infiere reparto por candidatura del correo ni se deduce fraude a partir de una discrepancia. Los candidatos del Senado se representan exclusivamente por código. El ZIP original puede contener nombres públicos de candidaturas: el fichero 04 no se abre ni extrae y no se sube a Git.
