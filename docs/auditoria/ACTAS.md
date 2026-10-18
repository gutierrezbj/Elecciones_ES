# Actas: cadena documental y procedimiento de verificación

Base legal: LOREG vigente el 23/07/2023. Las citas son paráfrasis; el texto literal está en la versión consolidada del BOE (BOE-A-1985-11672).

## Qué documentos existen y quién los tiene

| Documento | Artículo | Contenido | Copias | Quién lo custodia | Acceso para este proyecto |
|---|---|---|---|---|---|
| Acta de escrutinio de mesa | 97.2, 98.1 | Electores, certificaciones censales, votantes, nulos, blancos y votos por candidatura | Se fija en la entrada del local; una copia por candidatura que la pida; otra a la persona designada por la Administración, **solo para el escrutinio provisional** (98.2) | Candidaturas, Administración | Solo a través de las candidaturas que la recogieron |
| Acta de la sesión | 99 | Lo anterior, interventores que votaron fuera de lista, reclamaciones, protestas e incidentes | Copia gratuita a representantes, apoderados e interventores (99.2) | Mesa → sobres 1, 2 y 3 | Candidaturas; originales en Junta y juzgado |
| Expediente electoral (sobre 1) | 100.2 | Originales de las actas de constitución y sesión, lista numerada de votantes, papeletas impugnadas, lista del censo, certificaciones censales | Original | Junta Electoral (vía juez, 101.3) | Restringido |
| Sobre 2 | 100.3, 101.4 | Copias de las actas | — | Juzgado de Primera Instancia o de Paz | Restringido; lo pueden reclamar Juntas y tribunales |
| Sobre 3 | 100.3, 105.3 | Copias de las actas | — | Lo usa la Junta si falta el sobre 1 | Restringido |
| Acta de escrutinio general | 108.1 | Por circunscripción: electores, votantes, votos por candidatura, blancos y nulos | Triplicado | Junta Electoral Provincial | Restringido; el resumen sale en BOE (BOE-A-2023-18907) |
| Acta de sesión de escrutinio general | 108.1 | Incidencias del escrutinio general | — | JEP | Restringido |
| Reclamaciones y recursos | 108.2-3; 109 y ss. | Reclamaciones ante la JEP, recursos ante la JEC, contencioso-electoral | — | JEP, JEC, tribunales | Resoluciones de la JEC: publicación parcial |

## Límites que impone la ley

- Las papeletas se destruyen tras el recuento, salvo las nulas o reclamadas (art. 97.3). **No hay recuento independiente posible.** La unidad de evidencia más fina es el acta de mesa.
- En el escrutinio general la Junta no puede anular actas ni votos: solo verifica sumas y subsana errores materiales, de hecho o aritméticos (art. 106.1). No computa actas dobles y diferentes ni actas con más votos que electores, salvo error material (art. 105.4).
- Si faltan los sobres, la Junta puede usar la copia del acta que presente una candidatura; si hay copias contradictorias, no usa ninguna (art. 105.3).
- El escrutinio provisional sale de una copia del acta entregada a la Administración "a los solos efectos" de informar provisionalmente (art. 98.2). No tiene efecto jurídico en el resultado.

## Procedimiento propuesto para verificar un acta

1. **Origen.** Registrar quién aporta el documento (candidatura, interventor, Junta, tribunal), cuándo y con qué base de acceso. Ninguna acta llega por canales anónimos.
2. **Preservación.** Guardar el escaneo original sin editar y calcular su SHA-256 en el momento de recibirlo. Las transcripciones van en un fichero aparte.
3. **Privacidad.** Antes de guardar en el repositorio, eliminar o tapar nombres, DNI y firmas de miembros de mesa, interventores y apoderados. No se publica nunca la lista numerada de votantes.
4. **Identificación.** Extraer provincia, municipio, distrito, sección y mesa, y comprobar que la clave existe en el fichero 09 de Interior.
5. **Coherencia interna.** Comprobar votantes = nulos + blancos + candidaturas; votantes ≤ censo + certificaciones + interventores fuera de lista; firmas presentes.
6. **Doble transcripción.** Dos personas transcriben por separado. Si no coinciden, se resuelve contra la imagen antes de comparar con nada.
7. **Contraste.** Comparar con el registro de mesa de Interior. Si difiere, buscar si hay copia del acta de otra candidatura, resolución de la JEP o recurso.
8. **Clasificación.** Abrir un hallazgo con los estados de [HALLAZGOS_Y_FALSOS_POSITIVOS.md](HALLAZGOS_Y_FALSOS_POSITIVOS.md). Una diferencia entre un acta aportada por una parte y el dato oficial **no** es por sí misma una irregularidad: la Junta pudo subsanar un error (art. 106.1).

## Riesgos jurídicos

- Publicar actas sin tapar los datos personales de los miembros de la mesa expone al proyecto en materia de protección de datos.
- Atribuir discrepancias a personas concretas (presidentes de mesa, empleados de Correos, empresas contratistas) sin resolución que lo respalde puede ser difamatorio. Los hallazgos se refieren a claves de mesa, no a personas.
- Las actas que aporte una candidatura llegan con sesgo de selección: cada parte aporta las que le interesan. Hay que declarar la cobertura y no extrapolar.

## Solicitudes de acceso por explorar (no realizadas)

- Petición a las Juntas Electorales Provinciales de Toledo y Cantabria de las actas de escrutinio general y de sesión del 23J, para explicar el hallazgo H-001 (ver hallazgos).
- Petición a la JEC de las resoluciones de recursos del 23J por circunscripción.
- Contactar con las candidaturas para pedir las copias de actas de mesa que recogieron.

Antes de cualquier solicitud hace falta decidir quién la firma y con qué base legal. Es una decisión del responsable del proyecto, no del agente.
