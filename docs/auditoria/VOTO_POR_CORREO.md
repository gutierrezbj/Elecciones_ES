# Matriz de verificabilidad del voto por correo — 23J

Base legal: LOREG en su versión vigente el 23/07/2023 (arts. 72, 73, 75 y 88), obtenida de la API de legislación consolidada del BOE y seleccionada por `fecha_vigencia`.

Regla de uso: cada fila es una magnitud distinta. No se suman entre sí, no se restan para "estimar" votos perdidos y no se reparten por candidatura.

## Residentes en España (arts. 72, 73 y 88)

| Etapa | Qué mide | Unidad | Quién la produce | Granularidad publicada | Cifra localizada | Calidad de la fuente | Verificabilidad |
|---|---|---|---|---|---|---|---|
| 1. Solicitud | Solicitudes presentadas en Correos, presenciales o telemáticas (art. 72.a) | solicitudes | Correos, por cuenta de la OCE | Nacional; algunas CCAA en prensa | 2.622.808 "solicitudes admitidas" (el reparto 1.924.976 presenciales + 697.832 telemáticas solo consta en prensa) | Primaria: [nota de Correos del 22/07/2023](https://www.correos.com/ca/sala-prensa/exito-en-la-gestion-del-voto-por-correo-que-marca-record-historico-con-2-471-935-votos-admitidos-para-las-elecciones-generales/), localizada en el PR #5 | agregado_institucional |
| 2. Recepción en la OCE | Voto por correo por fecha de recepción y por provincia de inscripción y de remisión (INE, tablas [59763](https://www.ine.es/jaxi/Tabla.htm?L=0&tpx=59763) y [59766](https://www.ine.es/jaxi/Tabla.htm?L=0&tpx=59766)) | por confirmar: probablemente solicitudes recibidas en la OCE (incluye 122.790 "posteriores a 13/07/2023", fecha límite de solicitud) | OCE (INE) | Provincia de inscripción × provincia de remisión; tramos de fecha | 2.604.386 | Primaria oficial, localizada en el PR #5 | agregado_oficial; unidad pendiente de nota metodológica |
| 2 bis. Aceptación | Solicitudes comprobadas y anotadas en el censo (art. 73.1) | solicitudes aceptadas | OCE (INE) | No localizada por separado | — | — | no_localizado |
| 3. Envío | Documentación enviada por la OCE por correo certificado (art. 73.2) | envíos | OCE / Correos | No localizada | ">2,3 millones puestas a disposición" (cifra intermedia, previa al 23J) | Prensa | agregado_secundario, no usar como cifra final |
| 4. Entrega al elector | Avisos de recibo firmados por el elector (art. 73.2) | entregas | Correos | No publicada | — | — | inaccesible |
| 5. Depósito / admisión | Sobres de voto admitidos en Correos (art. 73.3) | sobres | Correos | Nacional; La Rioja en prensa (19.897) | 2.471.935 "votos admitidos", 94,2 % de las solicitudes admitidas | Primaria: [nota de Correos del 22/07/2023](https://www.correos.com/ca/sala-prensa/exito-en-la-gestion-del-voto-por-correo-que-marca-record-historico-con-2-471-935-votos-admitidos-para-las-elecciones-generales/) | agregado_institucional |
| 6. Traslado a mesa | Correspondencia entregada a las mesas el día de la votación; registro a disposición de las Juntas (art. 73.4) | sobres por mesa | Correos | No publicada | — | — | restringido (Juntas) |
| 7. Introducción en urna | Sobres que el Presidente introduce tras comprobar el certificado y la inscripción; nombres anotados en la lista numerada de votantes (art. 88.2) | votantes por mesa | Mesa electoral | Solo en el expediente electoral (sobre 1, art. 100) | — | — | restringido (acta y lista numerada) |
| 8. Escrutinio | Votos por correo dentro de la urna | — | Mesa | **No existe**: se escrutan mezclados con los presenciales (arts. 88.2 y 95.4) | — | — | imposible por diseño legal |

## Residentes en el extranjero, CERA (art. 75)

Desde la LO 12/2022 (BOE-A-2022-16018, vigente desde el 04/10/2022) la OCE envía la documentación de oficio: el 23J fue la primera elección general sin voto rogado. El voto del CERA llega a la Junta Electoral y se escruta aparte, por eso los ficheros de Interior lo traen en registros propios (municipio `999`).

| Magnitud | Congreso | Senado | Fuente | Verificabilidad |
|---|---|---|---|---|
| Censo CERA | 2.328.260 | 2.328.260 (nacional) | Interior, fichero 09, registro nacional CERA | verificado |
| Votantes CERA (blancos + nulos + candidaturas) | 208.431 | 213.937 | Interior, fichero 09 | verificado (dato oficial según la marca del fichero) |
| Desglose | Provincia (52 registros) | Distrito electoral, con islas | Interior | verificado |

Los votantes del CERA en Congreso y Senado no tienen por qué coincidir: son sobres y escrutinios distintos. La diferencia no es un hallazgo.

## Errores de interpretación que este proyecto debe evitar

- Llamar "votos por correo" a las solicitudes (etapa 1) o a los sobres admitidos (etapa 5).
- Restar la etapa 5 de la etapa 1 y presentar la diferencia como "votos perdidos". La diferencia mezcla al menos solicitudes no aceptadas y documentación no recogida, y no hay cifras públicas para separarlas.
- Atribuir a una mesa o a un partido un efecto del voto por correo. No hay dato de correo por mesa publicado (etapas 6-7) ni puede haberlo por candidatura (etapa 8).
- Comparar participación por mesa con voto por correo provincial. Son granularidades distintas.
- Sumar el CERA a las mesas sin descartar los registros de total autonómico y nacional (provincia o CA = 99). Triplica el censo CERA: 6.984.780 en lugar de 2.328.260 en Congreso.

## Fuentes primarias pendientes

- Nota metodológica de las tablas INE 59763 y 59766, para fijar si miden solicitudes recibidas, aceptadas o documentación tramitada.
- Las tres cifras (2.622.808 de Correos, 2.604.386 del INE y 2.471.935 de Correos) son unidades distintas. No se restan entre sí hasta conocer la definición del INE.
- Instrucción 5/2023 de la JEC citada en el art. 73.3.

Fuentes secundarias consultadas, que no sirven como evidencia: [El Independiente, 22/07/2023](https://www.elindependiente.com/espana/2023/07/22/un-dispositivo-de-14-000-carteros-llevara-el-23-j-a-las-urnas-2-471-935-votos-record-historico/), [RTVC](https://rtvc.es/26-millones-de-espanoles-piden-el-voto-por-correo-record-historico/), [Nueve Cuatro Uno](https://nuevecuatrouno.com/2023/07/22/record-absoluto-19-897-riojanos-votan-por-correo/), [Maldita, 03/06/2025](https://maldita.es/malditobulo/20250603/resultado-voto-correo-elecciones-23j/).
