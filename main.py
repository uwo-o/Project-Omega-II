from sqlite3.dbapi2 import connect
from tkinter import Button, Entry, Listbox, StringVar, Tk, ttk, Frame, Label, messagebox
from tkinter.constants import CENTER, DISABLED, END, NO
from tkinter.font import Font
import sqlite3
import re


'''================CONSTANTS==============='''
CONFIGURE_FILE="config.conf"

'''=============DATA STRUCTURES============'''
config=dict()



class Aplication:
    def __init__(self,master=None):
        self.total_sell_cash=0
        self.to_sell=[]
        self.create_widgets()

    def create_widgets(self):


        '''================================================================='''
        '''                             INTERFACE                           '''
        '''================================================================='''


        self.search_var=StringVar()
        self.search_var.trace("w",self.update_products_list)

        self.products_quantity=StringVar()

        self.total=StringVar()
        self.total.set(str(self.total_sell_cash))

        Label(text=config["ENTERPRISE_NAME"],font=font_title).pack(pady=10)

        #>>>>Products<<<<<

        self.frame_products=Frame(root)
        self.frame_products.place(x=10,rely=0.1,relheight=.4,relwidth=1)

        self.frame_table_to_sell=Frame(root)
        self.frame_table_to_sell.place(x=10,rely=0.45,relheight=.5,relwidth=1)

        self.frame_buttons=Frame(root)
        self.frame_buttons.place(x=10,rely=.8,relheight=.2,relwidth=.5)

        Label(self.frame_products,text="Productos",font=font_big).grid(row=0,column=3,padx=10)
        Label(self.frame_products,text="Producto").grid(row=1,column=1,padx=10)

        self.search_entry=Entry(self.frame_products,width=60,textvariable=self.search_var)
        self.search_entry.grid(row=2,column=0,columnspan=4,padx=5)

        Label(self.frame_products,text="Cantidad").grid(row=1,column=5,padx=10)

        self.search_entry=Entry(self.frame_products,textvariable=self.products_quantity)
        self.search_entry.grid(row=2,column=5,padx=5)

        self.products_list=Listbox(self.frame_products,width=80)
        self.products_list.grid(row=3,column=0,columnspan=7,rowspan=5,padx=5,pady=10)
        self.products_list.bind('<Double-Button>', self.selected_list)

        self.add_button=Button(self.frame_products,text="Agregar",command=self.add_to_pre_sell).grid(row=2,column=6)

        Label(self.frame_table_to_sell,text="Venta",font=font_big).grid(row=0,column=4,padx=10)

        Label(self.frame_table_to_sell,text="Total",font=font_big).grid(row=5,column=5,padx=10,sticky='e')
        self.total_entry=Entry(self.frame_table_to_sell,textvariable=self.total,state=DISABLED)
        self.total_entry.grid(row=5,column=6,padx=10)


        self.table=ttk.Treeview(self.frame_table_to_sell)
        self.table.grid(row=1,column=0,columnspan=7,padx=10)

        self.table['columns']=("ID","Producto","Precio U.","Cantidad","Precio F.")

        self.table.column('#0', width=0, stretch=NO)
        self.table.column('ID', anchor=CENTER, width=50)
        self.table.column('Producto', anchor=CENTER, width=250)
        self.table.column('Precio U.', anchor=CENTER, width=100)
        self.table.column('Cantidad', anchor=CENTER, width=80)
        self.table.column('Precio F.', anchor=CENTER, width=100)

        self.table.heading('#0', text='', anchor=CENTER)
        self.table.heading('ID', text='ID', anchor=CENTER)
        self.table.heading('Producto', text='Producto', anchor=CENTER)
        self.table.heading('Precio U.', text='Precio U.', anchor=CENTER)
        self.table.heading('Cantidad', text='Cantidad', anchor=CENTER)
        self.table.heading('Precio F.', text='Precio F.', anchor=CENTER)

        self.products_button=Button(self.frame_buttons,text="Actualizar",command=self.update_products_list).grid(row=0,column=0,padx=5,pady=5)
        self.products_button=Button(self.frame_buttons,text="Productos").grid(row=1,column=0,padx=5)

        self.sell_button=Button(root,width=25,height=5,text="Generar Venta").place(relx=.7,rely=.85)
        self.cancel_button=Button(root,width=25,height=5,text="Cancelar",command=self.cancel).place(relx=.4,rely=.85)

        self.update_products_list()

    def cancel(self):
        self.search_var.set("")
        self.products_quantity.set("")
        self.total_sell_cash=0
        self.total.set(str(self.total_sell_cash))
        for x in self.to_sell:
            self.to_sell.pop()
        x=self.table.get_children()
        for item in x:
            self.table.delete(item)
        

    def add_to_pre_sell(self):
        data=Data_base().get_product(self.search_var.get())
        self.to_sell.append((data[0][0],int(self.products_quantity.get())))
        self.total_sell_cash+=int(data[0][3])*int(self.products_quantity.get())
        self.table.insert(parent='',index=0, values=(data[0][0],data[0][1],data[0][3],self.products_quantity.get(),int(data[0][3])*int(self.products_quantity.get())))
        self.total.set(str(self.total_sell_cash))
        self.search_var.set("")
        self.products_quantity.set("")

    def selected_list(self, *args):
        self.search_var.set(self.products_list.selection_get())
    
    def update_products_list(self, *args):
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
    
    def get_product(self,product):
        conection=sqlite3.connect("database/DB")
        cursor = conection.cursor()
        self.product_data=[]
        try:
            self.cursor=cursor.execute("SELECT * FROM INVENTARY WHERE PRODUCTO = '{}'".format(product))
            for x in self.cursor:
                self.product_data.append(x)
            conection.close()
            return self.product_data
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
    root.geometry("650x720")
    root.title(config['ENTERPRISE_NAME'])
    root.resizable(width=0, height=0)

    font_title=Font(size=20)
    font_big=Font(size=10)

    Data_base()
    Aplication(master=root)

    root.mainloop()
    