# Hallazgos, revisión humana y falsos positivos

## Clasificación

Se mantienen los estados de `docs/HOJA_DE_RUTA.md` (PR #3) y se fija quién puede mover cada uno:

| Estado | Significado | Quién lo asigna | Evidencia mínima |
|---|---|---|---|
| `detected` | Una regla automática o una revisión manual ha encontrado una diferencia | Pipeline o agente | Regla, valores observado y esperado, ficheros con SHA-256 |
| `awaiting_evidence` | Hace falta un documento que no tenemos | Agente o revisor | Lista del documento concreto que falta y quién lo custodia |
| `explained` | Hay una causa documentada que no es error ni irregularidad (definición, código especial, artefacto de formato) | Revisor humano | Cita de la especificación, norma o documento |
| `confirmed_data_error` | Error de publicación o transcripción demostrado con un documento de mayor rango | Revisor humano | Documento oficial que contradice el dato |
| `documented_irregularity` | Irregularidad reconocida en una resolución oficial (Junta, tribunal) | Solo el responsable del proyecto | Resolución con referencia exacta |
| `dismissed` | Era un fallo de nuestro propio código o lectura | Revisor humano | Explicación y test que lo cubre |

Ningún agente puede asignar `documented_irregularity`. Un outlier estadístico nunca pasa de `detected` sin un documento.

Cada hallazgo separa cuatro campos: **observación** (qué dicen los datos), **hipótesis** (posibles causas, todas), **evidencia** (documentos con hash) y **conclusión** (vacía hasta que la firma un revisor).

## Criterios de revisión humana

1. El revisor no es quien escribió la regla que generó el hallazgo.
2. Antes de cualquier otra hipótesis se descartan las trampas de la tabla siguiente.
3. Se comprueba en el original (fichero con hash, acta), nunca solo en el dato normalizado.
4. Si la diferencia no cambia escaños, se dice explícitamente. Si los cambia, se dice también.
5. La conclusión se escribe en términos de datos y documentos, sin adjetivos ni personas.

## Trampas que generan falsos positivos (verificadas en los datos del 23J)

| # | Trampa | Efecto si se ignora | Cómo se evita | Comprobado |
|---|---|---|---|---|
| FP-01 | Los registros CERA incluyen totales autonómicos (provincia 99) y nacional (CA 99) | El censo CERA se triplica: 6.984.780 en vez de 2.328.260 (Congreso) | Usar solo registros CERA con CA y provincia ≠ 99 | Sí |
| FP-02 | En el Senado el CERA insular viene por isla y además por provincia (distrito 09) | Doble conteo en Baleares, Las Palmas y Santa Cruz de Tenerife | Usar islas o provincia, no las dos | Sí |
| FP-03 | Mesas con más votantes que censo de escrutinio | Parece voto excedente | El censo de la **sección** cuadra y el reparto por mesa no. Ver caso León | Sí, 4 mesas |
| FP-04 | Senado: "votos a candidaturas" en 09 cuenta papeletas, y en 10 hay votos por candidato (hasta 3 por papeleta, art. 96.3) | Suma de votos por candidato > votantes | No comparar el 10 del Senado con votantes | Sí: Toledo, 1.101.808 votos a candidatos frente a 375.259 papeletas a candidaturas y 390.969 votantes |
| FP-05 | Los blancos del Senado incluyen papeletas sin ninguna marca (art. 96.5) | Blancos del Senado ≫ blancos del Congreso (384.061 frente a 199.103 en mesas) | Comparar cada cámara solo consigo misma | Sí |
| FP-06 | Censo INE ≠ censo de escrutinio (diferencia nacional de 317) | Parece manipulación del censo | El BOE define el censo como residentes en España, CERA y certificaciones censales específicas de alta; usar el censo de escrutinio para la participación | Sí (la diferencia); la causa por mesa no está verificada |
| FP-07 | Mesas pequeñas: 651 mesas con censo < 50 y 1.587 municipios con censo < 100 | Participaciones del 100 % o mesas sin votos parecen anómalas por pura varianza | Umbrales por tamaño; nunca un ranking de "anomalías" sin intervalo | Sí: 43 mesas con votantes = censo, 3 con 0 votantes |
| FP-08 | Sección alfanumérica: tres dígitos y un espacio, una letra o otro dígito, según la especificación | Mesas fusionadas o claves falsas si se convierte a entero | Tratar la sección como texto de 4 caracteres | Sí |
| FP-09 | Extracción de PDF del BOE | Cifras truncadas ("9.938." en el Cuadro III) | Usar los ficheros de Interior para el cálculo y el BOE solo para conciliar totales revisados | Sí |
| FP-10 | Voto por correo sin desglose | Atribuir a correo diferencias de mesa | Ver VOTO_POR_CORREO.md | Por diseño legal |
| FP-11 | Comparar provisional y definitivo | Las diferencias son esperables (actas tardías, subsanaciones del art. 106) | Solo con datos provisionales por mesa, que no se han localizado | Bloqueado |
| FP-12 | Usar el Senado por mesa para medir participación | En 596 mesas los votantes del Senado y del Congreso difieren en más de 50, y en 57 mesas el Senado supera el censo | Medir participación por mesa solo con el Congreso; el Senado por mesa solo para votos por candidato, con cautela | Sí. Ver H-002 |

### Caso León (FP-03) — estado `explained` (propuesto)

| Mesa (prov-mun-dist-secc-mesa) | Censo INE | Censo escrutinio | Votantes Congreso |
|---|---|---|---|
| 24-206-01-001-A | 458 | 1.097 | 335 |
| 24-206-01-001-B | 634 | 251 | 468 |
| 24-206-01-001-C | 463 | 207 | 349 |
| **Sección** | **1.555** | **1.555** | 1.152 |
| 24-222-02-001-A | 232 | 1.144 | 174 |
| 24-222-02-001-B | 614 | 143 | 503 |
| 24-222-02-001-C | 530 | 89 | 436 |
| **Mesas A-C** | **1.376** | **1.376** | 1.113 |

El total del censo de la sección coincide y el reparto entre mesas no. Lo coherente es un error en el campo de censo de escrutinio por mesa, no votos de más. Pasa igual en el Senado. Para pasarlo a `explained` falta que un revisor humano lo confirme. Para `confirmed_data_error` haría falta el acta de la sesión de esas mesas.

## Hallazgos detectados

### H-001 — Suma de mesas ≠ agregado provincial oficial (Congreso, Toledo y Cantabria)

- **Estado:** `awaiting_evidence`
- **Observación:** con los ficheros de Interior `02202307_MESA.zip` (SHA-256 `e78fc231…`), el fichero 09 (mesas + CERA provincial) coincide con el fichero municipal 05 en los 8.131 municipios. Su suma por provincia coincide con el fichero 07 (circunscripción) y con el Cuadro I del BOE-A-2023-18907 en 50 de 52 provincias. Las dos restantes:

| Provincia | Magnitud | Suma de mesas | Fichero 07 = BOE | Diferencia |
|---|---|---|---|---|
| Toledo (45) | Votos a candidaturas | 384.764 | 384.589 | +175 |
| Toledo (45) | Blancos | 2.616 | 2.611 | +5 |
| Toledo (45) | Nulos | 5.798 | 5.788 | +10 |
| Cantabria (39) | Blancos | 3.266 | 3.262 | +4 |
| Cantabria (39) | Nulos | 5.007 | 4.995 | +12 |

Desglose de Toledo por candidatura (fichero 10 frente a fichero 08 = BOE): FO −221, PSOE +59, PUM+J −1, PP +280, VOX +68, PACMA +3, SUMAR −13. En Cantabria los votos por candidatura cuadran; solo difieren blancos y nulos.

- **Hipótesis (sin orden de preferencia):** (a) la JEP subsanó errores en el escrutinio general (art. 106.1) y la corrección se trasladó al agregado provincial pero no al registro de mesa; (b) error en la carga de los ficheros por mesa de Interior; (c) error en la carga del agregado. El fichero 07 coincide con el BOE, lo que hace menos probable (c).
- **Lo que no se puede decir:** que haya votos añadidos o quitados. La suma oficial proclamada es la del BOE y la diferencia está dentro de la publicación de Interior.
- **Escaños:** no cambian. D'Hondt de Toledo (6 escaños) con las cuatro candidaturas con escaño o cerca: PP 3, PSOE 2, VOX 1 tanto con la suma de mesas como con el dato oficial. Último cociente asignado: 48.938 frente a 48.844; siguiente, PSOE/3, 42.044 frente a 42.024.
- **Evidencia necesaria:** acta de escrutinio general y acta de sesión de la JEP de Toledo y de Cantabria (art. 108.1). Identificar qué mesas difieren requiere el acta de esas mesas o un fichero alternativo por mesa.
- **Reproducción:** ver [README](README.md#reproducción).
- **Decisión del responsable (18/10/2026):** aparcado por impacto nulo en escaños. No se envía solicitud de actas para este hallazgo. Queda preparado un borrador, fuera del repositorio, por si el proyecto decide verificar una muestra aleatoria de actas.

### H-002 — Votantes del Senado por mesa incoherentes con el Congreso

- **Estado:** `detected` (calidad de datos, prioridad baja)
- **Observación:** en la misma mesa, la suma de blancos, nulos y votos a candidaturas del Senado (fichero `03202307_MESA.zip`, 09) difiere de la del Congreso así:

| Diferencia absoluta | Mesas |
|---|---|
| 0 | 16.647 |
| 1-2 | 19.645 |
| 3-10 | 20.628 |
| 11-50 | 2.798 |
| > 50 | 596 (468 con Senado mayor, 128 con Congreso mayor) |

  Las mesas con diferencia > 50 se concentran en Barcelona (108), Madrid (83), Sevilla (60) y Valencia (31). Ejemplo: mesa 28-079-15-177-A, Congreso 354 votantes, Senado 631, con censo de 483. Aun así, la suma de mesas del Senado coincide con el agregado provincial de Interior en las 52 provincias.
- **Lo esperable:** diferencias pequeñas, porque un elector puede no depositar uno de los dos sobres. No lo son diferencias de cientos.
- **Dónde está el error.** Se ha cruzado el campo de papeletas del Senado (fichero 09, "votos a candidaturas") con la suma de votos por candidato (fichero 10):
  - En las 468 mesas con Senado mayor, los votos a candidatos guardan con los votantes del Congreso la proporción normal: mediana de 2,81 votos por votante, frente a 2,80 en el conjunto de mesas provinciales. Lo que está inflado es el campo de papeletas (o blancos y nulos), no los votos a candidatos.
  - En 388 mesas peninsulares la suma de votos a candidatos supera el máximo legal de 3 por papeleta (2 en Ceuta y Melilla, art. 96.3). Ahí el campo de papeletas es demasiado bajo. Ejemplo: mesa 11-008-01-010-A, 385 papeletas y 1.548 votos a candidatos (máximo posible 1.155).
  - En las 128 mesas con Senado menor la proporción es más baja (mediana de 2,18). No se ha determinado si faltan papeletas o votos a candidatos.
  - Los votos por candidato, que son los que deciden escaños, cuadran exactos con el BOE en los 1.152 candidatos (ver más abajo).
- **Hipótesis:** error al anotar en el acta del Senado los totales de papeletas, blancos o nulos, o error al transcribirlos. El cuadre provincial no permite elegir entre las dos, porque el agregado de Interior parece construido desde estos mismos registros.
- **Lo que no se puede decir:** que haya votos de más en el Senado ni que afecte a los escaños. El campo de papeletas por mesa no es fiable; los votos por candidato sí son coherentes con el resultado oficial.
- **Evidencia necesaria:** acta de sesión del Senado de una muestra de esas mesas, para ver si el error ya está en el acta o aparece al transcribirla.

## Controles superados

| Control | Ámbito | Resultado |
|---|---|---|
| Claves de mesa únicas | 60.314 mesas por cámara | 0 duplicados |
| Fichero 09 tiene su desglose en el 10 y al revés | Ambas cámaras | 0 registros huérfanos |
| Suma de candidaturas (10) = votos a candidaturas (09) | Congreso, 60.386 registros | 0 diferencias |
| Suma de mesas (09) = municipio (05) | 8.131 municipios, ambas cámaras | 0 diferencias |
| Suma de mesas + CERA = circunscripción (07) | Senado, 52 provincias | 0 diferencias |
| Circunscripción (07) = BOE Cuadro I | Congreso, 52 provincias | 0 diferencias |
| Votos por candidato (08) = BOE | Senado, 1.152 candidatos en 59 circunscripciones | 1 diferencia: el candidato de Madrid con la errata "1.007.32" que corrige el BOE-A-2023-19537; Interior tiene ya la cifra corregida, 1.007.322 |
| Reproducibilidad de descarga | 9 originales del manifest | Mismo SHA-256 en una segunda descarga el 18/10/2026 |

## Pista pendiente: Indra y resultados de mesa

- **Estado:** sin fuente primaria. No se usa como hecho.
- **Lo localizado:** solo fuentes secundarias. Según verificadores ([Maldita](https://maldita.es/malditobulo/20230804/falso-conteo-votos-malaga-indra/), [Público](https://www.publico.es/politica/desinformaciones-sobre-indra-elecciones-espana.html)) y prensa ([Vozpópuli](https://www.vozpopuli.com/espana/documento-interior-elecciones-generales-noviembre-2023.html)), Interior licitó un acuerdo marco para el servicio de recogida y difusión de resultados provisionales, adjudicado a Indra en febrero de 2023, al que Indra fue la única licitadora. **No se ha verificado** en la Plataforma de Contratación.
- **Marco legal verificado:** el escrutinio provisional se basa en una copia del acta "a los solos efectos de facilitar la información provisional" (art. 98.2). El resultado oficial lo fijan las Juntas sobre actas en papel (arts. 103-108). Por tanto, una afirmación sobre manipulación de resultados oficiales por el contratista del provisional tendría que mostrar una diferencia entre actas de mesa y resultado oficial, no entre provisional y oficial.
- **Para avanzar:** (1) localizar el vídeo original y la cita exacta, con fecha y autor; (2) descargar de la Plataforma de Contratación el expediente del acuerdo marco y su pliego de prescripciones técnicas; (3) identificar qué datos por mesa recibe el contratista y cuáles publica Interior. Hasta entonces, no se cita.
