#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
actualizarCalibre
Created on May 13, 2013

@author: betatron
'''

import sys
import zipfile
import fnmatch
import shutil
import os.path
import re
import sqlite3
from os import listdir
from os.path import isfile, join

from xml.dom import minidom

#Otras:
sdir = sys.argv[1] #directorio con los epubs a procesar
newbooks = sys.argv[1] + '/new/'
db = sys.argv[2] + '/' + 'metadata.db' #directorio de Calibre
con = sqlite3.connect(db)

tempdir = sdir + '/temp/' #directorio temporal para descomprimir el epub


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
    """Borra el directorio y todo su contenido
    
    Args:
        dir: ruta del directorio a borrar
    """
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

def query_db(con, cursor, val, db, what):
    cursor.execute("select %s from %s where %s" % (val, db, what))
    rows = cursor.fetchone()
    return rows
    
def get_version_from_title_page():
    elem = xmldoc_opf.getElementsByTagName('itemref') #get spine
    title_id = elem[2].getAttribute('idref')
    elem = xmldoc_opf.getElementsByTagName('manifest')
    for n in elem[0].childNodes:
        if n.nodeName == 'item':
            if n.getAttribute('id') == title_id:
                title_file = n.getAttribute('href')    
    f = open(tempdir + dir + title_file, "r", encoding="utf-8")
    pattern = '<p class="trevision"><strong class="sans">eP(UB|ub) r([0-9].[0-9])</strong></p>'
    for line in f:
        m = re.search(pattern, line)
        if not m is None:
            return m.group(2)    

listalibros = fnmatch.filter([ f for f in listdir(sdir) if isfile(join(sdir,f)) ], '*.epub')

libros_actualizados = 0

for epub in listalibros:    
    
    sourcefile = sdir + '/' + epub
    destinationfilename = sourcefile
    if sourcefile:  
        print('Comprobando: '  + os.path.basename(sourcefile))  
        zipf = zipfile.ZipFile(sourcefile,"r") 
        clean_dir(tempdir) #borramos contenido del directorio temporal
        zipf.extractall(tempdir) #descomprimimos el archivo
        zipf.close()
        f = open(tempdir + 'META-INF/container.xml') #buscamos la ruta del content.opf en el container.xml
        xmldoc = minidom.parse(f)
        f.close()
        elem = xmldoc.getElementsByTagName('rootfile')
        attr = elem[0].getAttribute('full-path')
        dir = os.path.dirname(attr) + '/'
        f = open(tempdir + attr, "r", encoding="utf-8") #abrimos el content.opf
        xmldoc_opf = minidom.parse(f) #Lo parseamos y lo dejamos en memoria, ya que la mayoria de comprobaciones lo necesitan
        f.close()
        
        #obtenemos titulo y autor
        elem = xmldoc_opf.getElementsByTagName('dc:title') #obtiene metadatos
        titulo = elem[0].firstChild.nodeValue
        elem = xmldoc_opf.getElementsByTagName('dc:creator') #obtiene metadatos
        author_sort =elem[0].getAttribute("opf:file-as")
        if (titulo and author_sort):
                            
            version = get_version_from_title_page()
            if version != None:
                cursor = con.cursor()
                cursor.execute("select id, title, author_sort, path from books where LOWER(title) LIKE '" + titulo.lower() + "' AND author_sort = '" + author_sort + "'")
                row = cursor.fetchone()
                if (row != None):                
                    if cursor.fetchone() == None: #solo ha encontrado un libro
                        
                        id = row[0]
                        destino = sys.argv[2] + '/' + row[3]
                        #obtener version de este libro
                        cursor.execute("select book, value from custom_column_1 where book = " + str(id))
                        row = cursor.fetchone()
                        if row!= None:
                            version_anterior = row[1]
                            #if version_anterior != version:
                            #copiar el archivo                            
                            for e in locate("*.epub",destino):
                                epub_destino = e
                                
                            shutil.copyfile(sourcefile, epub_destino)
                            #actualizar version
                            cursor.execute("update custom_column_1 set value = " + version + " where book = " + str(id))
                            con.commit()
                            print("--versión anterior %s, actualizado a %s" % (version_anterior, version))
                            #delete book from the list
                            os.remove(sourcefile)
                            libros_actualizados += 1
                        else:
                            #el libro no tiene n. de version. Lo dejamos apartado para revisión manual
                            print('libro sin número de versión')
                else:
                    #el libro es nuevo. lo movemos a nuevo directorio
                    shutil.move(sourcefile, newbooks)

print('Total libros actualizados: ' + str(libros_actualizados))   
