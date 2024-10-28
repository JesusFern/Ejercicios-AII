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
    # Cambiar url y empezar scrapping
    url = ""
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f, "lxml")
    
def almacenar_bd():
    #Aqui se crea la db.
    
    lista =  extraer_elementos()

def cargar():
    #BORRAR ESTA LINEA // => Esta función será la que llamaremos siempre en el ejercicio que pida hacer la carga dee datos
    sure = messagebox.askyesno("Are you sure?", "¿Seguro que quieres cargar los datos?")
    if sure:
        almacenar_bd();   
def ventana_principal():
        
    root = Tk()
    
    #Crear aqui configuración de menú / botones según pida el ejercicio
    
    root.mainloop()
    
#ventana_principal()
#Descomentar linea superior cuando se empiece a crear el programa con Tkinter.


    