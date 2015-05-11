#registro de cambios

## v1.12(20/10/2013) ##
  * Añadido Error 064. Antes se cerraba el programa de forma inesperada al encontrarse este error

## v1.11(02/07/2013) ##
  * Corregida [Issue 25](https://code.google.com/p/eplvalidator/issues/detail?id=25)
  * Nuevas pruebas: [Issue 26](https://code.google.com/p/eplvalidator/issues/detail?id=26), [Issue 29](https://code.google.com/p/eplvalidator/issues/detail?id=29),  [Issue 27](https://code.google.com/p/eplvalidator/issues/detail?id=27), [Issue 30](https://code.google.com/p/eplvalidator/issues/detail?id=30)
  * Se permite usar año de 4 cifras en la fecha de modificación de la página título

## v1.10(16/06/2013) ##
  * Comprobación de que los metadatos Autor, File-as, Fecha de publicación y Sinopsis son diferentes de los del epubbase
  * Detección de la página info por su posición, en caso de que no se encuentre ningún archivo de nombre info.xhtml
  * Corrección automática de marcar cover.jpg como imagen de portada
  * Generación automática de nuevo UUID en caso de que coincida con el epub base
  * Generación automática del archivo com.apple.ibooks.display.xml en caso de que el libro tenga fuentes incrustadas


## v1.09(12/06/2013) ##
  * Corregidas [Issue 21](https://code.google.com/p/eplvalidator/issues/detail?id=21), [Issue 22](https://code.google.com/p/eplvalidator/issues/detail?id=22), [Issue 23](https://code.google.com/p/eplvalidator/issues/detail?id=23)
  * Añadidos caracteres '-', '.', ',' en el patron que detecta una saga en el nombre de archivo
  * Añadido apóstrofe a los caracteres permitidos en nombre de archivo y título
  * Detección de nombre de editor digital (Digital editor) en la página info para libros en inglés
  * Ampliada la detección de fecha de publicación en página info para fechas tipo "Nombre apellido, octubre de 2011"
  * Detección de pagina info por su nombre "info.xhtml" en lugar de por la posición que ocupa en el libro, para de esta manera detectarla correctamente en caso de que el editor introduzca alguna página con logos o imágenes antes de la página info.

## v1.08(09/06/2013) ##
  * Añadida comprobación nueva: [Issue 16](https://code.google.com/p/eplvalidator/issues/detail?id=16)
  * Añadida comprobación nueva: [Issue 17](https://code.google.com/p/eplvalidator/issues/detail?id=17)
  * Añadida comprobación nueva: [Issue 19](https://code.google.com/p/eplvalidator/issues/detail?id=19)
  * Corregido fallo cuando no se encontraba el metadato "fecha de publicación"

## v1.07(30/05/2013) ##
  * Añadido Error 047 : 'El identificador único del ePub debe ser del tipo UUID'
  * Sustituir & amp ;  por & al detectar autor en página info y título
  * Comprobación de que el editor en la página de título coincide con el de la página info
  * Mejoras en el código para reducir el número de lecturas de los metadatos en el archivo opf

## v1.06(25/05/2013) ##
  * Implementada [Issue 4](https://code.google.com/p/eplvalidator/issues/detail?id=4)
  * Añadido apóstrofe (') a los caracteres permitidos en nombre de autor (página de título, página info y metadatos). Añadidos ": ( ) ! ¡" a los caracteres permitidos en título del libro (página de título y metadatos)
  * Reportar error si no se detecta correctamente el tamaño de cover.jpg por error en el formato del archivo
  * Reorganizados los mensajes de error y codificado cada uno con un número de error, para una futura exportación de los resultados a un fichero CSV
  * Añadido portugués a la lista de idiomas
  * Corregida [Issue 13](https://code.google.com/p/eplvalidator/issues/detail?id=13), detección correcta de File-as para libros con varios autores
  * Corregido caracter inválido (tilde) en el nombre de una variable en el código


## v1.05(20/05/2013) ##
  * Añadida compatibilidad con el nuevo book-id del epub base 'urn:uuid:00000000-0000-0000-0000-000000000000'
  * Corregida [Issue 12](https://code.google.com/p/eplvalidator/issues/detail?id=12)
  * Añadido el caracter ":" a los caracteres permitidos en el título
  * Añadidos los caracteres "¿" y "?" a los caracteres permitidos en el título (página de título y metadatos, pero no en nombre de archivo)
  * Permitidas fechas que incluyan mes, o mes y día en la fecha de publicación que aparece en la página info (formato yyyy[-mm[-dd]])
  * Permitido id="heading\_id\_X" en página de título (compatibilidad con versiones de Sigil anteriores a v0.7)
  * Corregida [Issue 10](https://code.google.com/p/eplvalidator/issues/detail?id=10)
  * Implementada [Issue 11](https://code.google.com/p/eplvalidator/issues/detail?id=11)

## v1.04 ##
  * Corregida [Issue 6](https://code.google.com/p/eplvalidator/issues/detail?id=6)
  * Cambiado género "Guión" por "Guion" (ambas grafías son correctas, pero esta es la que se adoptó en el listado de la web)
  * Corregidos errores ortográficos en los mensajes del validador
  * Añadida posibilidad de ejecutar el script con un archivo como argumento (o arrastrando el archivo sobre el validador en Windows)
  * Implementada [Issue 9](https://code.google.com/p/eplvalidator/issues/detail?id=9)
  * Eliminados instrucciones.txt y changelog.txt del paquete. Pasan a la wiki de la página de google code
  * Detección de error si el File-as no contiene exáctamente una coma

## v1.03 ##
  * Corregida [Issue 5](https://code.google.com/p/eplvalidator/issues/detail?id=5)
  * Implementada [Issue 4](https://code.google.com/p/eplvalidator/issues/detail?id=4)
  * Implementada [Issue 1](https://code.google.com/p/eplvalidator/issues/detail?id=1)
  * Pequeñas mejoras en el código

## v1.02 ##
  * Corregida detección del subgénero "Ciencias naturales" (había una mayúscula de más)
  * Cambiada detección de "No ficción" por "No Ficción"
  * Abortar la ejecución cuando el número de argumentos es erróneo

## v1.01 ##
  * Añadida pausa al finalizar la ejecución, para que no se cierre la ventana con los resultados
  * Solucionado problema con toc.ncx que quedaba abierto
  * Contemplada posibilidad de nombres con guion en pagina de info, para la detección del año de publicación
  * Captura de excepciones en la importación del módulo tkinter

## v1.00 ##
  * Versión inicial