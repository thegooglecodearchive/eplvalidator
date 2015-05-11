# QUE ES EPLVALIDATOR #
Se trata de un script en python que nos ayudará a detectar gran cantidad de fallos frecuentes en los epubs antes de publicarlos en la web.

# PRERREQUISITOS #
Al ser un script de python, es multiplataforma. Puede ser ejecutado en Windows, OSX y Linux sin problema. Sin embargo requerirá que tengamos instalado en nuestra máquina un intérprete de python 3. Hoy en día, normalmente todos tenemos instalado un intérprete de python 2.x. Sin embargo esto no será suficiente, debemos instalar un intérprete de python 3 (en las pruebas se está usando python 3.3, así que recomiendo esta versión). Para comprobar si tenemos python3 instalado, y ver qué versión en concreto, podemos ejecutar en la línea de comandos:

> `python3 --version`

Si obtenemos algo así como:

> `python3 no se reconoce como un comando interno...”`

o bien:

> `bash: python3: command not found”`
> Nota: el mensaje en concreto dependerá del SO y del idioma que estéis utilizando

significa que NO tenemos un interprete de python 3 instalado. En caso de que tengamos uno, la salida nos mostrará el número de versión.

Si obtienes un error de este tipo:

> `Error: failed to import settings module (No module named '_tkinter', please install the python-tk package)Traceback (most recent call last):`

probablemente el problema es que no tienes la librería tkinter instalada. En Ubuntu se soluciona con el siguiente comando:

> `sudo apt-get install python3-tk`

Si no disponemos del interprete de python 3, debemos visitar http://python.org/download/ y descargar e instalar la versión correspondiente a nuestro sistema operativo (recomiendo instalar la 3.3.1 o posterior).

# USUARIOS DE WINDOWS #

Si eres usuario de windows y no sabes o no quieres instalar Python 3, tienes a tu disposición en la sección de descargas una versión compilada del script con todo lo necesario para ejecutarse (cortesía de nuestro amigo Yorik). Descárgala, descomprime el archivo y ejecútalo directamente.

# USUARIOS DE OSX #

Actualmente estoy intentando preparar una versión equivalente a la de windows, pero para OSX, en la que no sea necesario tener instalado el interprete de python 3. Por desgracia no está lista todavía. En el futuro estará disponible en la sección de descargas.

# MODO DE EMPLEO: #

El script tiene dos modos de empleo

## Modo 1. Validar un único archivo ##

Ejecutamos el script bien haciendo doble click sobre él (sólo Windows), o bien desde la linea de comandos sin ningún argumento adicional "python3 eplvalidator.py"

Nos mostrará una pantalla de selección de archivos. Buscamos el epub que deseamos validar y pulsamos aceptar.

Se ejecutará el script y nos mostrará los errores detectados en una nueva pantalla.

_Nota: Si nos da algún error relacionado con la librería Tkinter, es muy probable que estemos intentando ejecutar con una versión 2.x de Python. Por favor vuelve al primer paso y verifica que tienes instalado Python 3.x_

## Modo 2. Validar todos los archivos dentro de un directorio ##

Ejecutamos el script desde la línea de comandos, poniendo como argumento la ruta al directorio donde se encuentran los epubs que deseamos validar. Por ejemplo algo así como “python3 eplvalidator.py /home/monthy/EPL/libros\_pendientes”

El script ejecutará la validación sobre todos los epubs que encuentre en dicho directorio y nos mostrará una pantalla con los resultados.

_¡CUIDADO!: Si la ruta o el nombre del archivo contienen espacios, deberás colocarlo entre comillas dobles, por ejemplo "c:\Mi directorio\Libro a validar.epub"_

# FALSOS POSITIVOS #

En caso que el programa os reporte errores en los epubs que pensáis que son incorrectos, por favor informad de ello creando un nuevo tiquet, incluyendo a ser posible el epub que dio el falso positivo.