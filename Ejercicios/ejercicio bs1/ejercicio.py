'''
Created on 23 sept 2024

@author: jesfe
'''
import urllib.request
from bs4 import BeautifulSoup
import sqlite3
import tkinter as tk
from tkinter import *

def extraer_elementos():
    lista=[]
    for num_paginas in range(0,3):
        url = 'https://www.vinissimus.com/es/vinos/tinto/?cursor='+str(36*num_paginas)
        f = urllib.request.urlopen(url)
        s = BeautifulSoup(f, "lxml")
        lista_una_pagina = s.find_all("div", class_="product-list-item")
        lista.extend(lista_una_pagina)
    
    return lista

def almacenar_bd():
    conn = sqlite3.connect('vinos.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS VINO")
    conn.execute("DROP TABLE IF EXISTS TIPOS_UVAS")
    conn.execute('''CREATE TABLE VINO
         (NAME           TEXT    NOT NULL,
         PRECIO          REAL,
         DENOMINACION    TEXT,
         BODEGA          TEXT,
         TIPO_UVAS        TEXT);''')
    conn.execute('''CREATE TABLE TIPOS_UVAS
       (NOMBRE            TEXT NOT NULL);''')
    
    lista_vinos = extraer_elementos()
    
    conn.commit()
    conn.close()
    
    
def func_pruebas():
    lista_vinos = extraer_elementos()
    for vino in lista_vinos:
        datos = vino.find("div",class_=["details"])
        nombre = datos.a.h2.string.strip()
        bodega = datos.find("div",class_=["cellar-name"]).string.strip()
        denominacion = datos.find("div",class_=["region"]).string.strip()
        tipo_uva = datos.find("div",class_=["tags"]).find_all("span")
        for uva in tipo_uva:
            print("Tipo de uva del vino "+ nombre + " " + uva.string)


func_pruebas()
        


    
    
