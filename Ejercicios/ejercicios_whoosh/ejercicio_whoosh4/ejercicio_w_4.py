#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, os, shutil
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, DATETIME, KEYWORD, ID, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
from whoosh import query
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
    # Define el encabezado User-Agent para hacer la solicitud
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
    req = urllib.request.Request("https://www.recetasgratis.net/Recetas-de-Aperitivos-tapas-listado_receta-1_1.html", headers=headers)
    
    # Realiza la solicitud y procesa la página principal
    f = urllib.request.urlopen(req)
    s = BeautifulSoup(f,"lxml")
    l= s.find_all("div", class_=['resultado','link'])
    for i in l:
        titulo = i.a.string.strip()
        comensales = i.find("span",class_="comensales")
        if comensales:
            comensales = int(comensales.string.strip())
        else:
            comensales=-1
        
        receta_url = i.find('a')['href']
        req_receta = urllib.request.Request(receta_url, headers=headers)
        f1 = urllib.request.urlopen(req_receta)
        s1 = BeautifulSoup(f1, "lxml")
        autor = s1.find("div", class_='nombre_autor').a.string.strip()
        fecha = s1.find("div", class_='nombre_autor').find('span', class_="date_publish").string
        fecha = fecha.replace('Actualizado:','').strip()
        fecha = datetime.strptime(fecha, "%d %B %Y")
        introduccion = s1.find("div", class_="intro").text
        caracteristicas = s1.find("div", class_="properties inline")
        if caracteristicas:
            caracteristicas = caracteristicas.text.replace("Características adicionales:","")
            caracteristicas = ",".join([c.strip() for c in caracteristicas.split(",")] )     
        else:
            caracteristicas = "sin definir"
        lista.append((titulo, comensales, autor, fecha, caracteristicas,introduccion))
    
    return lista

def almacenar_datos():
    #define el esquema de la informaciÃ³n
    schem = Schema(titulo=TEXT(stored=True,phrase=False), comensales=NUMERIC(stored=True, numtype=int), autor=ID(stored=True), fecha=DATETIME(stored=True), caracteristicas=KEYWORD(stored=True,commas=True,lowercase=True), introduccion=TEXT(stored=True,phrase=False))
    #eliminamos el directorio del Ã­ndice, si existe
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
    
    #creamos el Ã­ndice
    ix = create_in("Index", schema=schem)
    
    #creamos un writer para poder aÃ±adir documentos al indice
    writer = ix.writer()
    i=0
    lista=extraer_recetas()
    for receta in lista:
        #aÃ±ade cada pelicula de la lista al Ã­ndice
        writer.add_document(titulo=str(receta[0]), comensales=int(str(receta[1])), autor=str(receta[2]), fecha=receta[3], caracteristicas=str(receta[4]), introduccion=str(receta[5]))    
        i+=1
    writer.commit()
    messagebox.showinfo("Fin de indexado", "Se han indexado "+str(i)+ " recetas") 
    
def listar(results):      
    v = Toplevel()
    v.title("RECETAS DE COCINA DE RECETAS GRATIS")
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in results:
        s = 'TITULO: ' + row['titulo']
        lb.insert(END, s)       
        s = "COMENSALES: " + str(row['comensales'])
        lb.insert(END, s)
        s = "AUTOR: " + row['autor']
        lb.insert(END, s)
        s = "FECHA: " + row['fecha'].strftime('%d-%m-%Y')
        lb.insert(END, s)
        s = "CARACTERISTICAS: " + row['caracteristicas']
        lb.insert(END, s)
        s = "INTRODUCCION: " + row['introduccion']
        lb.insert(END, s)
        lb.insert(END,"------------------------------------------------------------------------\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)
    
def buscar_titulo_introduccion():
    def mostrar_lista(event):
        #abrimos el Ã­ndice
        ix=open_dir("Index")
        #creamos un searcher en el Ã­ndice    
        with ix.searcher() as searcher:
            #se crea la consulta: buscamos en los campos "titulo" o "sinopsis" alguna de las palabras que hay en el Entry "en"
            #se usa la opciÃ³n OrGroup para que use el operador OR por defecto entre palabras, en lugar de AND
            query = MultifieldParser(["titulo","introduccion"], ix.schema, group=OrGroup).parse(str(en.get()))
            #llamamos a la funciÃ³n search del searcher, pasÃ¡ndole como parÃ¡metro la consulta creada
            results = searcher.search(query, limit=3) #sÃ³lo devuelve los 3 primeros
            #recorremos los resultados obtenidos(es una lista de diccionarios) y mostramos lo solicitado
            v = Toplevel()
            v.title("Listado de Recetas")
            v.geometry('800x150')
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=BOTTOM, fill = BOTH)
            sc.config(command = lb.yview)
            #Importante: el diccionario solo contiene los campos que han sido almacenados(stored=True) en el Schema
            for r in results: 
                lb.insert(END,r['titulo'])
                lb.insert(END,"    Introduccion: "+r['introduccion'])
                lb.insert(END,'')
    v = Toplevel()
    v.title("Busqueda por Titulo o Introduccion")
    l = Label(v, text="Introduzca las palabras a buscar:")
    l.pack(side=LEFT)
    en = Entry(v)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)

def buscar_fecha():
    def mostrar_lista(event):
        #comprobamos el formato de la entrada
        if not re.match(r"\d{2}/\d{2}/\d{4}\s+\d{2}/\d{2}/\d{4}", en.get()):
            messagebox.showinfo("Error", "Formato del rango de fecha incorrecto. Use DD/MM/AAAA DD/MM/AAAA.")
            return

        ix=open_dir("Index")      
        with ix.searcher() as searcher:
            
            # Dividimos la entrada en las dos fechas y convertimos al formato AAAAMMDD
            aux = en.get().split()
            try:
                fecha_inicio = datetime.strptime(aux[0], "%d/%m/%Y").strftime("%Y%m%d")
                fecha_fin = datetime.strptime(aux[1], "%d/%m/%Y").strftime("%Y%m%d")
            except ValueError:
                messagebox.showinfo("Error", "Formato de fecha incorrecto. Use DD/MM/AAAA DD/MM/AAAA.")
                return
            rango_fecha = f"[{fecha_inicio} TO {fecha_fin}]"
            query = QueryParser("fecha", ix.schema).parse(rango_fecha)
            results = searcher.search(query,limit=None) #devuelve todos los resultados
            listar(results)
    
    v = Toplevel()
    v.title("Busqueda por Fecha")
    l = Label(v, text="Introduzca rango de fechas DD/MM/AAAA DD/MM/AAAA:")
    l.pack(side=LEFT)
    en = Entry(v)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)

def buscar_caracteristicas_titulo():
    def mostrar_lista():    
        with ix.searcher() as searcher:
            entrada = '"'+str(sp.get())+'"' #se ponen comillas porque hay categorÃ­as con mÃ¡s de una palabra
            query = QueryParser("caracteristicas", ix.schema).parse(entrada) & QueryParser("titulo", ix.schema).parse(en.get())
            results = searcher.search(query,limit=10)
            listar(results)
    v = Toplevel()
    v.title("Busqueda por Caracteristicas y titulo")
    l = Label(v, text="Seleccione tematica y titulo a buscar:")
    l.pack(side=LEFT)
    
    ix=open_dir("Index")      
    with ix.searcher() as searcher:
        #lista de todas las temÃ¡ticas disponibles en el campo de temÃ¡ticas
        lista_caracteristicas = [i.decode('utf-8') for i in searcher.lexicon('caracteristicas')]
    
    sp = Spinbox(v, values=lista_caracteristicas, state="readonly")
    sp.pack(side=LEFT)
    en = Entry(v)
    en.pack(side=LEFT)
    boton_buscar = Button(v, text="Buscar", command=mostrar_lista)
    boton_buscar.pack(side=LEFT)


def ventana_principal():
    def listar_todo():
        ix=open_dir("Index")
        with ix.searcher() as searcher:
            results = searcher.search(query.Every(),limit=None)
            listar(results) 
        
    root = Tk()
    menubar = Menu(root)
    
    datosmenu = Menu(menubar, tearoff=0)
    datosmenu.add_command(label="Cargar", command=cargar)
    datosmenu.add_command(label="Listar", command=listar_todo)
    datosmenu.add_separator()
    datosmenu.add_command(label="Salir", command=root.quit)
    
    menubar.add_cascade(label="Datos", menu=datosmenu)
    
    buscarmenu = Menu(menubar, tearoff=0)
    buscarmenu.add_command(label="Titulo o Introduccion", command=buscar_titulo_introduccion)
    buscarmenu.add_command(label="Fecha", command=buscar_fecha)
    buscarmenu.add_command(label="Características y Título", command=buscar_caracteristicas_titulo)
    
    menubar.add_cascade(label="Buscar", menu=buscarmenu)
    
    root.config(menu=menubar)
    root.mainloop()

    

if __name__ == "__main__":
    ventana_principal()