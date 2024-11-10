#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, os, shutil
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, DATETIME, KEYWORD, ID
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup

# lineas para evitar error SSL
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
    
def cargar():
    respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere recargar los datos. \nEsta operaciÃ³n puede ser lenta")
    if respuesta:
        almacenar_datos()
        
        
def extraer_recetas():
    import locale #para activar las fechas en formato espaÃ±ol
    locale.setlocale(locale.LC_TIME, "es_ES")
    
    lista=[]
    f = urllib.request.urlopen("https://www.recetasgratis.net/Recetas-de-Aperitivos-tapas-listado_receta-1_1.html")
    s = BeautifulSoup(f,"lxml")
    l= s.find_all("div", class_=['resultado','link'])
    for i in l:
        titulo = i.a.string.strip()
        comensales = i.find("span",class_="comensales")
        if comensales:
            comensales = int(comensales.string.strip())
        else:
            comensales=-1
        
        f1 = urllib.request.urlopen(i.find('a')['href'])
        s1 = BeautifulSoup(f1,"lxml")
        autor = s1.find("div", class_='nombre_autor').a.string.strip()
        fecha = s1.find("div", class_='nombre_autor').find('span', class_="date_publish").string
        fecha = fecha.replace('Actualizado:','').strip()
        fecha = datetime.strptime(fecha, "%d %B %Y")
        introduccion = s1.find("div", class_="intro").text
        caracteristicas = s1.find("div", class_="properties inline")
        if caracteristicas:
            caracteristicas = caracteristicas.text.replace("CaracterÃ­sticas adicionales:","")
            caracteristicas = ",".join([c.strip() for c in caracteristicas.split(",")] )     
        else:
            caracteristicas = "sin definir"
        lista.append((titulo, comensales, autor, fecha, caracteristicas,introduccion))
    
    return lista

def almacenar_datos():
    #define el esquema de la informaciÃ³n
    schem = Schema(titulo=TEXT(stored=True,phrase=False), comensales=NUMERIC(stored=True), autor=TEXT(stored=True), fecha=DATETIME(stored=True), caracteristicas=KEYWORD(stored=True,commas=True,lowercase=True), introduccion=TEXT(stored=True,phrase=False))
    
    #eliminamos el directorio del Ã­ndice, si existe
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
    
    #creamos el Ã­ndice
    ix = create_in("Index", schema=schem)

if __name__ == "__main__":
    for receta in extraer_recetas():
        print(receta[5])