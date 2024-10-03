'''
Created on 23 sept 2024

@author: jesfe
'''
import urllib.request
from bs4 import BeautifulSoup
import sqlite3
import tkinter as tk
from tkinter import *
from tkinter import messagebox

def extraer_elementos():
    lista=[]
    for num_paginas in range(0,3):
        url = 'https://www.vinissimus.com/es/vinos/tinto/?cursor='+str(36*num_paginas)
        f = urllib.request.urlopen(url)
        s = BeautifulSoup(f, "lxml")
        lista_una_pagina = s.find_all("div", class_="product-list-item")
        lista.extend(lista_una_pagina)
    
    return lista

def cargar():
    respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere recargar los datos. \nEsta operaciÃ³n puede ser lenta")
    if respuesta:
        almacenar_bd()
        
        
def listar_todos():
    conn = sqlite3.connect('vinos.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT NOMBRE, PRECIO, BODEGA, DENOMINACION FROM VINO")
    conn.close
    listar_vinos(cursor)
    
def denominacion():
    w = Spinbox(master, from_=0, to=10)
    w.pack()


def almacenar_bd():
    conn = sqlite3.connect('vinos.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS VINO")
    conn.execute("DROP TABLE IF EXISTS TIPOS_UVAS")
    conn.execute('''CREATE TABLE VINO
         (NOMBRE           TEXT    NOT NULL,
         PRECIO          REAL,
         DENOMINACION    TEXT,
         BODEGA          TEXT,
         TIPO_UVAS        TEXT);''')
    conn.execute('''CREATE TABLE TIPOS_UVAS
       (NOMBRE            TEXT NOT NULL);''')
    
    lista_vinos = extraer_elementos()
    tipo_uvas=set()
    for vino in lista_vinos:
        datos = vino.find("div",class_=["details"])
        nombre = datos.a.h2.string.strip()
        bodega = datos.find("div",class_=["cellar-name"]).string.strip()
        denominacion = datos.find("div",class_=["region"]).string.strip()
        etiquetas_uvas = datos.find("div",class_=["tags"])
        lista_uvas = list()
        if etiquetas_uvas:
            lista_uvas = etiquetas_uvas.find_all("span")
        tags = datos.find("div",class_=["tags"])
        uvas = "Sin info sobre tipo de uva"
        if tags:
            uvas = "".join(tags.stripped_strings)
        
        for uva in lista_uvas:
            tipo_uvas.add(uva.string.replace("/","").strip())
        
        precio = list(vino.find("p",class_=["price"]).stripped_strings)[0]
        #si tiene descuento el prcio es el del descuento
        dto = vino.find("p",class_=["price"]).find_next_sibling("p",class_="dto")
        if dto:
            precio = list(dto.stripped_strings)[0]
        conn.execute("""INSERT INTO VINO (NOMBRE, PRECIO, DENOMINACION, BODEGA, TIPO_UVAS) VALUES (?,?,?,?,?)""",
                     (nombre, float(precio.replace(',','.')), denominacion, bodega, uvas))
    conn.commit()
    
    #insertamos el la tabla TIPOS_UVAS los elemento sdel conjunto tipos_uva
    for u in list(tipo_uvas):
        conn.execute("""INSERT INTO TIPOS_UVAS (NOMBRE) VALUES (?)""",
                     (u,))
    conn.commit()
    
    cursor = conn.execute("SELECT COUNT(*) FROM VINO")
    cursor1 = conn.execute("SELECT COUNT(*) FROM TIPOS_UVAS")
    messagebox.showinfo("Base Datos",
                        "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " vinos y "
                        + str(cursor1.fetchone()[0]) + " tipos de uvas")
    conn.close()
 
def listar_vinos(cursor):      
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        s = 'VINO: ' + row[0]
        lb.insert(END, s)
        lb.insert(END, "------------------------------------------------------------------------")
        s = "     PRECIO: " + str(row[1]) + ' | BODEGA: ' + row[2]+ ' | DENOMINACION: ' + row[3]
        lb.insert(END, s)
        lb.insert(END,"\n\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)
    
def ventana_principal():
    raiz = Tk()
    
    menu = Menu(raiz)
    
    
     #DATOS
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_command(label="Listar", command=listar_todos)
    menudatos.add_command(label="Salir", command=raiz.quit)
                          
    menu.add_cascade(label="Datos", menu=menudatos)
    
    #Buscar
    menubuscar = Menu(menu, tearoff=0)
    menudatos.add_command(label="Denominacion", command=denominacion)
    
    menu.add_cascade(label="Buscar", menu=menubuscar)
    
    raiz.config(menu=menu)
    
    raiz.mainloop()


if __name__ == "__main__":
    ventana_principal()
        


    
    
