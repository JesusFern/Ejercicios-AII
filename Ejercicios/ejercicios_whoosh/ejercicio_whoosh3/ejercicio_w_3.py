#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, shutil
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, NUMERIC, KEYWORD, ID
from whoosh.qparser import QueryParser
from datetime import datetime

PAGINAS = 3  #numero de paginas

# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
    
def extraer_datos():
    lista=[]
    
    for p in range(1,PAGINAS+1):
        url="https://www.elseptimoarte.net/estrenos/2024/" + str(p) + "/"
        f = urllib.request.urlopen(url)
        s = BeautifulSoup(f,"lxml")
        l = s.find("ul", class_="elements").find_all("li")
        lista.extend(l)
    return lista
def extraer_peliculas():
    lista = []
    datos = extraer_datos()
    for dato in datos:
        url =  "https://www.elseptimoarte.net/" + dato.a['href']
        f = urllib.request.urlopen(url)
        s = BeautifulSoup(f, "lxml")
        seccion = list(s.find("main",id="content").find_all("section", class_="highlight"))[0]
        titulo = seccion.find('dt' ,string="Título").find_next_sibling('dd').string.strip()
        titulo_original = seccion.find('dt' ,string="Título original").find_next_sibling('dd').string.strip()
        paises = seccion.find('dt' ,string="País").find_next_sibling('dd').a.string.strip()
        fecha_estreno =  datetime.strptime(seccion.find('dt' ,string="Estreno en España").find_next_sibling('dd').string.strip(), '%d/%m/%Y')
        director = seccion.find('dt' ,string="Director").find_next_sibling('dd').a.string.strip()
        generos = "".join(s.find('div', id='datos_pelicula').find('p', class_='categorias').stripped_strings)
        apartado = s.find("div", class_="wrapper contenido").find("div", itemprop="description")
        sinopsis = ""
        if apartado.string:
            sinopsis =  sinopsis + apartado.string.strip()
        else:
            for p in apartado.find_all("p"):
                if p.string:
                    sinopsis = sinopsis + p.string + " "
                else:
                    sinopsis = sinopsis + p.get_text() + " "
        
        print("Titulo: " + titulo + "Titulo original: " + titulo_original + "paises : " + paises + "fecha estreno : " + str(fecha_estreno) +"director : " + director +"generos : " + generos)
        print("Sinopsis: " + sinopsis)
        lista.append((titulo,titulo_original,paises,fecha_estreno,director,generos))
    return lista
    
if __name__ == "__main__":
    peli = extraer_peliculas()
    # for peli in pelis:
    #     print("Titulo: " + str(peli[0]) + "Titulo original: " + str(peli[1]) + "paises : " + str(peli[2]) + "fecha estreno : " + str(peli[3]) +"director : " + str(peli[4]) +"generos : " + str(peli[5]))
    

