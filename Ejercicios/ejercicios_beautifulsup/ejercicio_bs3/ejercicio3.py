'''
Created on 1 oct 2024

@author: jesfe
'''
import urllib.request
from bs4 import BeautifulSoup
import sqlite3
import tkinter as tk
from tkinter import *
from tkinter import messagebox

# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
    

def extraer_elementos():
    lista=[]
    for num_paginas in range(1,3):
        url = "https://zacatrus.es/juegos-de-mesa.html?p=" + str(num_paginas)
        f = urllib.request.urlopen(url)
        s = BeautifulSoup(f, "lxml")
        lista_una_pagina = s.find_all("li", class_="item product product-item")
        lista.extend(lista_una_pagina)
    return lista
        
def almacenar_bd():
    conn = sqlite3.connect('juegos.db')
    conn.execute("DROP TABLE IF EXISTS JUEGO")
    conn.text_factory = str
    conn.execute('''CREATE TABLE JUEGO
         (TITULO           TEXT    NOT NULL,
         PORCENTAJE_VOTOS            INT,
         PRECIO        REAL,
         TEMATICA         TEXT,
         COMPLEJIDAD        TEXT);''')
    lista_juegos =  extraer_elementos()
    for juego in lista_juegos:
        detalles_juego= juego.find("div", class_= "product details product-item-details")
        titulo = detalles_juego.strong.a.string.strip()
        porcentaje_votos = detalles_juego.find("div", class_="rating-result")
        if porcentaje_votos:
            porcentaje_votos = int(detalles_juego.find("div", class_="rating-result").span.string.replace("%",""))
        else:
            porcentaje_votos=0
        precio = float(detalles_juego.find("div", class_="price-box price-final_price").find("span", class_="price").string.replace(",",".").replace("€","").strip())
        link_detalles = detalles_juego.strong.a['href']
        tematica = extraer_detalles(link_detalles)[0]
        complejidad = extraer_detalles(link_detalles)[1]
        conn.execute("INSERT INTO JUEGO (TITULO ,PORCENTAJE_VOTOS,PRECIO,TEMATICA,COMPLEJIDAD) \
             VALUES (?,?,?,?,?)", (titulo, porcentaje_votos, precio, tematica, complejidad))
        print("Game registered successfully")
        conn.commit()
        
    cursor = conn.execute("SELECT Count(*) from JUEGO")
    total_juegos = cursor.fetchone()[0]
    
    
    messagebox.showinfo("Succesfully created.", "Base de datos creada correctamente. Se han registrado "+ str(total_juegos)+" juegos de mesa.") 
    conn.close()
    
def extraer_detalles(url):
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f, "lxml")
    valor_tematica = s.find("div", attrs={"data-th": "Temática"})
    valor_complejidad = s.find("div", attrs={"data-th": "Complejidad"})
    if valor_tematica:
        tematica= valor_tematica.string.strip()
    else:    
        tematica="-"
    if valor_complejidad:
        complejidad= valor_complejidad.string.strip()
    else:
        complejidad="-"
    return (tematica,complejidad)

def cargar():
    sure = messagebox.askyesno("Are you sure?", "¿Seguro que quieres cargar los datos?")
    if sure:
        almacenar_bd();
        
def listar_juegos():
    conn = sqlite3.connect('juegos.db')
    cursor = conn.execute("SELECT TITULO ,PORCENTAJE_VOTOS,PRECIO,TEMATICA,COMPLEJIDAD from JUEGO")
    v = Toplevel()
    scrollbar = Scrollbar(v)
    scrollbar.pack( side = RIGHT, fill=Y )
    Lb1 = Listbox(v, width=150, yscrollcommand = scrollbar.set)
    for row in cursor:
        Lb1.insert(END, "Titulo: "+ row[0] + " //// Porcentaje de votos positivos: " + str(row[1]) + " //// Precio: "  + str(row[2])+ " //// Temática: " + row[3] + " //// Complejidad: " + row[4])
        Lb1.insert(END, "------------------------------------------------------")
    Lb1.pack(side = LEFT, fill = BOTH )
    scrollbar.config( command = Lb1.yview )
    conn.close()
def listar_mejores_juegos():
    conn = sqlite3.connect('juegos.db')
    cursor = conn.execute("SELECT TITULO ,PORCENTAJE_VOTOS,PRECIO,TEMATICA,COMPLEJIDAD from JUEGO WHERE PORCENTAJE_VOTOS>90 ORDER BY PORCENTAJE_VOTOS DESC")
    v = Toplevel()
    scrollbar = Scrollbar(v)
    scrollbar.pack( side = RIGHT, fill=Y )
    Lb1 = Listbox(v, width=150, yscrollcommand = scrollbar.set)
    for row in cursor:
        Lb1.insert(END, "Titulo: "+ row[0] + " //// Porcentaje de votos positivos: " + str(row[1]) + " //// Precio: "  + str(row[2])+ " //// Temática: " + row[3] + " //// Complejidad: " + row[4])
        Lb1.insert(END, "------------------------------------------------------")
    Lb1.pack(side = LEFT, fill = BOTH )
    scrollbar.config( command = Lb1.yview )
    conn.close()

def buscar_por_tematica():
    def listar_por_tematica(event):
        conn = sqlite3.connect('juegos.db')
        te = '%' + w.get() + '%'
        cursor_1 = conn.execute("SELECT TITULO,TEMATICA,COMPLEJIDAD from JUEGO WHERE TEMATICA LIKE ?",  (te,))
        v = Toplevel()
        scrollbar = Scrollbar(v)
        scrollbar.pack( side = RIGHT, fill=Y )
        Lb1 = Listbox(v, width=150, yscrollcommand = scrollbar.set)
        for row in cursor_1:
            Lb1.insert(END, "Titulo: "+ row[0] + " //// Tematica: " + row[1] + " //// Complejidad: " + row[2])
            Lb1.insert(END, "------------------------------------------------------")
        Lb1.pack(side = LEFT, fill = BOTH )
        scrollbar.config( command = Lb1.yview )
        conn.close()
    
    conn = sqlite3.connect('juegos.db')
    cursor_t = conn.execute("SELECT TEMATICA from JUEGO")
    tematicas = set()
    for row in cursor_t:
        splitted = row[0].split(",")
        for t in splitted:
            tematicas.add(t.strip())
    conn.close()
    
    v = Toplevel()
    L1 = Label(v, text="Temática")
    L1.pack( side = LEFT)
    w = Spinbox(v, value = list(tematicas))
    w.bind("<Return>", listar_por_tematica)
    w.pack()
    
def buscar_por_complejidad():
    def listar_por_complejidad(event):
        conn = sqlite3.connect('juegos.db')
        co = '%' + w.get() + '%'
        cursor_1 = conn.execute("SELECT TITULO,TEMATICA,COMPLEJIDAD from JUEGO WHERE COMPLEJIDAD LIKE ?",  (co,))
        v = Toplevel()
        scrollbar = Scrollbar(v)
        scrollbar.pack( side = RIGHT, fill=Y )
        Lb1 = Listbox(v, width=150, yscrollcommand = scrollbar.set)
        for row in cursor_1:
            Lb1.insert(END, "Titulo: "+ row[0] + " //// Tematica: " + row[1] + " //// Complejidad: " + row[2])
            Lb1.insert(END, "------------------------------------------------------")
        Lb1.pack(side = LEFT, fill = BOTH )
        scrollbar.config( command = Lb1.yview )
        conn.close()
    
    conn = sqlite3.connect('juegos.db')
    cursor_t = conn.execute("SELECT COMPLEJIDAD from JUEGO")
    complejidad = set()
    for row in cursor_t:
        complejidad.add(row[0].strip())
        
    conn.close()
    
    v = Toplevel()
    L1 = Label(v, text="Complejidad")
    L1.pack( side = LEFT)
    w = Spinbox(v, value = list(complejidad))
    w.bind("<Return>", listar_por_complejidad)
    w.pack()
def ventana_principal():
        
    root = Tk()
    menubar = Menu(root)
    
    #Datos
    menudatos = Menu(menubar, tearoff=0)
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_command(label="Salir", command=root.quit)
    
    menubar.add_cascade(label="Datos", menu=menudatos)
    
    #Listar
    menulistar = Menu(menubar, tearoff=0)
    menulistar.add_command(label="Juegos", command=listar_juegos)
    menulistar.add_command(label="Mejores Juegos", command=listar_mejores_juegos)
    
    menubar.add_cascade(label="Listar", menu=menulistar)
    
    #Buscar
    menubuscar = Menu(menubar, tearoff=0)   
    
    menubar.add_cascade(label="Buscar", menu=menubuscar)
    menubuscar.add_command(label="Temática", command=buscar_por_tematica)
    menubuscar.add_command(label="Complejidad", command=buscar_por_complejidad)
    

    root.config(menu=menubar)
    root.mainloop()
    
    
    
ventana_principal()
    
