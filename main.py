from sqlite3.dbapi2 import connect
from tkinter import Button, Entry, Listbox, StringVar, Tk, ttk, Frame, Label, messagebox
from tkinter.constants import CENTER, DISABLED, END, NO
from tkinter.font import Font
from datetime import datetime
import sqlite3
import re


'''================CONSTANTS==============='''
CONFIGURE_FILE="config.conf"

'''=============DATA STRUCTURES============'''
config=dict()



class Aplication:
    def __init__(self,master=None):

        #I create utils

        self.total_sell_cash=0
        self.to_sell=[]
        self.sell={}

        #and i call this metod to create the work space

        self.create_widgets()

    def create_widgets(self):


        '''================================================================='''
        '''                             INTERFACE                           '''
        '''================================================================='''
        
        #Interface widgets creation.

        #its to search values in a list

        self.search_var=StringVar()
        self.search_var.trace("w",self.update_products_list)

        self.products_quantity=StringVar()

        self.total=StringVar()

        #Starts total cost entry in 0

        self.total.set(str(self.total_sell_cash))

        #I load the enterprise name

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

        #Here i create the table when the products to sell appears.

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

        self.refresh_button=Button(self.frame_buttons,text="Actualizar",command=self.update_products_list).grid(row=0,column=0,padx=5,pady=5)
        self.products_button=Button(self.frame_buttons,text="Productos",command=lambda:Edit_inventary()).grid(row=1,column=0,padx=5)

        self.cancel_button=Button(root,width=25,height=5,text="Cancelar",command=self.cancel).place(relx=.4,rely=.85)
        self.sell_button=Button(root,width=25,height=5,text="Generar Venta",command=self.create_sell).place(relx=.7,rely=.85)
        
        #and update the table

        self.update_products_list()

    def cancel(self):

        #this clean the variables, and reestart to 0 the hud

        self.search_var.set("")
        self.products_quantity.set("")
        self.total_sell_cash=0
        self.total.set(str(self.total_sell_cash))
        self.to_sell=[]
        x=self.table.get_children()
        for item in x:
            self.table.delete(item)    

    def create_sell(self):

        #I create a petition to sell

        self.sell={}
        exit=0

        #I obtain the id of the row in the table

        for x in self.table.get_children():

            #I revise value per value if this product is repeteated and plus them

            data=self.table.item(x)['values']
            if data[1] not in self.sell:
                self.sell[data[1]]=0
            self.sell[data[1]]+=data[3]
        
        #i comprobe the products stock

        for x in Data_base().get_inventary():
            if x[1] in self.sell:

                #If the result between the number of products and his stock is negative, we need more stock for x product

                if int(int(x[2])-self.sell[x[1]])<0:
                    messagebox.showerror("ERROR","El producto {} tiene stock insuficiente, cantidad: {}.".format(x[1],x[2]))

                    #exit flags is activated

                    exit=1
                    break
        if exit:
            pass

        else:
            
            #call to confirm sell class

            Confirm_sell(self.sell,self.total_entry.get())

            #clean entry's

            self.cancel()

    def add_to_pre_sell(self):

        #i call to database to obtain the product data about the entry

        data=Data_base().get_product(self.search_var.get())

        #I create this list to have the count of elements quantity

        self.to_sell.append((data[0][0],int(self.products_quantity.get())))

        #i plus the cost to have the final cost

        self.total_sell_cash+=int(data[0][3])*int(self.products_quantity.get())

        #i insert the values in the table

        self.table.insert(parent='',index=0, values=(data[0][0],data[0][1],data[0][3],self.products_quantity.get(),int(data[0][3])*int(self.products_quantity.get())))

        #i set the final price

        self.total.set(str(self.total_sell_cash))

        #i clean the variables

        self.search_var.set("")
        self.products_quantity.set("")

    def selected_list(self, *args):

        #this function is needed to get the values from a selected var in a list, doing double click

        self.search_var.set(self.products_list.selection_get())
    
    def update_products_list(self, *args):

        #This finction is to find the similar characters in a list

        #I load the shearch data

        search=self.search_var.get()

        #Match list
    
        products_list=[]
        
        #All inventary

        list=Data_base().get_inventary()

        #add al values to list

        for x in list:
            products_list.append(x[1])

        #sort list

        products_list.sort()
        
        #clean the text

        self.products_list.delete(0, END)

        #add match elements in to a list, if its is empty, add all elements

        for item in products_list:
            if search.lower() in item.lower():
                self.products_list.insert(END, item)

class Confirm_sell:
    def __init__(self,list,cost):

        #start the variables

        self.list=list
        self.cost=cost

        self.cost_var=StringVar()
        
        #create a mini windows

        self.root=Tk()
        self.root.geometry("250x130")
        self.root.resizable(height=0,width=0)
        self.root.title("Pago")

        self.main_frame=Frame(self.root)
        self.main_frame.pack()

        #i call the metod to create the work space

        self.widgets()

    def widgets(self):

        #Interface

        Label(self.main_frame,text="Costo total:").pack()
        self.total_cost_entry=Entry(self.main_frame,textvariable=self.cost_var)
        self.total_cost_entry.insert(END,str(self.cost))
        self.total_cost_entry['state']=DISABLED
        self.total_cost_entry.pack()
        Label(self.main_frame,text="Pago:").pack()
        self.pay_entry=Entry(self.main_frame)
        self.pay_entry.insert(END,str(self.cost))
        self.pay_entry.pack()
        Button(self.main_frame,text="Aceptar",command=self.cash_back_calculator).pack(pady=10)

    def cash_back_calculator(self):

        #send a message with the cashback calculed, if the joined value is empty automatically is seted to total value

        messagebox.showinfo("VUELTO", "El vuelto es de: ${}.".format(int(self.pay_entry.get())-int(self.cost)))
        Data_base().sell(self.list,self.cost)

        #destroy itself

        self.root.destroy()

class Data_base:
    def __init__(self):

        #Connect or create data base

        conection=sqlite3.connect("database/DB")
        cursor = conection.cursor()
        try:
            #If dont exist the tables its created

            cursor.execute(
                '''
                CREATE TABLE INVENTARY(
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
        conection=sqlite3.connect("database/DB")
        cursor = conection.cursor()
        try:
            cursor.execute(
                '''
                CREATE TABLE SELLS(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                PRODUCTO VARCHAN(100) NOT NULL,
                CANTIDAD INT NOT NULL,
                GANANCIA INT NOT NULL,
                FECHA VARCHAN(100) NOT NULL)
                '''
            )
            conection.commit()
            conection.close()
        except:
            conection.close()
        self.inventary=self.get_inventary()
        self.product_data=[]
        for x in self.inventary:
            self.product_data.append(x[1])

    def sell(self,list,cost):
        conection=sqlite3.connect("database/DB")
        cursor = conection.cursor()
        for x in list:
            try:

                #Update selled items

                quantity = cursor.execute("SELECT CANTIDAD FROM INVENTARY WHERE PRODUCTO='{}'".format(x)).fetchall()[0][0]
                self.cursor=cursor.execute("UPDATE INVENTARY SET CANTIDAD='{}' WHERE PRODUCTO = '{}'".format(quantity-int(list[x]),x))
                conection.commit()
                self.cursor=cursor.execute("INSERT INTO SELLS VALUES(NULL,'{}','{}','{}','{}')".format(x,list[x],cost,datetime.now()))
                conection.commit()
                conection.close()
            except Exception as e:
                conection.close()
                messagebox.showerror("ERROR",e)

    def get_inventary(self):
        conection=sqlite3.connect("database/DB")
        cursor = conection.cursor()

        #create a list with the elements of the inventary table
        
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

        #Obtain all data about at one product

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

    def set_data(self,data):
        conection=sqlite3.connect("database/DB")
        cursor = conection.cursor()
        if data[0] in self.product_data:
            try:

                #if value exist its updated

                self.cursor=cursor.execute("UPDATE INVENTARY SET CANTIDAD='{}',PRECIO='{}' WHERE PRODUCTO = '{}'".format(data[1],data[2],data[0]))
                conection.commit()
                conection.close()
            except Exception as e:
                conection.close()
                messagebox.showerror("ERROR",e)
        else:
            try:

                #if item no exist this is created

                self.cursor=cursor.execute("INSERT INTO INVENTARY VALUES(NULL,'{}','{}','{}')".format(data[0],data[1],data[2]))
                conection.commit()
                conection.close()
            except Exception as e:
                conection.close()
                messagebox.showerror("ERROR",e)

    def delete_data(self,id):
        conection=sqlite3.connect("database/DB")
        cursor = conection.cursor()
        try:

            #just delete a item
            
            self.cursor=cursor.execute("DELETE FROM INVENTARY WHERE ID = '{}'".format(id))
            conection.commit()
            conection.close()

        except Exception as e:
            conection.commit()
            conection.close()
            messagebox.showerror("ERROR",e)

class Edit_inventary:
    def __init__(self):

        self.products_var=StringVar()
        self.product_quantity_var=StringVar()
        self.product_price_var=StringVar()
        self.delete_var=StringVar()

        self.root=Tk()
        self.root.geometry("500x500")
        self.root.resizable(height=0,width=0)
        self.root.title("Productos")

        self.main_frame=Frame(self.root)
        self.main_frame.place(relx=0,rely=0,relheight=1,relwidth=1)

        self.frame1=Frame(self.main_frame)
        self.frame1.pack()

        self.widgets()
        self.set_table()

    def Spacer(self,frame):
        return Label(frame,text="----------------------------------------------------------------------------------------------")
    
    def widgets(self):

        self.Spacer(self.frame1).grid(row=0,column=0,columnspan=4)
        Label(self.frame1,text="Ingresar Productos").grid(row=1,column=0,columnspan=4)
        self.Spacer(self.frame1).grid(row=2,column=0,columnspan=4)

        Label(self.frame1,text="Nombre del producto").grid(row=3,column=0)
        Label(self.frame1,text="Cantidad").grid(row=3,column=1)
        Label(self.frame1,text="Precio Unidad").grid(row=3,column=2)

        self.product_entry=Entry(self.frame1,textvariable=self.products_var)
        self.product_entry.grid(row=4,column=0,padx=5)

        self.product_quantity_entry=Entry(self.frame1,textvariable=self.product_quantity_var)
        self.product_quantity_entry.grid(row=4,column=1,padx=5)

        self.product_price_entry=Entry(self.frame1,textvariable=self.product_price_var)
        self.product_price_entry.grid(row=4,column=2,padx=5)

        Button(self.frame1,text="Ingresar",command=self.set_data).grid(row=4,column=3,padx=5)

        self.Spacer(self.frame1).grid(row=5,column=0,columnspan=4)

        Label(self.frame1,text="BASE DE DATOS").grid(row=6,column=0,columnspan=4,padx=5)

        self.Spacer(self.frame1).grid(row=7,column=0,columnspan=4)

        self.table=ttk.Treeview(self.frame1)
        self.table.grid(row=8,column=0,columnspan=4,padx=5)

        self.table['columns']=("ID","Producto","Precio U.","Cantidad")

        self.table.column('#0', width=0, stretch=NO)
        self.table.column('ID', anchor=CENTER, width=50)
        self.table.column('Producto', anchor=CENTER, width=250)
        self.table.column('Precio U.', anchor=CENTER, width=100)
        self.table.column('Cantidad', anchor=CENTER, width=80)

        self.table.heading('#0', text='', anchor=CENTER)
        self.table.heading('ID', text='ID', anchor=CENTER)
        self.table.heading('Producto', text='Producto', anchor=CENTER)
        self.table.heading('Precio U.', text='Precio U.', anchor=CENTER)
        self.table.heading('Cantidad', text='Cantidad', anchor=CENTER)

        self.table.bind('<Double-Button>', self.selected_data)

        self.Spacer(self.frame1).grid(row=9,column=0,columnspan=4)
        Label(self.frame1,text="Eliminar").grid(row=10,column=1)
        Label(self.frame1,text="ID").grid(row=11,column=0,sticky="e")
        self.delete_entry=Entry(self.frame1,text="Aceptar",textvariable=self.delete_var,width=20)
        self.delete_entry.grid(row=11,column=1)
        Button(self.frame1,text="Eliminar",command=self.delete_item).grid(row=11,column=2,sticky="w")
        self.Spacer(self.frame1).grid(row=2,column=0,columnspan=4)
    
    def delete_item(self):
        Data_base().delete_data(self.delete_entry.get())
        self.delete_entry.delete(0,END)
        self.product_quantity_entry.delete(0, END)
        self.product_price_entry.delete(0, END)
        self.product_entry.delete(0, END)
        self.set_table()

    def selected_data(self,*args):
        data=self.table.item(self.table.selection()[0])['values']
        self.product_entry.delete(0,END)
        self.product_quantity_entry.delete(0,END)
        self.product_price_entry.delete(0,END)
        self.delete_entry.delete(0,END)
        self.product_entry.insert(0,data[1])
        self.product_quantity_entry.insert(0,data[3])
        self.product_price_entry.insert(0,data[2])
        self.delete_entry.insert(0,data[0])

    def set_data(self):
        Data_base().set_data((self.product_entry.get(),self.product_quantity_entry.get(),self.product_price_entry.get()))
        self.product_quantity_entry.delete(0, END)
        self.product_price_entry.delete(0, END)
        self.product_entry.delete(0, END)
        self.delete_entry.delete(0,END)
        self.set_table()

    def set_table(self):
        products=Data_base().get_inventary()
        x=self.table.get_children()
        for item in x:
            self.table.delete(item)
        for x in products:
            self.table.insert("",0,values=(x[0],x[1],x[3],x[2]))

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

    #i create 2 adittionals font types to my project

    font_title=Font(size=20)
    font_big=Font(size=10)

    #I started the de database

    Data_base()

    #app starts

    Aplication(master=root)
    
    #its necesary to maintance the aplication detecting data

    root.mainloop()
    