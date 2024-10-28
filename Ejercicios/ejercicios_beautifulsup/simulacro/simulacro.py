import urllib.request
from bs4 import BeautifulSoup
import sqlite3
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from urllib.request import Request, urlopen
from datetime import datetime

# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
    
def extraer_elementos():
    # Cambiar url y empezar scrapping
    lista = []
  
    for num_pagina in range(1,3):
        url = "https://www.metacritic.com/browse/game/?releaseYearMin=1958&releaseYearMax=2024&page="
        url = url + str(num_pagina)
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = Request(url,headers=hdr)
        f = urllib.request.urlopen(req)
        s = BeautifulSoup(f, "lxml")
        lista_una_pagina = s.find("div", class_="c-productListings").find_all("div", class_="c-finderProductCard c-finderProductCard-game")
        lista.extend(lista_una_pagina)
  
    return lista
 
def almacenar_bd():
    conn = sqlite3.connect('juegos.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS JUEGOS")
    conn.execute('''CREATE TABLE JUEGOS
      (TITULO                     TEXT NOT NULL,
       CONSOLA                    TEXT,
       LANZAMIENTO                TEXT,
       METASCORE                  INT,         
       USER_SCORE                 FLOAT,
       RATING                     TEXT,
       SUMMARY                    TEXT,
       DEVELOPER                  TEXT,
       PUBLISHER                  TEXT,
       GENEROS                    TEXT);''')
  
    lista =  extraer_elementos()
  
    for juego in lista:
        url = "https://www.metacritic.com" + juego.a['href']
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = Request(url,headers=hdr)
        f = urllib.request.urlopen(req)
        s = BeautifulSoup(f, 'lxml')
        detalles = s.find("div", class_="c-productHero_score-container u-flexbox u-flexbox-column g-bg-white")
      
        nombre_juego = juego.a.find("div", class_="c-finderProductCard_info u-flexbox-column").find("div").attrs['data-title']
        consola = detalles.find("div", class_="c-ProductHeroGamePlatformInfo u-flexbox g-outer-spacing-bottom-medium").div.div
        if consola.string:
            consola = consola.string.strip()
        else:
            consola = consola.svg.title.string.strip()
        fecha_lanzamiento = detalles.find("div", class_="g-text-xsmall").span.find_next_sibling("span").string.strip()
        metascore = juego.find("div", class_="c-finderProductCard_meta g-outer-spacing-top-auto").span.div.div.span.string.strip()
        summary = juego.find("div", class_="c-finderProductCard_description").span.string.strip()
      
        user_score = s.find("div","c-productScoreInfo u-clearfix").find("div", "c-productScoreInfo_scoreNumber u-float-right").span.string.strip()
        rating = s.find("div" , class_="c-productionDetailsGame_esrb_title u-inline-block g-outer-spacing-left-medium-fluid")
        if rating:
            rating= rating.find("span",class_="u-block").string.strip()
        else:
            rating = "No tiene calificacion por edades"
    
        developer = s.find("li" , class_="c-gameDetails_listItem g-color-gray70 u-inline-block").string.strip()
        publisher = s.find("div","c-gameDetails_Distributor u-flexbox u-flexbox-row").find("span" , class_="g-outer-spacing-left-medium-fluid g-color-gray70 u-block").string.strip()
        list_genre = s.find("div",class_="c-gameDetails_sectionContainer u-flexbox u-flexbox-row u-flexbox-alignBaseline").find_all("li","c-genreList_item")
        genres= ""
        for g in list_genre:
            genre = g.a.find("span","c-globalButton_label").string.strip()
            genres = genres + genre + ","
      
        #print((nombre_juego, consola, datetime.strptime(fecha_lanzamiento, "%b %d, %Y").date(), metascore, user_score, rating, developer, publisher, genres))
      
        conn.execute("""INSERT INTO JUEGOS (TITULO, CONSOLA, LANZAMIENTO, METASCORE, USER_SCORE, RATING, SUMMARY, DEVELOPER, PUBLISHER, GENEROS)
        VALUES (?,?,?,?,?,?,?,?,?,?)""", (nombre_juego,consola,fecha_lanzamiento,int(metascore),float(user_score),rating,summary,developer,publisher,genre))
      
    conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM JUEGOS")
    messagebox.showinfo("Base Datos",
                       "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " juegos")
    conn.close()

              

def cargar():
    #BORRAR ESTA LINEA // => Esta función será la que llamaremos siempre en el ejercicio que pida hacer la carga dee datos
    sure = messagebox.askyesno("Are you sure?", "¿Seguro que quieres cargar los datos?")
    if sure:
        almacenar_bd();
        
        
def listar_juegos():
    conn = sqlite3.connect('juegos.db')
    cursor = conn.execute("SELECT TITULO ,CONSOLA,LANZAMIENTO from JUEGOS")
    v = Toplevel()
    scrollbar = Scrollbar(v)
    scrollbar.pack( side = RIGHT, fill=Y )
    Lb1 = Listbox(v, width=150, yscrollcommand = scrollbar.set)
    for row in cursor:
        Lb1.insert(END, "Titulo: "+ row[0] + " //// Consola: " + str(row[1]) + " //// Lanzamiento: "  + str(row[2]))
        Lb1.insert(END, "------------------------------------------------------")
    Lb1.pack(side = LEFT, fill = BOTH )
    scrollbar.config( command = Lb1.yview )
    conn.close()  
    
def listar_juegos_user_score():
    conn = sqlite3.connect('juegos.db')
    conn.text_factory = str 
    cursor = conn.execute("SELECT * FROM JUEGOS ORDER BY USER_SCORE DESC")
  
    v = Toplevel()
    v.title("LISTADO DE JUEGOS ORDENADOS POR USER SCORE")
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width = 150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(END,row[0])
        lb.insert(END,"    Consola: "+ row[1])
        lb.insert(END,"    Fecha de Lanzamiento: "+ row[2])
        lb.insert(END,"    Metascore: "+ str(row[3]))
        lb.insert(END,"    User Score: "+ str(row[4]))
        lb.insert(END,"    Rating: "+ row[5])
        lb.insert(END,"    Summary: "+ row[6])
        lb.insert(END,"    Publisher: "+ row[7])
        lb.insert(END,"    Developer: "+ row[8])
        lb.insert(END,"    Generos: "+ row[9])
        lb.insert(END,"\n\n")
    lb.pack(side=LEFT,fill=BOTH)
    sc.config(command = lb.yview)
  
    conn.close()


def buscar_por_publisher():
    def listar_por_publisher(event):
        conn = sqlite3.connect('juegos.db')
        pu = '%' + w.get() + '%'
        cursor_1 = conn.execute("SELECT TITULO ,CONSOLA,LANZAMIENTO,PUBLISHER from JUEGOS WHERE PUBLISHER LIKE ?",  (pu,))
        v = Toplevel()
        scrollbar = Scrollbar(v)
        scrollbar.pack( side = RIGHT, fill=Y )
        Lb1 = Listbox(v, width=150, yscrollcommand = scrollbar.set)
        for row in cursor_1:
            Lb1.insert(END, "Titulo: "+ row[0] + " //// Consola: " + str(row[1]) + " //// Lanzamiento: "  + str(row[2])+ " //// Publisher: "  + str(row[3]))
            Lb1.insert(END, "------------------------------------------------------")
        Lb1.pack(side = LEFT, fill = BOTH )
        scrollbar.config( command = Lb1.yview )
        conn.close()
        
        
    conn = sqlite3.connect('juegos.db')
    cursor_t = conn.execute("SELECT PUBLISHER from JUEGOS")
    publisher = set()
    for row in cursor_t:
        publisher.add(row[0].strip())
        
    conn.close()
    
    v = Toplevel()
    L1 = Label(v, text="Publisher")
    L1.pack( side = LEFT)
    w = Spinbox(v, value = list(publisher))
    w.bind("<Return>", listar_por_publisher)
    w.pack()
def buscar_por_palabra_clave_desc():
    def listar_por_publisher(event):
        conn = sqlite3.connect('juegos.db')
        pu = '%' + E1.get() + '%'
        cursor_1 = conn.execute("SELECT TITULO ,CONSOLA,LANZAMIENTO,SUMMARY from JUEGOS WHERE SUMMARY LIKE ?",  (pu,))
        v = Toplevel()
        scrollbar = Scrollbar(v)
        scrollbar.pack( side = RIGHT, fill=Y )
        Lb1 = Listbox(v, width=150, yscrollcommand = scrollbar.set)
        for row in cursor_1:
            Lb1.insert(END, "Titulo: "+ row[0] + " //// Consola: " + str(row[1]) + " //// Lanzamiento: "  + str(row[2])+ " //// Publisher: "  + str(row[3])+ " //// Summary: "  + str(row[3]))
            Lb1.insert(END, "------------------------------------------------------")
        Lb1.pack(side = LEFT, fill = BOTH )
        scrollbar.config( command = Lb1.yview )
        conn.close()
    
    top = Toplevel()
    L1 = Label(top, text="Palabra clave en descripcion")
    L1.pack( side = LEFT)
    E1 = Entry(top, bd =5)
    E1.bind("<Return>", listar_por_publisher)
    E1.pack(side = RIGHT)

def buscar_por_genero():
    def listar(event):
            conn = sqlite3.connect('juegos.db')
            conn.text_factory = str
            cursor = conn.execute("SELECT TITULO, SUMMARY, GENEROS FROM JUEGOS where GENEROS LIKE '%" + str(genero.get()) + "%'")
            conn.close
            v = Toplevel()
            v.title("LISTADO DE JUEGOS")
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, width = 150, yscrollcommand=sc.set)
            for row in cursor:
                lb.insert(END,row[0] + ":")
                lb.insert(END,"    Summary: "+ row[1])
                lb.insert(END,"    Generos: "+ row[2])
                lb.insert(END,"\n\n")
            lb.pack(side=LEFT,fill=BOTH)
            sc.config(command = lb.yview)
    
    conn = sqlite3.connect('juegos.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT DISTINCT GENEROS FROM JUEGOS")
    
    generos=set()
    for i in cursor:
        varios = i[0].split(",")
        for t in varios:
            generos.add(t.strip())

    v = Toplevel()
    label = Label(v,text="Seleccione el genero: ")
    label.pack(side=LEFT)
    genero = Spinbox(v, width= 30, values=list(generos))
    genero.bind("<Return>", listar)
    genero.pack(side=LEFT)
    
    conn.close()


def ventana_principal():
      
    raiz = Tk()
    menu = Menu(raiz)
  
    # DATOS
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos)
    
    menulistar = Menu(menu, tearoff=0)
    menulistar.add_command(label="Listar juegos", command=listar_juegos)
    menulistar.add_command(label="Listar juegos ordenados por user score", command=listar_juegos_user_score)
    menu.add_cascade(label="Listar", menu=menulistar)
    
    menubuscar = Menu(menu, tearoff=0)
    menubuscar.add_command(label="Buscar juegos por publisher", command=buscar_por_publisher)
    menubuscar.add_command(label="Buscar juegos por palabra clave en descripcion", command=buscar_por_palabra_clave_desc)
    menubuscar.add_command(label="Buscar juegos por genero", command=buscar_por_genero)
    menu.add_cascade(label="Buscar", menu=menubuscar)
    raiz.config(menu=menu)
    raiz.mainloop()




    
ventana_principal()