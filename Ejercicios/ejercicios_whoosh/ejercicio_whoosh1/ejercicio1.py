  #encoding:latin-1
import os
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME, ID
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh import qparser, query
from tkinter import *
from tkinter import messagebox
from whoosh.query import DateRange

agenda={}
dirdocs="Docs\Correos"
dirindex="Index"
dirage="Docs\Agenda"

def crea_index():
    def carga():
        sch = Schema(remitente=TEXT(stored=True), 
                     destinatarios=KEYWORD(stored=True), 
                     fecha=DATETIME(stored=True), 
                     asunto=TEXT(stored=True), 
                     contenido=TEXT(stored=True,phrase=False), 
                     nombrefichero=ID(stored=True))
        
        ix = create_in(dirindex, schema=sch)
        writer = ix.writer()
        for docname in os.listdir(dirdocs):
            if not os.path.isdir(dirdocs+docname):
                add_doc(writer, dirdocs, docname)                  
        writer.commit()
        messagebox.showinfo("INDICE CREADO", "Se han cargado " + str(ix.reader().doc_count()) + " documentos")
    
    if not os.path.exists(dirdocs):
        messagebox.showerror("ERROR", "No existe el directorio de documentos " + dirdocs)
    else:
        if not os.path.exists(dirindex):
            os.mkdir(dirindex)
    if not len(os.listdir(dirindex))==0:
        respuesta = messagebox.askyesno("Confirmar","Indice no vacÃ­o. Desea reindexar?") 
        if respuesta:
            carga()           
    else:
        carga()

def add_doc(writer, path, docname):
    try:
        fileobj=open(path+'\\'+docname, "r")
        rte=fileobj.readline().strip()
        dtos=fileobj.readline().strip()
        f=fileobj.readline().strip()
        dat=datetime.strptime(f,'%Y%m%d')
        ast=fileobj.readline().strip()
        ctdo=fileobj.read()
        fileobj.close()           
        
        writer.add_document(remitente=rte, destinatarios=dtos, fecha=dat, asunto=ast, contenido=ctdo, nombrefichero=docname)
    
    except:
        messagebox.showerror("ERROR", "Error: No se ha podido aÃ±adir el documento "+path+'\\'+docname)
 
 
def crea_agenda():
    try:
        fileobj=open(dirage+"\\" + "agenda.txt", "r")
        email=fileobj.readline()
        while email:
            nombre=fileobj.readline()
            agenda[email.strip()]=nombre.strip()
            email=fileobj.readline()
            
        for email,nombre in agenda.items():
            print("Email agenda: " + email + " , Nombre en agenda: " + nombre)
            
    except:
        messagebox.showerror("ERROR", "Error: No se ha podido aÃ±adir el documento "+dirage+'\\'+"agenda.txt")
               
def cargar():
    crea_index()
    crea_agenda()        

def listar(results):      
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in results:
        s = 'REMITENTE: ' + row['remitente']
        lb.insert(END, s)       
        s = "DESTINATARIOS: " + row['destinatarios']
        lb.insert(END, s)
        s = "FECHA: " + row['fecha'].strftime('%d-%m-%Y')
        lb.insert(END, s)
        s = "ASUNTO: " + row['asunto']
        lb.insert(END, s)
        s = "CUERPO: " + row['contenido']
        lb.insert(END, s)
        lb.insert(END,"------------------------------------------------------------------------\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)

def buscar_cuerpo_asunto():
    def listar_por_cuerpo_o_asunto(event):
        consulta = entry.get().strip()
        try:
            ix = open_dir(dirindex)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el �ndice: {str(e)}")
            return
        with ix.searcher() as searcher:
            parser = MultifieldParser(["asunto", "contenido"], schema=ix.schema)
            query = parser.parse(consulta)
            results = searcher.search(query, limit=None)
        
            v = Toplevel()
            scrollbar = Scrollbar(v)
            scrollbar.pack( side = RIGHT, fill=Y )
            lb = Listbox(v, width=150, yscrollcommand = scrollbar.set)
            for row in results:
                s = 'REMITENTE: ' + row['remitente']
                lb.insert(END, s)       
                s = "DESTINATARIOS: " + row['destinatarios']
                lb.insert(END, s)
                s = "FECHA: " + row['fecha'].strftime('%d-%m-%Y')
                lb.insert(END, s)
                s = "ASUNTO: " + row['asunto']
                lb.insert(END, s)
                s = "CUERPO: " + row['contenido']
                lb.insert(END, s)
                lb.insert(END,"------------------------------------------------------------------------\n")
            lb.pack(side = LEFT, fill = BOTH )
            scrollbar.config( command = lb.yview )
        
    v = Toplevel()
    L1 = Label(v, text="Cuerpo o Asunto: ")
    L1.pack( side = LEFT)
    entry = Entry(v, bd =5)
    entry.bind("<Return>", listar_por_cuerpo_o_asunto)
    entry.pack(side=LEFT)
    
def buscar_por_fecha():
    def listar_por_fecha(event):
        fecha_input = entry.get().strip()
        
        try:
            fecha = datetime.strptime(fecha_input, '%Y%m%d')
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha incorrecto. Use YYYYMMDD.")
            return
        
        try:
            ix = open_dir(dirindex)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el �ndice: {str(e)}")
            return
        

        with ix.searcher() as searcher:
            query = DateRange("fecha", start=fecha, end=None)
            results = searcher.search(query, limit=None)
            

            resultados = []
            for result in results:
                resultados.append({
                    'remitente': result['remitente'],
                    'destinatarios': result['destinatarios'],
                    'fecha': result['fecha'].strftime('%d-%m-%Y'),
                    'asunto': result['asunto'],
                    'contenido': result['contenido']
                })

        v_result = Toplevel()
        v_result.title("Resultados de la b�squeda por Fecha")
        scrollbar = Scrollbar(v_result)
        scrollbar.pack(side=RIGHT, fill=Y)
        Lb1 = Listbox(v_result, width=150, yscrollcommand=scrollbar.set)
        
        if len(resultados) == 0:
            Lb1.insert(END, "No se encontraron correos posteriores a la fecha ingresada.")
        else:
            for row in resultados:
                Lb1.insert(END, 'REMITENTE: ' + row['remitente'])
                Lb1.insert(END, 'DESTINATARIOS: ' + row['destinatarios'])
                Lb1.insert(END, 'FECHA: ' + row['fecha'])
                Lb1.insert(END, 'ASUNTO: ' + row['asunto'])
                Lb1.insert(END, 'CUERPO: ' + row['contenido'])
                Lb1.insert(END, "------------------------------------------------------")
        
        Lb1.pack(side=LEFT, fill=BOTH)
        scrollbar.config(command=Lb1.yview)
    v = Toplevel()
    v.title("Buscar por Fecha (YYYYMMDD)")
    
    L1 = Label(v, text="Fecha (YYYYMMDD): ")
    L1.pack(side=LEFT)
    
    entry = Entry(v, bd=5)
    entry.bind("<Return>", listar_por_fecha)
    entry.pack(side=LEFT)
def ventana_principal():
    def listar_todo():
        ix=open_dir(dirindex)
        with ix.searcher() as searcher:
            results = searcher.search(query.Every(),limit=None)
            listar(results) 
    
    raiz = Tk()

    menu = Menu(raiz)

    #DATOS
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_command(label="Listar", command=listar_todo)
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos)

    #BUSCAR
    menubuscar = Menu(menu, tearoff=0)
    menubuscar.add_command(label="Por cuerpo o asunto", command=buscar_cuerpo_asunto)
    menubuscar.add_command(label="Por fecha", command=buscar_por_fecha)
    menu.add_cascade(label="Buscar", menu=menubuscar)
    raiz.config(menu=menu)

    raiz.mainloop()


if __name__ == "__main__":
    ventana_principal()
