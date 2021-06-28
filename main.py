from sqlite3.dbapi2 import connect
from tkinter import Entry, Listbox, Tk, ttk, Frame, Label, messagebox
from tkinter.font import Font
import sqlite3
import re


'''================CONSTANTS==============='''
CONFIGURE_FILE="config.conf"

'''=============DATA STRUCTURES============'''
config=dict()

class Data_base:
    def __init__(self):
        conection=sqlite3.connect("database/DB")
        cursor = conection.cursor()
        try:
            #If dont exist the DB its created
            cursor.execute(
                '''
                CREATE TABLE INVENTARY (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                PRODUCTO VARCHAN(100) NOT NULL,
                CANTIDAD INT NOT NULL,
                PRECIO INT NOT NULL)
                '''
            )
            conection.commit()
            messagebox.showinfo("BASE DE DATOS CREADA","Se ha creado con exito la base de datos.")
            conection.close()
        except:
            #If exist the DB its shiw the next message
            messagebox.showinfo("BASE DE DATOS CONECTADA","Se ha conectado con exito a la base da datos.")
            conection.close()

    def get_inventary(self):
        conection=sqlite3.connect("database/DB")
        cursor = conection.cursor()
        try:
            cursor.execute("SELECT * FROM INVENTARY")
            conection.close()
            return cursor
        except Exception as e:
            conection.close()
            messagebox.showerror("ERROR",e)

if __name__=="__main__":

    #In first plac, read the config file, to set the config values
    regex = re.compile(r"(\w*) = \"(.*)\"") #Format: (name_conf) = (value)
    with open(CONFIGURE_FILE) as File: #Open config file
        for x in regex.findall(File.read()): #Read file
            config[x[0]]=x[1] #Config generate
    
    #Create the windows called root
    root=Tk()
    root.geometry("1280x720")
    root.title(config['ENTERPRISE_NAME'])
    root.resizable(width=0, height=0)

    Data_base()

    '''================================================================='''
    '''                             INTERFACE                           '''
    '''================================================================='''


    font_title=Font(size=20)
    Label(text=config["ENTERPRISE_NAME"],font=font_title,bg="white").pack(pady=10)

    #>>>>Products<<<<<

    frame_products=Frame(root)
    frame_products.place(x=10,y=40,relheight=.5,relwidth=.4)
    Label(frame_products,text="Buscar").grid(row=0,column=3,padx=10,pady=10)
    search_entry=Entry(frame_products,width=80)
    search_entry.grid(row=1,column=0,columnspan=7,padx=10)
    products=Listbox(frame_products,width=80).grid(row=2,column=0,columnspan=7,padx=10,pady=10)

    root.mainloop()
    