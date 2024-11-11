#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, shutil
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, NUMERIC, KEYWORD, ID, DATETIME
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
from datetime import datetime
from whoosh.query import DateRange

PAGINAS = 3  #numero de paginas

# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
    
    
def cargar():
    respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere recargar los datos. \nEsta operaciÃ³n puede ser lenta")
    if respuesta:
        almacenar_datos()
    
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
        lista.append((titulo,titulo_original,paises,fecha_estreno,director,generos, url,sinopsis))
    return lista

def almacenar_datos():
    #define el esquema de la informaciÃ³n
    schem = Schema(titulo=TEXT(stored=True,phrase=False), titulo_original=TEXT(stored=True,phrase=False) ,paises=KEYWORD(stored=True,commas=True,lowercase=True) ,
                   fecha_estreno=DATETIME(stored=True), director=KEYWORD(stored=True,commas=True,lowercase=True), generos=KEYWORD(stored=True,commas=True,lowercase=True),
                   sinopsis=TEXT(stored=True,phrase=False) , url=ID(stored=True,unique=True))
    
    #eliminamos el directorio del Ã­ndice, si existe
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
    
    #creamos el Ã­ndice
    ix = create_in("Index", schema=schem)
    #creamos un writer para poder aÃ±adir documentos al indice
    writer = ix.writer()
    i=0
    lista=extraer_peliculas()
    for j in lista:
        #aÃ±ade cada pelicula de la lista al Ã­ndice
        writer.add_document(titulo=str(j[0]), titulo_original=str(str(j[1])), paises=str(j[2]), 
                            fecha_estreno=(j[3]), director=str(j[4]), generos=str(j[5]) , url = str(j[6]), sinopsis= str(j[7]))    
        i+=1
    writer.commit()
    messagebox.showinfo("Fin de indexado", "Se han indexado "+str(i)+ " juegos")    
    
def buscar_titulo_sinopsis():
    def mostrar_lista(event):
        #abrimos el Ã­ndice
        ix=open_dir("Index")
        #creamos un searcher en el Ã­ndice    
        with ix.searcher() as searcher:
            #se crea la consulta: buscamos en los campos "titulo" o "sinopsis" alguna de las palabras que hay en el Entry "en"
            #se usa la opciÃ³n OrGroup para que use el operador OR por defecto entre palabras, en lugar de AND
            query = MultifieldParser(["titulo","sinopsis"], ix.schema, group=OrGroup).parse(str(en.get()))
            #llamamos a la funciÃ³n search del searcher, pasÃ¡ndole como parÃ¡metro la consulta creada
            results = searcher.search(query) #sÃ³lo devuelve los 10 primeros
            #recorremos los resultados obtenidos(es una lista de diccionarios) y mostramos lo solicitado
            v = Toplevel()
            v.title("Listado de Peliculas")
            v.geometry('800x150')
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=BOTTOM, fill = BOTH)
            sc.config(command = lb.yview)
            #Importante: el diccionario solo contiene los campos que han sido almacenados(stored=True) en el Schema
            for r in results: 
                lb.insert(END,r['titulo'])
                lb.insert(END,r['titulo_original'])
                lb.insert(END,r['director'])
                lb.insert(END,'')
    v = Toplevel()
    v.title("Busqueda por Titulo o Sinopsis")
    l = Label(v, text="Introduzca las palabras a buscar:")
    l.pack(side=LEFT)
    en = Entry(v)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)
    
def buscar_generos():
    def mostrar_lista_por_genero(event):
        # Abrimos el índice
        ix = open_dir("Index")
        
        # Creamos un searcher en el índice
        with ix.searcher() as searcher:
            #lista de todos los gÃ©neros disponibles en el campo de gÃ©neros
            lista_generos = [i.decode('utf-8') for i in searcher.lexicon('generos')]
            # en la entrada ponemos todo en minÃºsculas
            entrada = str(en.get().lower())
            #si la entrada no estÃ¡ en la lista de gÃ©neros disponibles, da un error e informa de los gÃ©neros disponibles     
            if entrada not in lista_generos:
                messagebox.showinfo("Error", "El criterio de bÃºsqueda no es un gÃ©nero existente\nLos gÃ©neros existentes son: " + ",".join(lista_generos))
                return
            # Creamos la consulta: buscamos solo en el campo "generos" la palabra que está en el Entry "en"
            # `QueryParser` solo apunta a un campo en este caso (generos)
            query = QueryParser("generos", ix.schema).parse('"'+entrada+'"')
            
            # Llamamos a la función search del searcher, limitando a los primeros 20 resultados
            results = searcher.search(query, limit=20)
            
            # Creamos una ventana para mostrar los resultados
            v = Toplevel()
            v.title("Listado de Películas por Género")
            v.geometry('800x300')
            
            # Scrollbar y Listbox para los resultados
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=LEFT, fill=BOTH, expand=True)
            sc.config(command=lb.yview)
            
            # Mostramos los resultados en la Listbox
            for r in results:
                lb.insert(END, f"Título: {r['titulo']}")
                lb.insert(END, f"Título Original: {r['titulo_original']}")
                lb.insert(END, f"Paises: {r['paises']}")
                lb.insert(END, "----------------------")
                
    # Configuración de la ventana de entrada para buscar por género
    v = Toplevel()
    v.title("Búsqueda por Género")
    l = Label(v, text="Introduzca el género a buscar:")
    l.pack(side=LEFT)
    
    # Entry para ingresar el género
    en = Entry(v)
    en.bind("<Return>", mostrar_lista_por_genero)  # Ejecuta la búsqueda al presionar Enter
    en.pack(side=LEFT)
    
def buscar_fecha():
    def mostrar_lista_por_fecha(event):
        # Obtener las fechas del Entry
        rango_fechas = en.get().split()
        
        if len(rango_fechas) != 2:
            print("Formato incorrecto. Debe ingresar dos fechas en el formato AAAAMMDD AAAAMMDD.")
            return
        
        try:
            # Convertir las fechas de texto a objetos de tipo datetime
            fecha_inicio = datetime.strptime(rango_fechas[0], "%Y%m%d")
            fecha_fin = datetime.strptime(rango_fechas[1], "%Y%m%d")
        except ValueError:
            print("Error en el formato de fecha. Asegúrese de que esté en el formato AAAAMMDD.")
            return
        
        # Abrimos el índice
        ix = open_dir("Index")
        
        # Creamos un searcher en el índice
        with ix.searcher() as searcher:
            # Crear la consulta de rango en el campo `fecha_estreno`
            query = DateRange("fecha_estreno", fecha_inicio, fecha_fin)
            
            # Ejecutar la búsqueda sin límite para obtener todas las películas en el rango de fechas
            results = searcher.search(query, limit=None)
            
            # Crear la ventana para mostrar los resultados
            v = Toplevel()
            v.title("Listado de Películas por Rango de Fecha")
            v.geometry('500x300')
            
            # Scrollbar y Listbox para los resultados
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=LEFT, fill=BOTH, expand=True)
            sc.config(command=lb.yview)
            
            # Mostrar los resultados en la Listbox
            for r in results:
                titulo = r['titulo']
                fecha = r['fecha_estreno'].strftime("%Y-%m-%d")  # Formato de fecha legible
                lb.insert(END, f"Título: {titulo}")
                lb.insert(END, f"Fecha de Estreno: {fecha}")
                lb.insert(END, "----------------------")
                
    # Configuración de la ventana de entrada para buscar por rango de fechas
    v = Toplevel()
    v.title("Búsqueda por Rango de Fecha de Estreno")
    l = Label(v, text="Introduzca el rango de fechas (AAAAMMDD AAAAMMDD):")
    l.pack(side=LEFT)
    
    # Entry para ingresar el rango de fechas
    en = Entry(v)
    en.bind("<Return>", mostrar_lista_por_fecha)  # Ejecuta la búsqueda al presionar Enter
    en.pack(side=LEFT)
    
# permite buscar una pelÃ­cula por su tÃ­tulo y modificar su fecha de estreno
def modificar_fecha():
    def modificar():
        #comprobamos el formato de la entrada
        if(not re.match("\d{8}",en1.get())):
            messagebox.showinfo("Error", "Formato del rango de fecha incorrecto")
            return
        ix=open_dir("Index")
        lista=[]    # lista de las pelÃ­culas a modificar, usamos el campo url (unique) para updates 
        with ix.searcher() as searcher:
            query = QueryParser("titulo", ix.schema).parse(str(en.get()))
            results = searcher.search(query, limit=None) 
            v = Toplevel()
            v.title("Listado de PelÃ­culas a Modificar")
            v.geometry('800x150')
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=BOTTOM, fill = BOTH)
            sc.config(command = lb.yview)
            for r in results:
                lb.insert(END,r['titulo'])
                lb.insert(END,r['fecha_estreno'])
                lb.insert(END,'')
                lista.append(r) #cargamos la lista con los resultados de la bÃºsqueda
        # actualizamos con la nueva fecha de estreno todas las pelÃ­culas de la lista
        respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere modificar las fechas de estrenos de estas peliculas?")
        if respuesta:
            writer = ix.writer()
            for r in lista:
                writer.update_document(url=r['url'], fecha_estreno=datetime.strptime(str(en1.get()),'%Y%m%d'), titulo=r['titulo'], titulo_original=r['titulo_original'], paises=r['paises'], director=r['director'], generos=r['generos'], sinopsis=r['sinopsis'])
            writer.commit()
    
    v = Toplevel()
    v.title("Modificar Fecha Estreno")
    l = Label(v, text="Introduzca TÃ­tulo PelÃ­cula:")
    l.pack(side=LEFT)
    en = Entry(v)
    en.pack(side=LEFT)
    l1 = Label(v, text="Introduzca Fecha Estreno AAAAMMDD:")
    l1.pack(side=LEFT)
    en1 = Entry(v)
    en1.pack(side=LEFT)
    bt = Button(v, text='Modificar', command=modificar)
    bt.pack(side=LEFT)


def ventana_principal():       
    root = Tk()
    root.geometry("150x100")

    menubar = Menu(root)
    
    datosmenu = Menu(menubar, tearoff=0)
    datosmenu.add_command(label="Cargar", command=cargar)
    datosmenu.add_separator()   
    datosmenu.add_command(label="Salir", command=root.quit)
    
    menubar.add_cascade(label="Datos", menu=datosmenu)
    
    buscarmenu = Menu(menubar, tearoff=0)
    buscarmenu.add_command(label="Titulo o sinopsis", command=buscar_titulo_sinopsis)
    buscarmenu.add_command(label="Generos", command=buscar_generos)
    buscarmenu.add_command(label="Fecha", command=buscar_fecha)
    buscarmenu.add_command(label="Modificar fecha", command=modificar_fecha)
    
    menubar.add_cascade(label="Buscar", menu=buscarmenu)
    
    root.config(menu=menubar)
    root.mainloop()

if __name__ == "__main__":
    ventana_principal()