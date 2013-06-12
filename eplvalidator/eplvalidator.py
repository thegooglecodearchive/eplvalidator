#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
version = 1.09
version_plantilla = 'v1.0a'

#archivos principales
title_file = ""
info_file = ""

#errores
listaerrores = {1 : "File-as (%s) incorrecto. Falta coma de separación",
                2 : "Falta marcar cover.jpg como imagen de portada",
                3 : "Falta género o género erróneo",
                4 : "Falta subgénero o subgénero erróneo",
                5 : "Subgéneros de No ficción utilizado en libro de Ficción",
                6 : "Géneros de No ficción utilizado en libro de Ficción",
                7 : "Subgéneros de Ficción utilizado en libro de No ficción",
                8 : "Géneros de Ficción utilizado en libro de No ficción",
                9 : "Uso simultáneo de géneros de Ficción y No ficción",
                10 : "Género (%s) no está en la lista de géneros aceptados por la web",
                11 : "El tamaño del archivo interno %s excede de 300 KB",
                12 : "Falta File-as (Ordenar como) para el autor o colaborador %s",
                13 : "Caracteres no permitidos en nombre de archivo",
                14 : "Caracteres no permitidos en nombre de archivo interno %s",
                15 : "El bookID coincide con el del epub base. Debe cambiarse para cada nuevo aporte",
                16 : 'BookID no encontrado',
                17 : 'BookID en toc.ncx y content.opf son diferentes',
                18 : "Versión no encontrada en el nombre de archivo",
                19 : "No se ha detectado correctamente la versión en la página de título. Es posible que haya algún error en el formato",
                20 : "No se ha detectado correctamente la fecha en la página de título. Es posible que haya algún error en el formato",
                21 : "No se ha detectado correctamente la fecha de modificación en los metadatos",
                22 : "No se ha detectado correctamente la fecha de modificación en la página de título",
                23 : "La fecha de modificación en la página de título (%s) difiere de la fecha de modificación de los metadatos (%s)",
                24 : 'La versión en nombre de archivo (%s) difiere de la versión en la página de título (%s)',
                25 : "El formato del nombre de archivo no es correcto",
                26 : "El título que aparece en los metadatos es el del epub base",
                27 : "El autor que aparece en los metadatos es el del epub base",
                28 : "El idioma (%s) no es uno de los aceptados actualmente en la web",
                29 : "Editorial incorrecta. Debe ser ePubLibre (respetando las mayúsculas)",
                30 : "Los siguientes metadatos faltan o están erróneos: %s",
                31 : "No se ha detectado correctamente el año de publicación en la página info. Es posible que haya algún error en el formato",
                32 : "El año de publicación en los metadatos (%s) difiere del año en la página info (%s)",
                33 : "El año de publicación en los metadatos (%s) es posterior al año actual",
                34 : 'No se ha indicado la saga en los metadatos mediante la etiqueta <meta content="XXX" name="calibre:series"/>',
                35 : "Falta el traductor en los metadatos",
                36 : "Falta el traductor en la página info",
                37 : "El File_as (Ordenar como) del traductor (%s) parece incorrecto al compararlo con el nombre de traductor (%s)",
                38 : "El traductor en la página info (%s) no coincide con el traductor en los metadatos (%s)",
                39 : "Hay algún problema con el formato del archivo cover.jpg. No se ha podido detectar su tamaño",
                40 : "El tamaño de la portada (%s) es incorrecto. Debe ser 600 x 900",
                41 : "El File_as (Ordenar como) del autor (%s) parece incorrecto al compararlo con el nombre de autor (%s)",
                42 : "El nombre del autor en la página de título (%s) difiere de los metadatos (%s)",
                43 : "El nombre del autor en la página de info (%s) difiere de los metadatos (%s)",
                44 : "No se ha detectado correctamente el título en la página de título. Es posible que haya algún error en el formato",
                45 : "Título en los metadatos (%s) difiere del título en la página de título (%s)",
                46 : 'Encontrada etiqueta o estilo no permitido (%s) en la linea %s del archivo %s',
                47 : 'El identificador único del ePub debe ser del tipo UUID',
                48 : 'No se ha encontrado el nick del editor en la página de título',
                49 : 'No se ha encontrado el nick del editor en la página de info',
                50 : 'El editor en la página de título (%s) no coincide con el de la página info (%s)',
                51 : 'El formato del UUID no es correcto (%s)',
                52 : 'Se ha encontrado más de un archivo .css en el epub',
                53 : 'Metadato %s duplicado',
                54 : 'No se encuentra el archivo cover.jpg'}

uuid_epubbase = ['urn:uuid:125147a0-df57-4660-b1bc-cd5ad2eb2617', 'urn:uuid:00000000-0000-0000-0000-000000000000']

meses = ['enero', 'febrero' , 'marzo', 'abril', 'mayo', 'junio' , 'julio', 'agosto', 'septiembre' , 'octubre', 'noviembre', 'diciembre']

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
#Alemán, Catalán, Español, Euskera, Francés, Gallego, Inglés, Italiano, Mandarín, Sueco, Portugues 
idiomas = ['de', 'ca', 'es', 'eo', 'eu', 'fr', 'gl', 'en', 'it', 'zh', 'sv', 'pt' ]

#Otras:
caracteres_permitidos = string.ascii_letters + string.digits + " _-[]().,&:'" #Lista de caracteres permitidos en nombres de archivo

#Variables globales
lChapters = list() #lista con todos los capítulos del epub
lImages = list() #lista con todas las imágenes del epub
lSpine = list()

lista_errores = list()

#Funciones auxiliares
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
        if autor.count(',') < 1:
            lista_errores.append('ERROR 001: ' + listaerrores[1] % autor)
            return None
        
        authors = autor.split(' & ')
        autor_invertido = ''
        for a in authors:
            if autor_invertido != '':
                autor_invertido = autor_invertido + ' & '
            a_sort = a.split(', ')
            if len(a_sort) > 1:
                a_invertido = a_sort[1] + ' ' + a_sort[0]
                autor_invertido = autor_invertido + a_invertido
            else:
                a_invertido = a_sort 
             
        return autor_invertido
    else:
        return None

#obtención de datos básicos
def get_info_file_name():
    #elem = xmldoc_opf.getElementsByTagName('itemref') #get spine
    title_id = 'info.xhtml'
    elem = xmldoc_opf.getElementsByTagName('manifest')
    for n in elem[0].childNodes:
        if n.nodeName == 'item':
            if n.getAttribute('id') == title_id:
                return(n.getAttribute('href'))    

def get_title_file_name():
    elem = xmldoc_opf.getElementsByTagName('itemref') #get spine
    title_id = elem[2].getAttribute('idref')
    elem = xmldoc_opf.getElementsByTagName('manifest')
    for n in elem[0].childNodes:
        if n.nodeName == 'item':
            if n.getAttribute('id') == title_id:
                return(n.getAttribute('href'))    

def get_version_from_filename(epub):
    pattern = "\(r([0-9]\.[0-9])[^\)]*\).epub"
    m = re.search(pattern,epub)
    if m is None:
        lista_errores.append('ERROR 018: ' + listaerrores[18])
    else:
        return m.group(1)
    
def get_editor_from_title_page():
    global title_file
    if title_file == "":
        title_file = get_title_file_name()
        
    with open(tempdir + dir + title_file, "r", encoding="utf-8") as f:
        pattern = '<p class="tfirma"><strong class="sans">([^<]+)</strong>'
        for line in f:
            m = re.search(pattern, line)
            if not m is None:
                titulo = m.group(1)
                return titulo
    lista_errores.append('ERROR 048: ' + listaerrores[48])
    
def get_editor_from_info_page():
    global info_file
    if info_file == "":
        info_file = get_info_file_name()
    with open(tempdir + dir + info_file, "r", encoding="utf-8") as f:
        pattern = '<p class="salto10">(Editor digital|Digital editor): ([^<]+)(, .*)?</p>'
        for line in f:
            m = re.search(pattern, line)
            if not m is None:
                titulo = m.group(2)
                return titulo
    lista_errores.append('ERROR 049: ' + listaerrores[49])
   
#Funciones para comprobaciones en los epubs
def comprobar_editor_en_titulo_e_info():
    editor_titulo = get_editor_from_title_page()
    editor_info =get_editor_from_info_page()
    if (editor_titulo and editor_info and (editor_titulo != editor_info)):
        lista_errores.append('ERROR 050: ' + listaerrores[50] %(editor_titulo, editor_info))
    
def comprobar_portada_semantics():
    elem = xmldoc_opf.getElementsByTagName('metadata') #obtiene metadatos
    for node in elem[0].childNodes:
        if node.nodeName == 'meta':
            if node.getAttribute('name') == 'cover':
                if node.getAttribute('content') == 'cover.jpg':
                    return True
    lista_errores.append('ERROR 002: ' + listaerrores[2])

def comprobar_generos_y_subgeneros():
    elem = xmldoc_opf.getElementsByTagName('metadata') #obtiene metadatos
    for node in elem[0].childNodes:
        if node.nodeName == 'dc:subject':
            etiquetas = node.firstChild.nodeValue.split(', ')
            #comprueba que hay al menos un género
            if not set(etiquetas).intersection(generos):
                lista_errores.append('ERROR 003: ' + listaerrores[3])
            #comprueba que hay al menos un subgénero
            if not set(etiquetas).intersection(subgeneros):
                lista_errores.append('ERROR 004: ' + listaerrores[4])
            #si se ha añadido la etiqueta Ficción, entonces comprueba que no hay asignados géneros y subgéneros de No ficción
            if tipo[0] in etiquetas:
                if (set(etiquetas).intersection([item for item in subgeneros_no_ficcion if item not in subgeneros_ficcion])):
                    lista_errores.append('ERROR 005: ' + listaerrores[5])
                if set(etiquetas).intersection(generos_no_ficcion):
                    lista_errores.append('ERROR 006: ' + listaerrores[6])
            #si se ha añadido la etiqueta No ficción, entonces comrpueba que no hay asignados géneros y subgéneros de Ficción
            if tipo[1] in etiquetas:
                if (set(etiquetas).intersection([item for item in subgeneros_ficcion if item not in subgeneros_no_ficcion])):
                    lista_errores.append('ERROR 007: ' + listaerrores[7])
                if set(etiquetas).intersection(generos_ficcion):
                    lista_errores.append('ERROR 008: ' + listaerrores[8])
            #comprueba si hay mezclados géneros de ficción y no ficción
            if set(etiquetas).intersection(excl_generos_y_subgeneros_ficcion) and set(etiquetas).intersection(excl_generos_y_subgeneros_no_ficcion):
                lista_errores.append('ERROR 009: ' + listaerrores[9])
            #Comprueba si hay alguna etiqueta que no aparece en ninguna de las listas    
            for etiq in etiquetas:
                if etiq not in (tipo + generos + subgeneros):
                    lista_errores.append('ERROR 010: ' + listaerrores[10] % etiq)

def comprobar_file_size():
    for f in locate("*.*", tempdir):
        if os.path.getsize(f) > 307200:
            lista_errores.append('ERROR 011: ' + listaerrores[11] % os.path.basename(f))
    
    
def comprobar_file_as():
    elem = xmldoc_opf.getElementsByTagName('metadata') #obtiene metadatos
    for node in elem[0].childNodes:
        if (node.nodeName == 'dc:creator') or (node.nodeName =='dc:contributor'):
            atr_fileas = node.getAttribute('opf:file-as')
            if atr_fileas == "":
                lista_errores.append('ERROR 012: ' + listaerrores[12] %  node.firstChild.nodeValue)


def comprobar_nombre_archivo():
    if not all([c in caracteres_permitidos for c in os.path.basename(sourcefile)]):
        lista_errores.append('ERROR 013: ' + listaerrores[13])

def comprobar_nombre_archivos_internos():
    for f in locate("*.*", tempdir):
        if not all([c in caracteres_permitidos for c in os.path.basename(f)]):
            lista_errores.append('ERROR 014: ' + listaerrores[14] % os.path.basename(f))

def comprobar_bookid():
    """comprueba que el book-id es diferente del epub-base y que es el mismo en content.opf y toc.ncx"""
    node = xmldoc_opf.getElementsByTagName('dc:identifier')
    #comprueba si es del tipo UUID
    if (node[0].getAttribute('opf:scheme') != 'UUID'):
        lista_errores.append('ERROR 047: ' + listaerrores[47])
    #comprueba si es igual al del epubbase
    elif (node[0].firstChild.nodeValue in uuid_epubbase):
        lista_errores.append('ERROR 015: ' + listaerrores[15])
    #comrpueba si está relleno
    elif node[0].firstChild.nodeValue == "":
        lista_errores.append('ERROR 016: ' + listaerrores[16])
    else:
        #Comprobar formato correcto del UUID
        uuid4hex_pattern = 'urn:uuid:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
        m = re.search(uuid4hex_pattern, node[0].firstChild.nodeValue)
        if m is None:
            lista_errores.append('ERROR 051: ' + listaerrores[51] % node[0].firstChild.nodeValue)
        
        nodes_ncx = xmldoc_ncx.getElementsByTagName('meta')
        for n in nodes_ncx:
            if n.getAttribute('name') == 'dtb:uid':
                if n.getAttribute('content') != node[0].firstChild.nodeValue:
                    lista_errores.append('ERROR 017: ' + listaerrores[17])
        
 
def get_version_from_title_page(epub):
    global title_file
    if title_file == "":
        title_file = get_title_file_name()
    
    with open(tempdir + dir + title_file, "r", encoding="utf-8") as f:
        pattern = '<p class="trevision"><strong class="sans">eP(UB|ub) r([0-9].[0-9])</strong></p>'
        for line in f:
            m = re.search(pattern, line)
            if not m is None:
                return m.group(2) 
    lista_errores.append('ERROR 019: ' + listaerrores[19])

def get_modification_date_from_title_page():
    global title_file
    if title_file == "":
        title_file = get_title_file_name()
    with open(tempdir + dir + title_file, "r", encoding="utf-8") as f:
        pattern = '<p class="tfirma"><strong class="sans">[^<]+</strong> <code class="tfecha sans">(\d{2}\.\d{2}\.\d{2})</code></p>'
        for line in f:
            m = re.search(pattern, line)
            if not m is None:
                return datetime.strptime(m.group(1), '%d.%m.%y')
    lista_errores.append('ERROR 020: ' + listaerrores[20])

def get_modification_date_from_metadata():
    elem = xmldoc_opf.getElementsByTagName('dc:date') #obtiene metadatos
    for node in elem:
        if (node.getAttribute('opf:event') == 'modification'):
            return datetime.strptime(node.firstChild.nodeValue,'%Y-%m-%d')

def comprobar_fecha_modificacion():
    mdate_metadata = get_modification_date_from_metadata()
    mdate_title = get_modification_date_from_title_page()    
    if mdate_metadata != mdate_title:
        if mdate_metadata is None:
            lista_errores.append('ERROR 021: ' + listaerrores[21])
        elif mdate_title is None:
            lista_errores.append('ERROR 022: ' + listaerrores[22])
        else:
            lista_errores.append('ERROR 023: ' + listaerrores[23] % (mdate_title.date(), mdate_metadata.date()))

def comprobar_version_coincidente(epub):
    v_nombre_archivo = get_version_from_filename(epub)
    v_pagina_titulo = get_version_from_title_page(epub)
    if  v_nombre_archivo and v_pagina_titulo and (v_nombre_archivo != v_pagina_titulo):
        lista_errores.append('ERROR 024: ' + listaerrores[24] % (v_nombre_archivo, v_pagina_titulo))

def comprobar_formato_nombre_archivo():
    
    patterns = list()
    #[saga larga] Apellido, Nombre - Titulo (rx.x texto_opcional).epub
    patterns.append("\[[\w\s\-\.,]+\] ([\w\s\-\.]+, [\w\s\-\.]+)( & [\w\s\-\.]+, [\w\s\-\.]+)* - [\w\s\-\.,:]+ \(r\d\.\d\s?[\w\s\-\.]*\)\.epub")
    #Apellido, Nombre - [saga número] Titulo (rx.x texto_opcional).epub
    patterns.append("([\w\s\-\.]+, [\w\s\-\.]+)( & [\w\s\-\.]+, [\w\s\-\.]+)* - \[[\w\s\-\.,]+\] [\w\s\-\.,:]+ \(r\d\.\d\s?[\w\s\-\.]*\)\.epub")
    #Apellido, Nombre - Titulo (rx.x texto_opcional).epub
    patterns.append("([\w\s\-\.]+, [\w\s\-\.]+)( & [\w\s\-\.]+, [\w\s\-\.]+)* - [\w\s\-\.,:]+ \(r\d\.\d\s?[\w\s\-\.]*\)\.epub")
    #[saga larga] [subsaga número] Apellido, Nombre - Titulo (rx.x texto_opcional).epub
    patterns.append("\[[\w\s\-\.,]+\] [[\w\s\-\.,]+\] ([\w\s\-\.]+, [\w\s\-\.]+)( & [\w\s\-\.]+, [\w\s\-\.]+)* - [\w\s\-\.,:]+ \(r\d\.\d\s?[\w\s\-\.]*\)\.epub")

    for p in patterns:
        m = re.search(p,epub)
        if m is not None:
            return True
    lista_errores.append('ERROR 025: ' + listaerrores[25])

def comprobar_metadatos_obligatorios():
    elem = xmldoc_opf.getElementsByTagName('metadata') #obtiene metadatos
    metadatos_obligatorios = ['título', 'autor', 'idioma', 'editorial', 'publicación', 'modificación', 'descripción']
    for node in elem[0].childNodes:
        
        if node.nodeName == 'dc:title':
            if node.firstChild.nodeValue == 'Título': #hemos olvidado sustituir el título por defecto del epub base
                lista_errores.append('ERROR 026: ' + listaerrores[26])
            else:
                if 'título' in metadatos_obligatorios:
                    metadatos_obligatorios.remove('título')
        
        elif (node.nodeName == 'dc:creator') and (node.getAttribute('opf:role') == 'aut'):
            if node.firstChild.nodeValue == 'Autor': #hemos olvidado sustituir el autor por defecto del epub base
                lista_errores.append('ERROR 027: ' + listaerrores[27])
            else:
                if 'autor' in metadatos_obligatorios:
                    metadatos_obligatorios.remove('autor')
        
        elif node.nodeName == 'dc:language':
            if node.firstChild.nodeValue not in idiomas:
                lista_errores.append('ERROR 028: ' + listaerrores[28] % node.firstChild.nodeValue)
            else:
                if 'idioma' in metadatos_obligatorios:
                    metadatos_obligatorios.remove('idioma')
        
        elif node.nodeName == 'dc:publisher':
            if node.firstChild.nodeValue != 'ePubLibre':
                lista_errores.append('ERROR 029: ' + listaerrores[29])
            else:
                if 'editorial' in metadatos_obligatorios:
                    metadatos_obligatorios.remove('editorial')
                
        elif (node.nodeName == 'dc:date') and (node.getAttribute('opf:event') == 'modification'):
            if 'modificación' in metadatos_obligatorios:
                metadatos_obligatorios.remove('modificación')
                
        elif (node.nodeName == 'dc:date') and (node.getAttribute('opf:event') == 'publication'):
            if 'publicación' in metadatos_obligatorios:
                metadatos_obligatorios.remove('publicación')
                
        elif node.nodeName == 'dc:description':
            if 'descripción' in metadatos_obligatorios:
                metadatos_obligatorios.remove('descripción')
        
    if metadatos_obligatorios != list():
        #esto es una guarrada, pero me estaba dando problemas al imprimir la lista, ya que contiene cadenas en unicode
        metadatos_erroneos = ''
        for x in metadatos_obligatorios:
            metadatos_erroneos = metadatos_erroneos + x + ', '
        lista_errores.append('ERROR 030: ' + listaerrores[30] % metadatos_erroneos[:-2])

def get_anyo_publicacion_from_info_page():
    global info_file
    if info_file == "":
        info_file = get_info_file_name()
    with open(tempdir + dir + info_file, "r", encoding="utf-8") as f:
        patterns= list()
        patterns.append('<p>([\w\s\.\-&;\']+), ([0-9]{4})((-|/)(0[1-9]|1[0-2])((-|/)(0[1-9]|[1-2][0-9]|3[0-1]))?)?</p>')
        patterns.append('<p>[\w\s\.\-&;\']+, (' + '|'.join(meses) + ') de ([0-9]{4})</p>')
        for line in f:
            for pattern in patterns:
                m = re.search(pattern, line)
                if not m is None:
                    return int(m.group(2))
    lista_errores.append('ERROR 031: ' + listaerrores[31])

def get_anyo_metadatos():
    elem = xmldoc_opf.getElementsByTagName('metadata') #obtiene metadatos
    for node in elem[0].childNodes:
        if (node.nodeName == 'dc:date') and (node.getAttribute('opf:event') == 'publication'):            
            anyo = node.firstChild.nodeValue.split('-')[0]
            return int(datetime.strptime(anyo, '%Y').year)

def comprobar_anyo_publicacion():
    anyo_info = get_anyo_publicacion_from_info_page()
    anyo_metadatos = get_anyo_metadatos()
    if anyo_info and anyo_metadatos: 
        if  anyo_metadatos != anyo_info:
            lista_errores.append('ERROR 032: ' + listaerrores[32] % (anyo_metadatos, anyo_info))
        if date.today().year < anyo_metadatos:
            lista_errores.append('ERROR 033: ' + listaerrores[33] % (anyo_metadatos))

def has_saga_in_filename():
    pattern = "\[[\w\s\-,\.]+\]"
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
        if not nodes:
            lista_errores.append('ERROR 034: ' + listaerrores[34])

def get_translator_from_info_page():
    global info_file
    if info_file == "":
        info_file = get_info_file_name()
    with open(tempdir + dir + info_file, "r", encoding="utf-8") as f:
        pattern = '<p>Traducción: ([\w\s\.\-&;]+),?( \(?[0-9]{4}\)?)?</p>'
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
                lista_errores.append('ERROR 035: ' + listaerrores[35])
            elif (traductor_metadatos is not None):
                if (traductor_info is None):
                    lista_errores.append('ERROR 036: ' + listaerrores[36])
                if (traductor_fileas != '') and (traductor_fileas_invertido != traductor_metadatos):
                    lista_errores.append('ERROR 037: ' + listaerrores[37] % (traductor_fileas, traductor_metadatos))
            elif  traductor_metadatos != traductor_info:
                lista_errores.append('ERROR 038: ' + listaerrores[38] % (traductor_info, traductor_metadatos))
    
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
        try:
            width = int(w)
            height = int(h)
            return (width, height)
        except NameError:
            lista_errores.append('ERROR 039: ' + listaerrores[39])
            pass
    except struct.error:
        pass
    except ValueError:
        pass

def comprobar_size_portada():
    ruta = tempdir + '/OEBPS/Images/cover.jpg'
    try :
        with open(ruta, 'rb') as f:
            cover_size = get_jpg_size(f)
            if  cover_size != (600, 900):
                lista_errores.append('ERROR 040: ' + listaerrores[40] % str(cover_size))
    except IOError:
        lista_errores.append('ERROR 054: ' + listaerrores[54]) #no se encuentra cover.jpg
        

def get_author_from_info_page():
    global info_file
    if info_file == "":
        info_file = get_info_file_name()
    with open(tempdir + dir + info_file, "r", encoding="utf-8") as f:
        patterns = list()
        patterns.append('<p>([\w\s\.\-&;\']+), ([0-9]{4})((-|/)(0[1-9]|1[0-2])((-|/)(0[1-9]|[1-2][0-9]|3[0-1]))?)?</p>')
        patterns.append('<p>([\w\s\.\-&;\']+), (' + '|'.join(meses) + ') de ([0-9]{4})</p>')

        for line in f:
            for pattern in patterns:
                m = re.search(pattern, line)
                if not m is None:
                    titulo = m.group(1)
                    titulo = titulo.replace('&amp;','&')
                    return titulo
            
def get_author_from_metadata():
    elem = xmldoc_opf.getElementsByTagName('dc:creator') #obtiene metadatos
    for node in elem:
        if (node.getAttribute('opf:role') == 'aut'):
            author_fileas = node.getAttribute('opf:file-as')
            author_fileas_invertido = file_as_to_author(author_fileas)
            if author_fileas_invertido != node.firstChild.nodeValue:
                lista_errores.append('ERROR 041: ' + listaerrores[41] % (author_fileas, node.firstChild.nodeValue))
            return node.firstChild.nodeValue
        
def get_author_sort_from_metadata():
    elem = xmldoc_opf.getElementsByTagName('dc:creator') #obtiene metadatos
    for node in elem:
        if (node.getAttribute('opf:role') == 'aut'):
            return node.getAttribute('opf:file-as')

def get_author_from_title():
    global title_file
    if title_file == "":
        title_file = get_title_file_name()

    with open(tempdir + dir + title_file, "r", encoding="utf-8") as f:
        pattern = '<p class="tautor"><code class="sans">([\w\s\.\-&;\']+)</code></p>'
        for line in f:
            m = re.search(pattern, line)
            if not m is None:
                
                titulo = m.group(1)
                #sustituimos caracteres especiales
                titulo = titulo.replace('&amp;','&')
                return titulo
    
                
def comprobar_autor():
    '''Comprobamos que el autor coincide con el file-as y además coincide con el que aparece en la página de título e info
    '''
    author_title = get_author_from_title()
    author_metadata = get_author_from_metadata()
    author_info = get_author_from_info_page()
    #author_sort = file_as_to_author(get_author_sort_from_metadata())
    if author_metadata != author_title:
        lista_errores.append('ERROR 042: ' + listaerrores[42] % (author_title, author_metadata))
    if author_metadata != author_info: 
        lista_errores.append('ERROR 043: ' + listaerrores[43] % (author_info, author_metadata))

def get_title_from_title_page():
    global title_file
    if title_file == "":
        title_file = get_title_file_name()
        
    with open(tempdir + dir + title_file, "r", encoding="utf-8") as f:
        pattern = '<h1 class="ttitulo"( id="[^>]+")?( title="[^>]+")?><strong class="sans">([\'\w\s\.\-&;:,«»\?¿¡!\(\)]+)</strong></h1>'

        for line in f:
            m = re.search(pattern, line)
            if not m is None:
                titulo = m.group(3)
                titulo.replace('&amp;','&')
                return titulo
    lista_errores.append('ERROR 044: ' + listaerrores[44])

def get_title_from_metadata():
    elem = xmldoc_opf.getElementsByTagName('dc:title') #obtiene metadatos
    return elem[0].firstChild.nodeValue
    
def comprobar_titulo():
    titulo_metadata = get_title_from_metadata()
    titulo_titlepage = get_title_from_title_page()
    if titulo_metadata != titulo_titlepage:
        lista_errores.append('ERROR 045: ' + listaerrores[45] % (titulo_metadata, titulo_titlepage))

def comprobar_etiquetas_basura():
    patterns = list()
    patterns.append('<[ib]>')
    patterns.append('CDATA')
    patterns.append('class="((sgc)|(calibre))[^"]*"')
    for f in lChapters:
        for i, line in enumerate(open(tempdir + f, "r", encoding="utf-8")):
            for pattern in patterns:
                for match in re.finditer(pattern, line):
                    lista_errores.append('ERROR 046: ' + listaerrores[46] % (match.group(0), i+1, f))

def comprobar_css():
    files = locate("*.css",sdir)
    if sum(1 for _ in files) > 1:
        lista_errores.append('ERROR 052: ' + listaerrores[52])

def comprobar_metadatos_repetidos():
        metadatos_unicos = ['dc:title', 'dc:creator', 'dc:publisher', 'dc:description', 'dc:language', 'dc:subject']
        for metadato in metadatos_unicos:
            elem = xmldoc_opf.getElementsByTagName(metadato)
            if len(elem) > 1:
                lista_errores.append('ERROR 053: ' + listaerrores[53] % metadato)
    
if len(sys.argv) == 1:
    #interfaz gráfica para seleccionar archivo
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
        if sdir == '':
            sdir = os.curdir;
        tempdir = sdir + '/temp/' #directorio temporal para descomprimir el epub 
    else:
        print("Argumentos incorrectos. ABORTADO")
        sys.exit() 
else:
    print("Número de argumentos erróneo. ABORTADO")
    sys.exit() 

epubs_correctos = 0
epubs_erroneos = 0           
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
                    lChapters.append(os.path.join(dir, n.getAttribute('href')).replace('%20',' '))
                elif 'image' in node_type:
                    lImages.append(os.path.join(dir, n.getAttribute('href')).replace('%20',' '))
        elem = xmldoc.getElementsByTagName('spine') #get spine        

        #-----Aquí irán las comprobaciones, una a una
        comprobar_portada_semantics()    
        comprobar_generos_y_subgeneros()
        comprobar_file_size()
        comprobar_file_as()
        comprobar_nombre_archivo()
        comprobar_nombre_archivos_internos()
        comprobar_bookid() 
        comprobar_etiquetas_basura()
        comprobar_version_coincidente(epub)     
        comprobar_formato_nombre_archivo()  
        comprobar_metadatos_obligatorios()
        comprobar_metadatos_repetidos()
        comprobar_anyo_publicacion()
        comprobar_saga_en_metadatos()
        comprobar_traductor()
        comprobar_size_portada()
        comprobar_autor()
        comprobar_titulo()
        comprobar_fecha_modificacion()
        comprobar_editor_en_titulo_e_info()
        comprobar_css()

        #imprimir los errores
        print('EPLValidator v%s' %version)
        if lista_errores:
            epubs_erroneos +=1
            for e in lista_errores:
                print(e)
        else:
            epubs_correctos +=1
            print("todo está OK!")
        lista_errores = list()
        lChapters = list()
        lImages = list()
        title_file = ""
        info_file = ""
        print("")
        shutil.rmtree(tempdir)

print("Total epubs correctos: " + str(epubs_correctos))
print("Total epubs con errores: " + str(epubs_erroneos))
        
input("Presiona INTRO para finalizar el programa...")
