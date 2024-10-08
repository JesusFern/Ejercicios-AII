'''
Created on 8 oct 2024

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
    url = "https://resultados.as.com/resultados/futbol/primera/2023_2024/calendario/"
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f, "lxml")
    lista = s.find_all("div", class_="cont-modulo resultados")
    return lista


def almacenar_bd():
    conn = sqlite3.connect('jornadas.db')
    conn.execute("DROP TABLE IF EXISTS JORNADA")
    conn.text_factory = str
    conn.execute('''CREATE TABLE JORNADA
         (NUMERO_JORNADA           TEXT    NOT NULL,
         EQUIPO_LOCAL            TEXT,
         EQUIPO_VISITANTE        TEXT,
         RESULTADO         TEXT,
         ENLACE            TEXT);''')
    lista_jornadas =  extraer_elementos()
    for jornada in lista_jornadas:
        numero_jornada =  jornada.find("h2",class_="tit-modulo").a.string.strip()
        resultados = jornada.tbody.find_all("tr")
        for resultado in resultados:
            equipo_local = resultado.find_all("span", class_="nombre-equipo")[0].string.strip()
            equipo_visitante = resultado.find_all("span", class_="nombre-equipo")[1].string.strip()
            marcador = resultado.find("td", class_="col-resultado finalizado").a.string.strip()
            enlace_detalles = resultado.find("td", class_="col-resultado finalizado").a['href']
            print(enlace_detalles)
            conn.execute("INSERT INTO JORNADA (NUMERO_JORNADA ,EQUIPO_LOCAL,EQUIPO_VISITANTE,RESULTADO, ENLACE) \
             VALUES (?,?,?,?,?)", (numero_jornada, equipo_local, equipo_visitante, marcador, enlace_detalles))
            conn.commit()
            
    cursor = conn.execute("SELECT Count(*) from JORNADA")
    total_jornadas = cursor.fetchone()[0]
    messagebox.showinfo("Succesfully created.", "Base de datos creada correctamente. Se han registrado "+ str(total_jornadas)+" entradas.") 
    conn.close()
    
def cargar():
    sure = messagebox.askyesno("Are you sure?", "¿Seguro que quieres cargar los datos?")
    if sure:
        almacenar_bd();
def listar_jornadas():
    conn = sqlite3.connect('jornadas.db')
    cursor = conn.execute("SELECT NUMERO_JORNADA ,EQUIPO_LOCAL,EQUIPO_VISITANTE,RESULTADO from JORNADA")
    v = Toplevel()
    scrollbar = Scrollbar(v)
    scrollbar.pack( side = RIGHT, fill=Y )
    Lb1 = Listbox(v, width=150, yscrollcommand = scrollbar.set)
    lista_num_jornadas = set()
    for row in cursor:
        if row[0] not in lista_num_jornadas:
            if len(lista_num_jornadas)!=0:
                Lb1.insert(END, "")
            Lb1.insert(END, str(row[0]))
            Lb1.insert(END, "------------------------------------------------------")
            Lb1.insert(END, "") 
        Lb1.insert(END, str(row[1]) + " " + str(row[3]) + " "+ str(row[2]))
        lista_num_jornadas.add(row[0])
    Lb1.pack(side = LEFT, fill = BOTH )
    scrollbar.config( command = Lb1.yview )
    conn.close()
    
def buscar_por_jornada():
    def listar_por_numero_jornada(event):
        conn = sqlite3.connect('jornadas.db')
        num = '% ' + w.get() + ''
        cursor_1 = conn.execute("SELECT NUMERO_JORNADA ,EQUIPO_LOCAL,EQUIPO_VISITANTE,RESULTADO from JORNADA WHERE NUMERO_JORNADA LIKE ?",  (num,))
        v = Toplevel()
        scrollbar = Scrollbar(v)
        scrollbar.pack( side = RIGHT, fill=Y )
        Lb1 = Listbox(v, width=150, yscrollcommand = scrollbar.set)
        Lb1.insert(END, str(cursor_1.fetchone()[0]))
        Lb1.insert(END, "------------------------------------------------------")
        for row in cursor_1:
            Lb1.insert(END, str(row[1]) + " " + str(row[3]) + " "+ str(row[2]))
        Lb1.pack(side = LEFT, fill = BOTH )
        scrollbar.config( command = Lb1.yview )
        conn.close()
        
    conn = sqlite3.connect('jornadas.db')
    cursor_j = conn.execute("SELECT COUNT(DISTINCT NUMERO_JORNADA) from JORNADA")
    num_jornadas= cursor_j.fetchone()[0]
    conn.close()
    
    v = Toplevel()
    L1 = Label(v, text="Número jornada")
    L1.pack( side = LEFT)
    w = Spinbox(v, from_=1, to=num_jornadas)
    w.bind("<Return>", listar_por_numero_jornada)
    w.pack()
    

def estadisticas_jornada():
    def computar_estadisticas(event):
        total_goles = 0
        empates = 0
        victorias_locales = 0
        victorias_visitantes = 0
        conn = sqlite3.connect('jornadas.db')
        num = '% ' + w.get() + ''
        cursor_1 = conn.execute("SELECT NUMERO_JORNADA ,EQUIPO_LOCAL,EQUIPO_VISITANTE,RESULTADO from JORNADA WHERE NUMERO_JORNADA LIKE ?",  (num,))
        v = Toplevel()
        Lb1 = Listbox(v, width=150)
        Lb1.insert(END, str(cursor_1.fetchone()[0]))
        Lb1.insert(END, "------------------------------------------------------")
        for row in cursor_1:
            lista_goles = str(row[3]).split("-")
            goles_local = int(lista_goles[0])
            goles_visitante = int(lista_goles[1])
            total_goles += goles_local
            total_goles += goles_visitante
            if(goles_local>goles_visitante):
                victorias_locales+=1
            elif(goles_local == goles_visitante):
                empates+=1
            else:
                victorias_visitantes+=1
        Lb1.insert(END, "TOTAL GOLES JORNADA: " + str(total_goles))
        Lb1.insert(END, "")
        Lb1.insert(END, "Empates: " + str(empates))
        Lb1.insert(END, "Victorias locales: " + str(victorias_locales))
        Lb1.insert(END, "Victorias visitantes: " + str(victorias_visitantes))
        Lb1.pack(side = LEFT, fill = BOTH )
        conn.close()
    
    
    conn = sqlite3.connect('jornadas.db')
    cursor_j = conn.execute("SELECT COUNT(DISTINCT NUMERO_JORNADA) from JORNADA")
    num_jornadas= cursor_j.fetchone()[0]
    conn.close()
    
    v = Toplevel()
    L1 = Label(v, text="Número jornada")
    L1.pack( side = LEFT)
    w = Spinbox(v, from_=1, to=num_jornadas)
    w.bind("<Return>", computar_estadisticas)
    w.pack()
def ventana_principal():
        
    root = Tk()
    
    B1 = Button(root, text ="Almacenar resultados", command = cargar)
    B2 = Button(root, text ="Listar jornadas", command = listar_jornadas)
    B3 = Button(root, text ="Buscar por jornada", command = buscar_por_jornada)
    B4 = Button(root, text ="Estadisticas jornada", command = estadisticas_jornada)
    
    
    B1.place(x=50,y=10)
    B2.place(x=50,y=40)
    B3.place(x=50,y=70)
    B4.place(x=50,y=100)
    root.mainloop()
    
    
    
ventana_principal()