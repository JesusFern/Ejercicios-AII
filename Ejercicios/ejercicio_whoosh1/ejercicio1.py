  #encoding:latin-1
import os
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME, ID
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh import qparser, query
from tkinter import *
from tkinter import messagebox

agenda={}
dirdocs="Docs\Correos"
dirindex="Index"
dirage="Docs\Agenda"

def crea_index():
    def carga():
        sch = Schema(remitente=TEXT(stored=True), destinatarios=KEYWORD(stored=True), fecha=DATETIME(stored=True), asunto=TEXT(stored=True), contenido=TEXT(stored=True,phrase=False), nombrefichero=ID(stored=True))
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
        fileobj=open(dirage+'\\'+"agenda.txt", "r")
        email=fileobj.readline()
        while email:
            nombre=fileobj.readline()
            agenda[email.strip()]=nombre.strip()
            email=fileobj.readline()
    except:
        messagebox.showerror("ERROR", "No se ha podido crear la agenda. Compruebe que existe el fichero "+dirage+'\\'+"agenda.txt")
               
def cargar():
    crea_index()
    crea_agenda()        

