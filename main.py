from sqlite3.dbapi2 import connect
from tkinter import Button, Entry, Listbox, StringVar, Tk, ttk, Frame, Label, messagebox
from tkinter.constants import END
from tkinter.font import Font
import sqlite3
import re


'''================CONSTANTS==============='''
CONFIGURE_FILE="config.conf"

'''=============DATA STRUCTURES============'''
config=dict()



class Aplication:
    def __init__(self,master=None):
        self.create_widgets()

    def create_widgets(self):
        '''================================================================='''
        '''                             INTERFACE                           '''
        '''================================================================='''
        self.search_var=StringVar()
        self.search_var.trace("w",self.update_products_list)

        Label(text=config["ENTERPRISE_NAME"],font=font_title).pack(pady=10)

        #>>>>Products<<<<<

        self.frame_products=Frame(root)
        self.frame_products.place(x=10,y=40,relheight=.5,relwidth=.5)

        Label(self.frame_products,text="Productos",font=font_big).grid(row=0,column=3,padx=10)
        Label(self.frame_products,text="Buscar").grid(row=1,column=0,padx=10)

        self.search_entry=Entry(self.frame_products,width=70,textvariable=self.search_var)
        self.search_entry.grid(row=1,column=1,columnspan=6,padx=10)

        self.products_list=Listbox(self.frame_products,width=80)
        self.products_list.grid(row=2,column=0,columnspan=7,rowspan=5,padx=10,pady=10)
        self.products_list.bind('<Double-Button>', self.selected_list)

        self.add_button=Button(self.frame_products,text="Agregar",command=self.selected_list).grid(row=2,column=9)

        self.update_products_list()

    def selected_list(self, *args):
        print(self.products_list.selection_get())
    
    def update_products_list(self):
        search=self.search_var.get()

        products_list=[]

        list=Data_base().get_inventary()
        for x in list:
            products_list.append(x[1])

        products_list.sort()
        
        self.products_list.delete(0, END)

        for item in products_list:
            if search.lower() in item.lower():
                self.products_list.insert(END, item)

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
            conection.close()
        except:
            conection.close()

    def get_inventary(self):
        conection=sqlite3.connect("database/DB")
        cursor = conection.cursor()
        self.list=[]
        try:
            self.cursor=cursor.execute("SELECT * FROM INVENTARY")
            for x in self.cursor:
                self.list.append(x)
            conection.close()
            return self.list
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

    font_title=Font(size=20)
    font_big=Font(size=10)

    Data_base()
    Aplication(master=root)

    root.mainloop()
    