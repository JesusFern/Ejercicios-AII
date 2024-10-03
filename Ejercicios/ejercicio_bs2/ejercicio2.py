'''
Created on 26 sept 2024

@author: Usuario
'''
import urllib.request
from bs4 import BeautifulSoup
import sqlite3
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from datetime import datetime
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def extraer_informacion():
    url = "https://www.elseptimoarte.net/estrenos/2024/"
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f, "lxml")
    lista = s.find("ul", class_="elements")
    elementos = lista.find_all("li")
    
    datos = list(elementos)
    
    return datos
    
def almacenar_bd():
    datos = extraer_informacion()
    conn = sqlite3.connect('peliculas.db')
    print("Opened database successfully")
    conn.execute("DROP TABLE IF EXISTS PELICULA")
    conn.execute('''CREATE TABLE PELICULA
        (TITULO           TEXT,
         TITULO_ORIGINAL    TEXT,
         PAIS       TEXT,
         FECHA_ESTRENO         DATE,
         DIRECTOR        TEXT,
         GENEROS        TEXT);''')
    print("Table created successfully")
        
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
        
        conn.execute("INSERT INTO PELICULA (TITULO ,TITULO_ORIGINAL,PAIS,FECHA_ESTRENO,DIRECTOR,GENEROS) \
             VALUES (?,?,?,?,?,?)", (titulo, titulo_original, paises, fecha_estreno, director, generos))
        print("Film registered successfully")
        conn.commit()
        
    cursor = conn.execute("SELECT Count(*) from PELICULA")
    total_peliculas = cursor.fetchone()[0]
    
    
    messagebox.showinfo("Succesfully created.", "Base de datos creada correctamente. Se han registrado "+ str(total_peliculas)+" peliculas.") 
    conn.close()
    
 
 
def cargar():
    sure = messagebox.askyesno("Are you sure?", "¿Seguro que quieres cargar los datos?")
    if sure:
        almacenar_bd();
        
def listar():
    conn = sqlite3.connect('peliculas.db')
    cursor = conn.execute("SELECT TITULO,PAIS,DIRECTOR from PELICULA")
    
    
    v = Toplevel()
    scrollbar = Scrollbar(v)
    scrollbar.pack( side = RIGHT, fill=Y )
    Lb1 = Listbox(v, width=150, yscrollcommand = scrollbar.set)
    for row in cursor:
        Lb1.insert(END, "Titulo: "+ row[0] + " //// Pais: " + row[1] + " //// Director: "  + row[2])
        Lb1.insert(END, "------------------------------------------------------")
    Lb1.pack(side = LEFT, fill = BOTH )
    scrollbar.config( command = Lb1.yview )
    conn.close()
    
def buscar_por_titulo():
    def listar_por_titulo(event):
        conn = sqlite3.connect('peliculas.db')
        palabra_contenida = '%' + str(entry.get()).lower() + '%'
        cursor = conn.execute("SELECT TITULO,PAIS,DIRECTOR from PELICULA WHERE LOWER(TITULO) LIKE ?", (palabra_contenida,))
        
        v = Toplevel()
        scrollbar = Scrollbar(v)
        scrollbar.pack( side = RIGHT, fill=Y )
        Lb1 = Listbox(v, width=150, yscrollcommand = scrollbar.set)
        for row in cursor:
            Lb1.insert(END, "Titulo: "+ row[0] + " //// Pais: " + row[1] + " //// Director: "  + row[2])
            Lb1.insert(END, "------------------------------------------------------")
        Lb1.pack(side = LEFT, fill = BOTH )
        scrollbar.config( command = Lb1.yview )
        conn.close()
        
    v = Toplevel()
    L1 = Label(v, text="Titulo")
    L1.pack( side = LEFT)
    entry = Entry(v, bd =5)
    entry.bind("<Return>", listar_por_titulo)
    entry.pack(side=LEFT)

def buscar_por_fecha():   
    def listar_por_fecha(event):
        conn = sqlite3.connect('peliculas.db')
        try:
            fecha =  datetime.strptime(entry.get(), "%d-%m-%Y")
            cursor = conn.execute("SELECT TITULO,FECHA_ESTRENO from PELICULA WHERE FECHA_ESTRENO > ?", (fecha,))
            v = Toplevel()
            scrollbar = Scrollbar(v)
            scrollbar.pack( side = RIGHT, fill=Y )
            Lb1 = Listbox(v, width=150, yscrollcommand = scrollbar.set)
            for row in cursor:
                Lb1.insert(END, "Titulo: "+ row[0] + " //// Fecha: " + row[1])
                Lb1.insert(END, "------------------------------------------------------")
            Lb1.pack(side = LEFT, fill = BOTH )
            scrollbar.config( command = Lb1.yview )
            conn.close()
        except:
            conn.close()
            messagebox.showerror(title="Error",message="Error en la fecha\nFormato dd-mm-aaaa")
    v = Toplevel()
    L1 = Label(v, text="Fecha estreno (dd-mm-aaaa)")
    L1.pack( side = LEFT)
    entry = Entry(v, bd =5)
    entry.bind("<Return>", listar_por_fecha)
    entry.pack(side=LEFT)
    

def buscar_por_genero():
    def listar_por_genero(event):
        conn = sqlite3.connect('peliculas.db')
        ge = '%' + w.get() + '%'
        cursor_1 = conn.execute("SELECT TITULO,GENEROS from PELICULA WHERE GENEROS LIKE ?",  (ge,))
        v = Toplevel()
        scrollbar = Scrollbar(v)
        scrollbar.pack( side = RIGHT, fill=Y )
        Lb1 = Listbox(v, width=150, yscrollcommand = scrollbar.set)
        for row in cursor_1:
            Lb1.insert(END, "Titulo: "+ row[0] + " //// Generos: " + row[1])
            Lb1.insert(END, "------------------------------------------------------")
        Lb1.pack(side = LEFT, fill = BOTH )
        scrollbar.config( command = Lb1.yview )
        conn.close()
    
    conn = sqlite3.connect('peliculas.db')
    cursor = conn.execute("SELECT GENEROS from PELICULA")
    generos = set()
    for row in cursor:
        listado = row[0].split(",")
        for genero in listado:
            generos.add(genero.strip())
    
    conn.close()
    

    v = Toplevel()
    L1 = Label(v, text="Género")
    L1.pack( side = LEFT)
    w = Spinbox(v, value = list(generos))
    w.bind("<Return>", listar_por_genero)
    w.pack()

  
def ventana_principal():
        
    root = Tk()
    menubar = Menu(root)
    
    #Datos
    menudatos = Menu(menubar, tearoff=0)
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_command(label="Listar", command=listar)
    menudatos.add_command(label="Salir", command=root.quit)
    
    menubar.add_cascade(label="Datos", menu=menudatos)
    
    #Buscar
    menubuscar = Menu(menubar, tearoff=0)   
    menubuscar.add_command(label="Titulo", command=buscar_por_titulo)
    menubuscar.add_command(label="Fecha", command=buscar_por_fecha)
    menubuscar.add_command(label="Genero", command=buscar_por_genero)
    
    menubar.add_cascade(label="Buscar", menu=menubuscar)
    

    root.config(menu=menubar)
    root.mainloop()
    
    
    
ventana_principal()
    
    
