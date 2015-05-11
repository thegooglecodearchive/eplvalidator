EPLvalidator es un script en python que nos ayudará a detectar gran cantidad de fallos frecuentes en los ePubs que maquetemos, antes de publicarlos en la web.

## PRUEBAS ACTUALMENTE IMPLEMENTADAS ##

  * Comprobar "add semantics" en cover.jpg (corrección automática)
  * Comprobar géneros:
    1. Al menos existe un género de la lista oficial
    1. Al menos existe un subgénero de la lista oficial
    1. No hay género o subgéneros que no estén en la lista
    1. No hay géneros y subgéneros de Ficción asignados a libros de No ficción y viceversa
    1. Comprobar que no contiene simultáneamente subgéneros exclusivos de Ficción y de No ficción
  * Comprobar tamaño de archivos, verifica que ninguno exceda los 300 KB
  * Comprobar que todos los autores y contributors tienen File-As
  * Comprobar que el nombre de archivo no tiene caracteres no permitidos
  * Comprobar que los archivos internos no tienen caracteres no permitidos en el nombre
  * Comprobar que el bookID es diferente del epub base (corrección automática)
  * Comprobar que el bookID es del tipo UUID (y no del tipo "ISBN" por ejemplo) y tiene el formato correcto.
  * Comprobar que el bookID es el mismo en content.opf y toc.ncx
  * Comprobar la ausencia de etiquetas < i > < b > y estilos automáticos de Sigil y Calibre
  * Comprobar que la versión en el nombre de archivo coincide con la versión de la página de título
  * Comprobar formato correcto del nombre de archivo:
```
  [saga_larga numero_opcional] Apellidos, Nombre - Titulo [identificador] (rx.x texto_opcional).epub
  [saga_larga numero_opcional] [subsaga número] Apellidos, Nombre - Titulo [identificador] (rx.x texto_opcional).epub
  Apellidos, Nombre - [saga número] Titulo [identificador] (rx.x texto_opcional).epub
  Apellidos, Nombre - Titulo [identificador] (rx.x texto_opcional).epub
```
  * Comprobar que el epub contiene los metadatos obligatorios (título, autor, editorial[=ePubLibre], idioma, fecha publicación, fecha modificación, descripción)
  * Comprobar de que los metadatos Autor, File-as, Fecha de publicación y Sinopsis son diferentes de los del epub base
  * Comprobar que en caso de que el nombre de archivo contenga una serie, el metadato meta content="XXX" name="calibre:series" está presente en los metadatos
  * Comprobar que el año de publicación no es posterior al año actual (error frecuente en MacOSX)
  * Comprobar que el año de publicación (metadatos) coincide con el año de publicación en página info.
  * Comprobar que el traductor (metadatos) coincide con el traductor en página info (si existe)
  * Comprobar que las dimensiones de la portada son 900 x 600 px
  * Detectar inconsistencias del título entre la páginas de título y metadatos
  * Detectar inconsistencias del autor entre la páginas de título, página info y metadatos (incluyendo File-as)
  * Comprobar que la fecha de modificación en metadatos es la misma que la fecha de modificación que aparece en la página de título
  * Comprobar que la linea de subtítulo se ha eliminado si era innecesaria, o sustituido si el libro tiene subtítulo
  * Comprobar que la versión de la plantilla epubbase corresponde con la última versión (actualmente la v1.0)
  * Comprobar que se han eliminado las lineas innecesarias de la página info (ejemplo: "Diseño/retoque de portada", "Ilustrador", ...)
  * Comprobar que la fecha de modificación no sea 2012-12-12 ni 2013-04-23 (fechas de modificación de los dos epub base). Caso posible en versiones antiguas de Sigil, al no ser automático el cambio)
  * Comprobar que el editor en la página de título coincide con el de la página info
  * Comprobar que sólo existe un archivo css
  * Comprobar que se ha incluido el archivo com.apple.ibooks.display.xml en caso de que el libro tenga fuentes incrustadas (corrección automática)
  * Comprobar que se ha incluido el identificador único asignado por la web al nombre del archivo