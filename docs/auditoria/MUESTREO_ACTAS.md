# Protocolo de muestreo de actas de mesa — 23J

Versión 1. Estado: **pendiente de aprobación**. Se publica antes del sorteo, como preregistro: una vez integrado, ni el diseño ni la semilla se pueden cambiar sin una versión 2 justificada por escrito.

## Pregunta

¿Coinciden los resultados oficiales por mesa que publica el Ministerio del Interior con las actas de esas mesas?

Es la única comprobación que falta entre la papeleta y el BOE. Las papeletas se destruyen tras el recuento (art. 97.3 LOREG), así que el acta es la evidencia más cercana al recuento. El resto de la cadena (mesa → municipio → provincia → BOE) ya está verificado en [HALLAZGOS_Y_FALSOS_POSITIVOS.md](HALLAZGOS_Y_FALSOS_POSITIVOS.md).

**Qué puede concluir:** una estimación, con intervalo de confianza, de la proporción de mesas cuyos datos publicados difieren del acta.

**Qué no puede concluir:** nada sobre mesas concretas no muestreadas, ni sobre la intención de nadie, ni sobre lo que ocurrió antes de redactar el acta. Una diferencia no es por sí misma una irregularidad: la Junta pudo subsanar un error material o aritmético en el escrutinio general (art. 106.1).

## Marco

- 60.314 mesas físicas, idénticas en Congreso y Senado, de los ficheros `02202307_MESA.zip` y `03202307_MESA.zip`. Los SHA-256 están fijados en el script y en [evidencia/manifest_2026-10-18.csv](evidencia/manifest_2026-10-18.csv).
- Excluido el CERA: no tiene acta de mesa, porque se escruta en la Junta Electoral.
- Unidad muestral: la mesa. Por cada mesa se buscan las actas de Congreso y de Senado.

## Estratos y tamaño

| Estrato | Marco | Principal | Reserva | Uso |
|---|---|---|---|---|
| E1 general | 60.314 mesas | 300 | 300 | Estimación de la proporción de mesas con diferencias |
| E2 H-002 | 965 mesas del Senado con votantes que difieren en más de 50 de los del Congreso, o con más votos por papeleta de los que permite el art. 96.3 en circunscripciones no insulares; se descartan las que caigan en E1 | 30 | 30 | Explicar H-002; **no** entra en la estimación general |

**Por qué 300.** Con 0 diferencias en 300 mesas, el intervalo de confianza del 95 % (Clopper-Pearson) acota la proporción de mesas con diferencias por debajo del 1,22 %. Con 3 diferencias, el intervalo es 0,21 %-2,89 %. Más tamaño reduce poco el intervalo y multiplica el coste de conseguir actas.

**Reparto de E1.** Proporcional al número de mesas de cada provincia, con un mínimo de 2 y el método del mayor resto:

| Provincia | Mesas | Muestra | Provincia | Mesas | Muestra |
|---|---:|---:|---|---:|---:|
| A Coruña (15) | 1.544 | 7 | La Rioja (26) | 516 | 4 |
| Alacant/Alicante (03) | 2.227 | 9 | Las Palmas (35) | 1.564 | 7 |
| Albacete (02) | 521 | 4 | León (24) | 722 | 4 |
| Almería (04) | 837 | 5 | Lleida (25) | 549 | 4 |
| Araba/Álava (01) | 427 | 3 | Lugo (27) | 533 | 4 |
| Asturias (33) | 1.528 | 7 | Madrid (28) | 7.118 | 25 |
| Badajoz (06) | 902 | 5 | Melilla (52) | 87 | 2 |
| Barcelona (08) | 6.472 | 23 | Murcia (30) | 1.726 | 8 |
| Bizkaia (48) | 1.410 | 7 | Málaga (29) | 1.734 | 8 |
| Burgos (09) | 746 | 4 | Navarra (31) | 997 | 5 |
| Cantabria (39) | 777 | 5 | Ourense (32) | 539 | 4 |
| Castelló/Castellón (12) | 740 | 4 | Palencia (34) | 335 | 3 |
| Ceuta (51) | 96 | 2 | Pontevedra (36) | 1.344 | 6 |
| Ciudad Real (13) | 707 | 4 | Salamanca (37) | 648 | 4 |
| Cuenca (16) | 383 | 3 | Santa Cruz de Tenerife (38) | 1.379 | 7 |
| Cáceres (10) | 524 | 4 | Segovia (40) | 330 | 3 |
| Cádiz (11) | 1.528 | 7 | Sevilla (41) | 2.588 | 10 |
| Córdoba (14) | 948 | 5 | Soria (42) | 256 | 3 |
| Gipuzkoa (20) | 858 | 5 | Tarragona (43) | 1.039 | 5 |
| Girona (17) | 863 | 5 | Teruel (44) | 328 | 3 |
| Granada (18) | 1.121 | 6 | Toledo (45) | 903 | 5 |
| Guadalajara (19) | 587 | 4 | Valladolid (47) | 763 | 5 |
| Huelva (21) | 651 | 4 | València/Valencia (46) | 3.200 | 12 |
| Huesca (22) | 403 | 3 | Zamora (49) | 369 | 3 |
| Illes Balears (07) | 1.249 | 6 | Zaragoza (50) | 1.467 | 7 |
| Jaén (23) | 873 | 5 | Ávila (05) | 358 | 3 |
| **Total** | **60.314** | **300** | | | |

## Sorteo reproducible

1. Este protocolo se integra en `main` mediante un PR.
2. La semilla es `SHA-256("elecciones_es-muestreo-actas-v1|<SHA-256 Congreso>|<SHA-256 Senado>|<SHA-1 del commit de fusión de ese PR>")`. Nadie conoce el commit de fusión antes de fusionar, y después es público e inmutable. Para que nadie pueda rehacer la fusión hasta dar con una semilla conveniente, vale solo el **primer** commit de `main` que contiene este fichero (`git log --diff-filter=A --format=%H -- docs/auditoria/MUESTREO_ACTAS.md`, en su forma de commit de fusión), y el historial de `main` no se reescribe.
3. Cualquiera puede repetir el sorteo:

```bash
python3 -I docs/auditoria/muestreo/sortear_actas.py sortear --zip-congreso 02202307_MESA.zip --zip-senado 03202307_MESA.zip --commit <SHA del commit de fusión> --salida muestra.csv
```

4. La muestra se publica en un PR aparte (`docs/auditoria/muestreo/muestra_v1.csv`). Solo contiene códigos de mesa.

El script comprueba los SHA-256 de los ZIP antes de sortear. Dentro de cada provincia baraja la lista ordenada de mesas con un generador inicializado con la semilla: las primeras *n* son principales y las *n* siguientes, reservas en ese orden.

## Reglas de sustitución

- Se intenta conseguir el acta de cada mesa principal por todas las vías del apartado siguiente antes de declararla `no_disponible`.
- Solo entonces entra la siguiente reserva **de la misma provincia y en orden**. Nunca se elige la reserva a mano.
- Todas las mesas principales sustituidas se publican con el motivo.
- Si en E1 se consiguen menos del 70 % de las actas de las mesas principales, los resultados se publican como descriptivos, sin intervalo de confianza: la falta de respuesta podría no ser aleatoria.

## Fuentes de actas y jerarquía

| Nivel | Fuente | Base | Uso |
|---|---|---|---|
| A | Copia del acta entregada a una candidatura | Arts. 98.1 y 99.2 | Válida. Si se consiguen de dos candidaturas distintas y coinciden, nivel A+ |
| A | Copia facilitada por la Junta Electoral o por el juzgado (sobre 2) | Arts. 101.4 y 105.3 | Válida, por petición del responsable del proyecto |
| C | Fotografía del acta expuesta a la entrada del local, aportada por un ciudadano | Art. 98.1 | Solo como indicio. No entra en la estimación: no se puede verificar quién la tomó ni cuándo |

Si dos copias de nivel A de la misma mesa no coinciden entre sí, la mesa se clasifica `copias_contradictorias` y no se compara con el dato oficial, igual que hace la Junta (art. 105.3).

Pedir las actas a las candidaturas tiene un sesgo: cada una tiene copias solo de las mesas donde hubo interventores o apoderados. Por eso se piden a **todas** las candidaturas con representación, con la misma lista de mesas, y se publica qué aportó cada una.

## Transcripción y comparación

Se usa [muestreo/plantilla_transcripcion.csv](muestreo/plantilla_transcripcion.csv), una fila por candidatura o candidato.

1. Se calcula el SHA-256 del original (escaneo o PDF) al recibirlo. El original no se sube al repositorio público.
2. Dos personas transcriben cada acta por separado (`transcriptor` A y B), sin ver el dato oficial.
3. Si las dos transcripciones no coinciden, se resuelve contra la imagen y se anota la resolución.
4. La transcripción final se compara con los ficheros 09 y 10 de Interior.

Campos que se comparan: electores, votantes, nulos, blancos y votos por candidatura (Congreso) o por candidato (Senado). En el Senado se compara además el total de papeletas, para H-002.

## Clasificación por mesa

| Clase | Definición |
|---|---|
| `coincide` | Todos los campos comparados son iguales |
| `difiere` | Al menos un campo distinto. Se anota cuál, el valor del acta, el valor oficial y la diferencia |
| `ilegible` | El acta no permite leer algún campo comparado |
| `copias_contradictorias` | Dos copias de nivel A no coinciden entre sí |
| `no_disponible` | No se consiguió ninguna copia de nivel A tras agotar las vías |

Cada mesa `difiere` abre un hallazgo con los estados y criterios de [HALLAZGOS_Y_FALSOS_POSITIVOS.md](HALLAZGOS_Y_FALSOS_POSITIVOS.md). Antes de cualquier conclusión se comprueba si la Junta subsanó esa mesa.

## Resultado que se publicará

- Para E1, por cámara: número de mesas por clase, proporción `difiere` sobre (`coincide` + `difiere`) con intervalo de Clopper-Pearson al 95 % (`sortear_actas.py intervalo --n N --k K`), tasa de obtención y sustituciones.
- Por separado: suma de las diferencias de votos por candidatura en las mesas `difiere` y si alguna podría alterar un escaño en su circunscripción.
- Para E2: si el error de H-002 ya está en el acta o aparece al transcribirla.
- Siempre: la tabla completa mesa a mesa, con códigos y sin datos personales.

## Privacidad y custodia

- Las actas llevan nombres y firmas de miembros de mesa e interventores. No se publican: el repositorio solo guarda la transcripción y el SHA-256 del original.
- Los originales se guardan fuera del repositorio, con acceso restringido al responsable del proyecto y a los transcriptores.
- La lista numerada de votantes nunca se pide ni se acepta.

## Decisiones que corresponden al responsable del proyecto

- Aprobar este protocolo e integrarlo, lo que fija la semilla.
- Quién pide las actas a las candidaturas, a las Juntas y a los juzgados, y en nombre de quién.
- Quiénes son los dos transcriptores. Deben ser personas distintas al revisor de los hallazgos.
