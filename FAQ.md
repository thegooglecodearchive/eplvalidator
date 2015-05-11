

## ¿Para qué sirve eplvalidator? ##

Se trata de una herramienta útil para detectar pequeños fallos tontos que se nos suelen pasar al maquetar epubs con la plantilla de EPL

## ¿Detectará errores en el código xml o en la estructura general del ePub? ##

De momento esto no está implementado, aunque en el futuro posiblemente se incluirá esta funcionalidad.

## El validador me informa de que hay errores en las etiquetas del epub, sin embargo a mi me parece que son correctas. ¿Qué está pasando? ##

Las etiquetas (tipo, genero y subgénero) deben estar escritas exactamente tal como aparecen en la lista oficial de la web, separadas por comas, y con un espacio tras cada coma. Si las escribimos en minúsculas, sin tildes, o con una grafía diferente, el validador nos reportará el error.

## El validador me informa de que el formato del nombre de archivo es incorrecto, pero yo lo veo bien. ¿Cuál puede ser el problema? ##

Si también se han detectado caracteres no válidos en el nombre de archivo, el validador también reportará fallo en el formato del nombre, ya que al estar los caracteres no válidos por medio, no detecta bien la estructura del nombre. Una vez eliminemos los caracteres no válidos, este fallo desaparecerá también.

## ¿Realiza alguna modificación en mis epubs? ##

A partir de la versión 1.10, el validador puede corregir ciertos errores de manera automática, por ejemplo, marcar el cover.jpg como imagen de portada, cambiar el UUID si se ha dejado el del epub base, etc... Siempre que realice una modificación, nos informará del error detectado y de que ha sido corregido en el reporte de errores.

No obstante, si no queremos que el validador modifique nada, basta con desactivar esta opción cambiando la linea:
```
corregir_errores = True
```
por esta otra:
```
corregir_errores = False
```