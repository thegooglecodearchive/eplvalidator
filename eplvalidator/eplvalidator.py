#!/usr/bin/env python
# -*- coding: utf-8
'''
EPLValidator
Created on May 16, 2013

@author: betatron

Ver changelog.txt para listado de pruebas implementadas y pendientes

'''

import sys
import zipfile
import fnmatch
import shutil
import string
import os.path
import re
import struct
from datetime import date
from datetime import datetime
from xml.dom import minidom

try:
    from tkinter import Tk, filedialog
except ImportError as exc:
    sys.stderr.write("Error: failed to import settings module ({})".format(exc))
    pass #podemos seguir ejecutándolo sin tkinter

#Constantes globales
#-------------------
version = 1.05

uuid_epubbase = 'urn:uuid:125147a0-df57-4660-b1bc-cd5ad2eb2617'
uuid_epubbase_2 = 'urn:uuid:00000000-0000-0000-0000-000000000000'

#Géneros y subgéneros:
tipo = ['Ficción', 'No Ficción']

generos_ficcion = ['Guion', 'Novela', 'Poesía', 'Relato', 'Teatro']

generos_no_ficcion = ['Crónica', 'Divulgación', 'Ensayo', 'Referencia']

subgeneros_ficcion = ['Aventuras', 'Bélico', 'Ciencia ficción', 'Didáctico',
                      'Drama', 'Erótico', 'Fantástico', 'Filosófico',
                      'Histórico','Humor', 'Infantil', 'Interactivo', 'Intriga',
                      'Juvenil', 'Policial', 'Psicológico', 'Realista',
                      'Romántico', 'Sátira', 'Terror', 'Otros']
             
subgeneros_no_ficcion = ['Arte', 'Autoayuda', 'Ciencias exactas', 'Ciencias naturales',
                         'Ciencias sociales', 'Comunicación', 'Crítica y teoría literaria', 'Deportes y juegos',
                         'Diccionarios y enciclopedias', 'Espiritualidad', 'Filosofía', 'Historia',
                         'Hogar', 'Humor', 'Idiomas', 'Manuales y cursos', 'Memorias',
                         'Padres e hijos', 'Psicología', 'Salud y bienestar', 'Sexualidad',
                         'Tecnología', 'Viajes', 'Otros' ]

generos = generos_ficcion + generos_no_ficcion #todos los géneros

generos_y_subgeneros_ficcion = generos_ficcion + subgeneros_ficcion #todos los generos y subgeneros de ficción

generos_y_subgeneros_no_ficcion = generos_no_ficcion + subgeneros_no_ficcion #todos los géneros y subgéneros de ficción

#todos los géneros y subgéneros EXCLUSIVOS de Ficción
excl_generos_y_subgeneros_ficcion = [e for e in generos_y_subgeneros_ficcion if e not in generos_y_subgeneros_no_ficcion]

#todos los géneros y subgéneros EXCLUSIVOS de No Ficción
excl_generos_y_subgeneros_no_ficcion = [e for e in generos_y_subgeneros_no_ficcion if e not in generos_y_subgeneros_ficcion]

subgeneros = list(set(subgeneros_ficcion + subgeneros_no_ficcion)) #subgéneros sin repetición

#idiomas aceptados hasta la fecha
#Alemán, Catalán, Español, Euskera, Francés, Gallego, Inglés, Italiano, Mandarín, Sueco 
idiomas = ['de', 'ca', 'es', 'eu', 'fr', 'gl', 'en', 'it', 'zh', 'sv' ]

#Otras:
caracteres_permitidos = string.ascii_letters + string.digits + ' _-[]().,&:' #Lista de caracteres permitidos en nombres de archivo

#Variables globales
lChapters = list() #lista con todos los capítulos del epub
lImages = list() #lista con todas las imágenes del epub
lSpine = list()

lista_errores = list()

#Funciones auxiliares
#--------------------
def locate(pattern, root=os.curdir):
    """Localiza todos los archivos que coinciden con cierto patrón
    
    Args:
        patter: patrón que queremos localizar
        root: directorio donde se intentan localizar los archivos. Por defecto es el directorio actual
        
    Returns:
        generador con los archivos encontrados
"""
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)

            
def clean_dir(dir):
    """Borra el directorio y todo su contenido@
    
    Args:
        dir: ruta del directorio a borrar
    """
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)


def recursive_zip(zipf, directory, folder=None):
    """comprimir archivos. De momento no la usamos
    en el futuro podria usarse para corregir algunos de los fallos detectados
    y generar un nuevo epub"""
    nodes = os.listdir(directory)
    for item in nodes:
        if os.path.isfile(directory + '/' + item):
            zipf.write(directory + '/' + item, folder + '/' + item + '/', zipfile.ZIP_DEFLATED)
        elif os.path.isdir(directory + '/' + item):
            recursive_zip(zipf, os.path.join(directory, item), folder + '/' + item)

def file_as_to_author(autor):
    if autor != '':
        if autor.count(',') != 1:
            lista_errores.append("ERROR: File-as (%s) incorrecto. Falta coma de separación o hay más de una coma" % autor)
            return None
        author_sort = autor.split(', ')
        return author_sort[1] + ' ' + author_sort[0]
    else:
        return None

#Funciones para comprobaciones en los epubs
def comprobar_portada_semantics():
    elem = xmldoc_opf.getElementsByTagName('metadata') #obtiene metadatos
    for node in elem[0].childNodes:
        if node.nodeName == 'meta':
            if node.getAttribute('name') == 'cover':
                if node.getAttribute('content') == 'cover.jpg':
                    return True
    lista_errores.append("ERROR: Falta marcar cover.jpg como imagen de portada")

def comprobar_generos_y_subgeneros():
    elem = xmldoc_opf.getElementsByTagName('metadata') #obtiene metadatos
    for node in elem[0].childNodes:
        if node.nodeName == 'dc:subject':
            etiquetas = node.firstChild.nodeValue.split(', ')
            #comprueba que hay al menos un género
            if not set(etiquetas).intersection(generos):
                lista_errores.append("ERROR: Falta género o género erróneo")
            #comprueba que hay al menos un subgénero
            if not set(etiquetas).intersection(subgeneros):
                lista_errores.append("ERROR: Falta subgénero o subgénero erróneo")
            #si se ha añadido la etiqueta Ficción, entonces comprueba que no hay asignados géneros y subgéneros de No ficción
            if tipo[0] in etiquetas:
                if (set(etiquetas).intersection([item for item in subgeneros_no_ficcion if item not in subgeneros_ficcion])):
                    lista_errores.append("ERROR: Subgéneros de no ficción utilizado en libro de ficción")
                if set(etiquetas).intersection(generos_no_ficcion):
                    lista_errores.append("ERROR: Géneros de no ficción utilizado en libro de ficción")
            #si se ha añadido la etiqueta No ficción, entonces comrpueba que no hay asignados géneros y subgéneros de Ficción
            if tipo[1] in etiquetas:
                if (set(etiquetas).intersection([item for item in subgeneros_ficcion if item not in subgeneros_no_ficcion])):
                    lista_errores.append("ERROR: Subgéneros de ficción utilizado en libro de no ficción")
                if set(etiquetas).intersection(generos_ficcion):
                    lista_errores.append("ERROR: Géneros de ficción utilizado en libro de no ficción")
            #comprueba si hay mezclados géneros de ficción y no ficción
            if set(etiquetas).intersection(excl_generos_y_subgeneros_ficcion) and set(etiquetas).intersection(excl_generos_y_subgeneros_no_ficcion):
                lista_errores.append("ERROR: uso simultáneo de géneros de Ficción y No ficción")
            #Comprueba si hay alguna etiqueta que no aparece en ninguna de las listas    
            for etiq in etiquetas:
                if etiq not in (tipo + generos + subgeneros):
                    lista_errores.append("ERROR: Género '" + etiq + "' no está en la lista de géneros aceptados por la web")

def comprobar_file_size():
    for f in locate("*.*", tempdir):
        if os.path.getsize(f) > 307200:
            lista_errores.append("ERROR: El tamaño del archivo " + os.path.basename(f) + " excede de 300 KB")
    
    
def comprobar_file_as():
    elem = xmldoc_opf.getElementsByTagName('metadata') #obtiene metadatos
    for node in elem[0].childNodes:
        if (node.nodeName == 'dc:creator') or (node.nodeName =='dc:contributor'):
            atr_fileas = node.getAttribute('opf:file-as')
            if atr_fileas == "":
                lista_errores.append("ERROR: Falta File-as para el autor o colaborador " +  node.firstChild.nodeValue)


def comprobar_nombre_archivo():
    if not all([c in caracteres_permitidos for c in os.path.basename(sourcefile)]):
        lista_errores.append("ERROR: Caracteres no permitidos en nombre de archivo")

def comprobar_nombre_archivos_internos():
    for f in locate("*.*", tempdir):
        if not all([c in caracteres_permitidos for c in os.path.basename(f)]):
            lista_errores.append("ERROR: Caracteres no permitidos en nombre de archivo interno " + os.path.basename(f))

def comprobar_bookid():
    """comprueba que el book-id es diferente del epub-base y que es el mismo en content.opf y toc.ncx"""
    node = xmldoc_opf.getElementsByTagName('dc:identifier')
    if (node[0].firstChild.nodeValue == uuid_epubbase) or (node[0].firstChild.nodeValue == uuid_epubbase_2):
        lista_errores.append("ERROR: el bookID coincide con el del epub base. Debe cambiarse para cada aporte")
    elif node[0].firstChild.nodeValue == "":
        lista_errores.append('ERROR: bookID no encontrado')
    else:
        nodes_ncx = xmldoc_ncx.getElementsByTagName('meta')
        for n in nodes_ncx:
            if n.getAttribute('name') == 'dtb:uid':
                if n.getAttribute('content') != node[0].firstChild.nodeValue:
                    lista_errores.append('ERROR: bookID en toc.ncx diferente del bookID en content.opf')
        

def comprobar_etiquetas():
    pattern = re.compile("<[ib]>")
    for f in lChapters:
        for i, line in enumerate(open(tempdir + f, "r", encoding="utf-8")):
        #for i, line in enumerate(open(tempdir + f, "r")):   #python 2.7 
            for match in re.finditer(pattern, line):
                lista_errores.append('ERROR: Encontrada etiqueta no permitidas en la linea %s del archivo %s' % (i+1, f))

def get_version_from_filename(epub):
    pattern = "\(r([0-9]\.[0-9])[^\)]*\).epub"
    m = re.search(pattern,epub)
    if m is None:
        print("ERROR: version no encontrada en el nombre de archivo")
    else:
        return m.group(1) 
    
def get_version_from_title_page(epub):
    elem = xmldoc_opf.getElementsByTagName('itemref') #get spine
    title_id = elem[2].getAttribute('idref')
    elem = xmldoc_opf.getElementsByTagName('manifest')
    for n in elem[0].childNodes:
        if n.nodeName == 'item':
            if n.getAttribute('id') == title_id:
                title_file = n.getAttribute('href')    
    f = open(tempdir + dir + title_file, "r", encoding="utf-8")
    #f = open(tempdir + dir + title_file, "r") #python 2.7
    pattern = '<p class="trevision"><strong class="sans">eP(UB|ub) r([0-9].[0-9])</strong></p>'
    for line in f:
        m = re.search(pattern, line)
        if not m is None:
            return m.group(2) 
    lista_errores.append("ERROR: No se ha detectado correctamente la versión en la página de título. Es posible que haya algún error en el formato")
   

def comprobar_version_coincidente(epub):
    v_nombre_archivo = get_version_from_filename(epub)
    v_pagina_titulo = get_version_from_title_page(epub)
    if  v_nombre_archivo != v_pagina_titulo:
        lista_errores.append('ERROR: La versión en nombre de archivo (%s) difiere de la versión en la página de título (%s)' % (v_nombre_archivo, v_pagina_titulo))

def comprobar_formato_nombre_archivo():
    #[saga larga] Apellido, Nombre - Titulo (rx.x texto_opcional).epub
    pattern1 = "\[[\w\s\-\.]+\] ([\w\s\-\.]+, [\w\s\-\.]+)( & [\w\s\-\.]+, [\w\s\-\.]+)* - [\w\s\-\.,:]+ \(r\d\.\d\s?[\w\s\-\.]*\)\.epub"
    #Apellido, Nombre - [saga número] Titulo (rx.x texto_opcional).epub
    pattern2 = "([\w\s\-\.]+, [\w\s\-\.]+)( & [\w\s\-\.]+, [\w\s\-\.]+)* - \[[\w\s\-\.]+\] [\w\s\-\.,:]+ \(r\d\.\d\s?[\w\s\-\.]*\)\.epub"
    #Apellido, Nombre - Titulo (rx.x texto_opcional).epub
    pattern3 = "([\w\s\-\.]+, [\w\s\-\.]+)( & [\w\s\-\.]+, [\w\s\-\.]+)* - [\w\s\-\.,:]+ \(r\d\.\d\s?[\w\s\-\.]*\)\.epub"
    m = re.search(pattern1,epub)
    if m is None:
        m = re.search(pattern2, epub)
        if m is None:
            m = re.search(pattern3, epub)
            if m is None:
                lista_errores.append("ERROR: El formato del nombre de archivo no es correcto")

def comprobar_metadatos_obligatorios():
    elem = xmldoc_opf.getElementsByTagName('metadata') #obtiene metadatos
    metadatos_obligatorios = ['título', 'autor', 'idioma', 'editorial', 'publicación', 'modificación', 'descripción']
    for node in elem[0].childNodes:
        
        if node.nodeName == 'dc:title':
            if node.firstChild.nodeValue == 'Título': #hemos olvidado sustituir el título por defecto del epub base
                lista_errores.append("ERROR: El título que aparece en los metadatos es el del epub base")
            else:
                metadatos_obligatorios.remove('título')
        
        elif (node.nodeName == 'dc:creator') and (node.getAttribute('opf:role') == 'aut'):
            if node.firstChild.nodeValue == 'Autor': #hemos olvidado sustituir el autor por defecto del epub base
                lista_errores.append("ERROR: El autor que aparece en los metadatos es el del epub base")
            else:
                if 'autor' in metadatos_obligatorios:
                    metadatos_obligatorios.remove('autor')
        
        elif node.nodeName == 'dc:language':
            if node.firstChild.nodeValue not in idiomas:
                lista_errores.append("ERROR: El idioma no es uno de los aceptados actualmente en la web")
            else:
                metadatos_obligatorios.remove('idioma')
        
        elif node.nodeName == 'dc:publisher':
            if node.firstChild.nodeValue != 'ePubLibre':
                lista_errores.append("ERROR: Editorial incorrecta. Debe ser ePubLibre")
            else:
                metadatos_obligatorios.remove('editorial')
                
        elif (node.nodeName == 'dc:date') and (node.getAttribute('opf:event') == 'modification'):
            metadatos_obligatorios.remove('modificación')
                
        elif (node.nodeName == 'dc:date') and (node.getAttribute('opf:event') == 'publication'):
            metadatos_obligatorios.remove('publicación')
                
        elif node.nodeName == 'dc:description':
            metadatos_obligatorios.remove('descripción')
        
    if metadatos_obligatorios != list():
        #esto es una guarrada, pero me estaba dando problemas al imprimir la lista, ya que contiene cadenas en unicode
        metadatos_erróneos = ''
        for x in metadatos_obligatorios:
            metadatos_erróneos = metadatos_erróneos + x + ', '
        lista_errores.append("ERROR: Los siguientes metadatos faltan o están erróneos: %s" % metadatos_erróneos[:-2])

def get_anyo_publicacion_from_info_page():
    elem = xmldoc_opf.getElementsByTagName('itemref') #get spine
    title_id = elem[3].getAttribute('idref')
    elem = xmldoc_opf.getElementsByTagName('manifest')
    for n in elem[0].childNodes:
        if n.nodeName == 'item':
            if n.getAttribute('id') == title_id:
                title_file = n.getAttribute('href')    
    f = open(tempdir + dir + title_file, "r", encoding="utf-8")
    #f = open(tempdir + dir + title_file, "r") #python 2.7
    pattern = '<p>[\w\s\.\-&;]+, (\d{4})</p>'
    for line in f:
        m = re.search(pattern, line)
        if not m is None:
            return int(m.group(1))
    lista_errores.append("ERROR: No se ha detectado correctamente el año de publicación en la página info. Es posible que haya algún error en el formato")

def comprobar_anyo_publicacion():
    elem = xmldoc_opf.getElementsByTagName('metadata') #obtiene metadatos
    for node in elem[0].childNodes:
        if (node.nodeName == 'dc:date') and (node.getAttribute('opf:event') == 'publication'):            
            anyo_info = get_anyo_publicacion_from_info_page()
            anyo_metadatos =  int(datetime.strptime(node.firstChild.nodeValue, '%Y-%m-%d').year)
            if  anyo_metadatos != anyo_info:
                lista_errores.append("ERROR: el año de publicación en los metadatos (%s) difiere del año en la página info (%s)" % (anyo_metadatos, anyo_info))
            if date.today().year < anyo_metadatos:
                lista_errores.append("ERROR: el año de publicación en los metadatos (%s) es posterior al año actual" % (anyo_metadatos))

def has_saga_in_filename():
    pattern = "\[[\w\s]+\]"
    m = re.search(pattern, epub)
    if m is None:
        return False
    else:
        return True
     
def comprobar_saga_en_metadatos():
    '''En caso de aparecer una saga en el nombre de archivo, nos dará un aviso si no hay etiqueta de saga en los metadatos. Esto técnicamente no es un error, pero es recomendable añadir esta etiqueta'''
    if has_saga_in_filename():
        elem = xmldoc_opf.getElementsByTagName('meta') #obtiene metadatos
        nodes = [node for node in elem if node.getAttribute('name') == 'calibre:series']
        if nodes == list():
            lista_errores.append('WARNING: No se ha indicado la saga en los metadatos mediante la etiqueta <meta content="XXX" name="calibre:series"/>')

def get_translator_from_info_page():
    elem = xmldoc_opf.getElementsByTagName('itemref') #get spine
    title_id = elem[3].getAttribute('idref')
    elem = xmldoc_opf.getElementsByTagName('manifest')
    for n in elem[0].childNodes:
        if n.nodeName == 'item':
            if n.getAttribute('id') == title_id:
                title_file = n.getAttribute('href')    
    f = open(tempdir + dir + title_file, "r", encoding="utf-8")
    #f = open(tempdir + dir + title_file, "r") #python 2.7
    pattern = '<p>Traducción: ([\w\s\.\-&;]+)( \([0-9]{4}\))?</p>'
    for line in f:
        m = re.search(pattern, line)
        if not m is None:
            return m.group(1)

def comprobar_traductor():
    elem = xmldoc_opf.getElementsByTagName('dc:contributor') #obtiene metadatos
    for node in elem:
        if (node.getAttribute('opf:role') == 'trl'):            
            traductor_info = get_translator_from_info_page()
            traductor_metadatos =  node.firstChild.nodeValue
            traductor_fileas = node.getAttribute('opf:file-as')
            traductor_fileas_invertido = file_as_to_author(traductor_fileas)
            
            if (traductor_metadatos is None) and (traductor_info is not None):
                lista_errores.append("ERROR: Falta el traductor en los metadatos")
            elif (traductor_metadatos is not None):
                if (traductor_info is None):
                    lista_errores.append("ERROR: Falta el traductor en la página info")
                if (traductor_fileas != '') and (traductor_fileas_invertido != traductor_metadatos):
                    lista_errores.append("ERROR: el File_as del traductor (%s) parece incorrecto al compararlo con el nombre de traductor (%s)" % (traductor_fileas, traductor_metadatos))
            elif  traductor_metadatos != traductor_info:
                lista_errores.append("ERROR: el traductor en la página info (%s) no coincide con el traductor en los metadatos (%s)" % (traductor_info, traductor_metadatos))
    
def get_jpg_size(jpeg):
    '''
    obtiene el tamaño de un jpeg, de una manera un poco chapucera pero funciona
    '''
    jpeg.read(2)
    b = jpeg.read(1)
    try:
        while (b and ord(b) != 0xDA):
            while (ord(b) != 0xFF): b = jpeg.read(1)
            while (ord(b) == 0xFF): b = jpeg.read(1)
            if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                jpeg.read(3)
                h, w = struct.unpack(">HH", jpeg.read(4))
                break
            else:
                jpeg.read(int(struct.unpack(">H", jpeg.read(2))[0])-2)
            b = jpeg.read(1)
        width = int(w)
        height = int(h)
        return (width, height)
    except struct.error:
        pass
    except ValueError:
        pass

def comprobar_size_portada():
    ruta = tempdir + '/OEBPS/Images/cover.jpg'
    with open(ruta, 'rb') as f:
        cover_size = get_jpg_size(f)
    if  cover_size != (600, 900):
        lista_errores.append("ERROR: El tamaño de la portada (%s) es incorrecto" % str(cover_size))

def get_author_from_info_page():
    elem = xmldoc_opf.getElementsByTagName('itemref') #get spine
    title_id = elem[3].getAttribute('idref')
    elem = xmldoc_opf.getElementsByTagName('manifest')
    for n in elem[0].childNodes:
        if n.nodeName == 'item':
            if n.getAttribute('id') == title_id:
                title_file = n.getAttribute('href')    
    f = open(tempdir + dir + title_file, "r", encoding="utf-8")
    #f = open(tempdir + dir + title_file, "r") #python 2.7
    pattern = '<p>([\w\s\.\-&;]+), [0-9]{4}</p>'
    for line in f:
        m = re.search(pattern, line)
        if not m is None:
            return m.group(1)

def get_author_from_metadata():
    elem = xmldoc_opf.getElementsByTagName('dc:creator') #obtiene metadatos
    for node in elem:
        if (node.getAttribute('opf:role') == 'aut'):
            author_fileas = node.getAttribute('opf:file-as')
            author_fileas_invertido = file_as_to_author(author_fileas)
            if author_fileas_invertido != node.firstChild.nodeValue:
                lista_errores.append("ERROR: el File_as del autor (%s) parece incorrecto al compararlo con el nombre de autor (%s)" % (author_fileas, node.firstChild.nodeValue))
            return node.firstChild.nodeValue
        
def get_author_sort_from_metadata():
    elem = xmldoc_opf.getElementsByTagName('dc:creator') #obtiene metadatos
    for node in elem:
        if (node.getAttribute('opf:role') == 'aut'):
            return node.getAttribute('opf:file-as')

def get_author_from_title():
    elem = xmldoc_opf.getElementsByTagName('itemref') #get spine
    title_id = elem[2].getAttribute('idref')
    elem = xmldoc_opf.getElementsByTagName('manifest')
    for n in elem[0].childNodes:
        if n.nodeName == 'item':
            if n.getAttribute('id') == title_id:
                title_file = n.getAttribute('href')    
    f = open(tempdir + dir + title_file, "r", encoding="utf-8")
    pattern = '<p class="tautor"><code class="sans">([\w\s\.\-&;]+)</code></p>'
    for line in f:
        m = re.search(pattern, line)
        if not m is None:
            return m.group(1)
    
                
def comprobar_autor():
    '''Comprobamos que el autor coincide con el file-as y además coincide con el que aparece en la página de título e info
    '''
    author_title = get_author_from_title()
    author_metadata = get_author_from_metadata()
    author_info = get_author_from_info_page()
    author_sort = file_as_to_author(get_author_sort_from_metadata())
    if author_metadata != author_title:
        lista_errores.append("ERROR: El nombre del autor en la página de título (%s) difiere de los metadatos (%s)" % (author_title, author_metadata))
    if author_metadata != author_info: 
        lista_errores.append("ERROR: El nombre del autor en la página de info (%s) difiere de los metadatos (%s)" % (author_info, author_metadata))
    if author_metadata != author_sort:
        lista_errores.append("ERROR: El nombre del autor en el author_sort (%s) difiere de los metadatos (%s)" % (author_sort, author_metadata))

def get_title_from_title_page():
    elem = xmldoc_opf.getElementsByTagName('itemref') #get spine
    title_id = elem[2].getAttribute('idref')
    elem = xmldoc_opf.getElementsByTagName('manifest')
    for n in elem[0].childNodes:
        if n.nodeName == 'item':
            if n.getAttribute('id') == title_id:
                title_file = n.getAttribute('href')    
    with open(tempdir + dir + title_file, "r", encoding="utf-8") as f:
        pattern = '<h1 class="ttitulo"><strong class="sans">([\w\s\.\-&;,«»\?¿]+)</strong></h1>'
        for line in f:
            m = re.search(pattern, line)
            if not m is None:
                return m.group(1) 
    lista_errores.append("ERROR: No se ha detectado correctamente el título en la página de título. Es posible que haya algún error en el formato")

def get_title_from_metadata():
    elem = xmldoc_opf.getElementsByTagName('dc:title') #obtiene metadatos
    return elem[0].firstChild.nodeValue
    
def comprobar_titulo():
    titulo_metadata = get_title_from_metadata()
    titulo_titlepage = get_title_from_title_page()
    if titulo_metadata != titulo_titlepage:
        lista_errores.append("ERROR: título en los metadatos (%s) difiere del título en la página de título (%s)" % (titulo_metadata, titulo_titlepage))
         
if len(sys.argv) == 1:
    Tk().withdraw() # No necesitamos un GUI completo, así que no mostramos la ventana principal
    filename = filedialog.askopenfilename() # Muestra el diálogo y devuelve el nombre del archivo seleccionado
    files = [filename]
    (sdir, sfile) = os.path.split(filename)
    tempdir = sdir + '/temp/' #directorio temporal para descomprimir el epub 
    
elif len(sys.argv) == 2:     
    sdir = sys.argv[1] #directorio con los epubs a procesar
    if os.path.isdir(sdir):
        tempdir = sdir + '/temp/' #directorio temporal para descomprimir el epub 
        files = locate("*.epub",sdir)
    elif os.path.isfile(sdir):
        files = [sdir]
        (sdir, sfile) = os.path.split(sdir)
        tempdir = sdir + '/temp/' #directorio temporal para descomprimir el epub 
    else:
        print("Argumentos incorrectos. ABORTADO")
        sys.exit() 
else:
    print("Numero de argumentos erróneo. ABORTADO")
    sys.exit() 
                
#BUCLE PRINCIPAL                    

for epub in files: 
    sourcefile = epub
    destinationfilename = sourcefile
    if sourcefile:  
        print('Comprobando: '  + os.path.basename(sourcefile))  
        zipf = zipfile.ZipFile(sourcefile,"r") 
        clean_dir(tempdir) #borramos contenido del directorio temporal
        zipf.extractall(tempdir) #descomprimimos el archivo
        zipf.close()
        
        with open(tempdir + 'META-INF/container.xml') as f: #buscamos la ruta del content.opf en el container.xml
            xmldoc = minidom.parse(f)
        elem = xmldoc.getElementsByTagName('rootfile')
        attr = elem[0].getAttribute('full-path')
        dir = os.path.dirname(attr) + '/'
        with open(tempdir + attr, "r", encoding="utf-8") as f: #abrimos el content.opf
            xmldoc_opf = minidom.parse(f) #Lo parseamos y lo dejamos en memoria, ya que la mayoría de comprobaciones lo necesitan        
        with open(tempdir + dir + 'toc.ncx', "r", encoding="utf-8") as f: #abrimos el toc.ncx
            xmldoc_ncx = minidom.parse(f)
        elem = xmldoc_opf.getElementsByTagName('manifest') #obtenemos el manifiesto y registramos todos los capitulos e imágenes
        for n in elem[0].childNodes:
            if n.nodeName == 'item':
                node_type = n.getAttribute('media-type')
                if node_type == 'application/xhtml+xml':
                    lChapters.append(os.path.join(dir, n.getAttribute('href')))
                elif 'image' in node_type:
                    lImages.append(os.path.join(dir, n.getAttribute('href')))
        elem = xmldoc.getElementsByTagName('spine') #get spine        

        #-----Aquí irán las comprobaciones una a una
        comprobar_portada_semantics()    
        comprobar_generos_y_subgeneros()
        comprobar_file_size()
        comprobar_file_as()
        comprobar_nombre_archivo()
        comprobar_nombre_archivos_internos()
        comprobar_bookid() 
        comprobar_etiquetas()
        comprobar_version_coincidente(epub)     
        comprobar_formato_nombre_archivo()  
        comprobar_metadatos_obligatorios()
        comprobar_anyo_publicacion()
        comprobar_saga_en_metadatos()
        comprobar_traductor()
        comprobar_size_portada()
        comprobar_autor()
        comprobar_titulo()


        #imprimir los errores
        print('EPLValidator v%s' %version)
        if not lista_errores:
            print("todo está OK!")
        for e in lista_errores:
            print(e)
        lista_errores = list()
        lChapters = list()
        lImages = list()
        print("")
        shutil.rmtree(tempdir)
        
input("Presiona cualquier tecla para finalizar el programa...")