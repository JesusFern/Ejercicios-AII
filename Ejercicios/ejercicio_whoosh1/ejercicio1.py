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
    for num_paginas in range(1,5):
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
         PRECIO        REAL,
         TEMATICA         TEXT,
         COMPLEJIDAD        TEXT,
         NUM_JUGADORES        TEXT,
         DETALLES            TEXT);''')
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
        num_jugadores = extraer_detalles(link_detalles)[2]
        detalles = extraer_detalles(link_detalles)[3]
        conn.execute("INSERT INTO JUEGO (TITULO ,PRECIO,TEMATICA,COMPLEJIDAD,NUM_JUGADORES,DETALLES) \
             VALUES (?,?,?,?,?,?)", (titulo, precio, tematica, complejidad,num_jugadores,detalles))
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
    valor_num_jugadores = s.find("div", attrs={"data-th": "Núm. jugadores"})
    if valor_tematica:
        tematica= valor_tematica.string.strip()
    else:    
        tematica="-"
    if valor_complejidad:
        complejidad= valor_complejidad.string.strip()
    else:
        complejidad="-"
    if valor_num_jugadores:
        num_jugadores = valor_num_jugadores.string.strip()
    else:
        num_jugadores = "-"
        
   
    div_description = s.find('div', class_='product attribute description')
    if div_description:
        detalles = div_description.get_text(separator='\n', strip=True)
    else:
        detalles = "No hay detalles para este juego"
    
    return (tematica,complejidad,num_jugadores,detalles)

def cargar():
    sure = messagebox.askyesno("Are you sure?", "¿Seguro que quieres cargar los datos?")
    if sure:
        almacenar_bd();

def listar_juegos():
    conn = sqlite3.connect('juegos.db')
    cursor = conn.execute("SELECT TITULO ,PRECIO,TEMATICA,COMPLEJIDAD,NUM_JUGADORES,DETALLES from JUEGO")
    v = Toplevel()
    scrollbar = Scrollbar(v)
    scrollbar.pack( side = RIGHT, fill=Y )
    Lb1 = Listbox(v, width=150, yscrollcommand = scrollbar.set)
    for row in cursor:
        Lb1.insert(END, "Juego de mesa: "+ row[0])
        Lb1.insert(END, "    Temática: " + str(row[2]))
        Lb1.insert(END, "    Complejidad: " + str(row[3]))
        Lb1.insert(END, "    Numero de jugadores: " + str(row[4]))
        Lb1.insert(END, "    Detalles: " + str(row[5]))
        
        Lb1.insert(END, "------------------------------------------------------")
    Lb1.pack(side = LEFT, fill = BOTH )
    scrollbar.config( command = Lb1.yview )
    conn.close()        

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
    menubar.add_cascade(label="Listar", menu=menulistar)
    
    #Buscar
    menubuscar = Menu(menubar, tearoff=0)   
    
    menubar.add_cascade(label="Buscar", menu=menubuscar)
    

    root.config(menu=menubar)
    root.mainloop()
    
    
if __name__ == "__main__":    
    ventana_principal()  
