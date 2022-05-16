#importing all Modules
import socket
import threading
import cx_Oracle

#Network side socket creation

connectionlimit = 10
port = 12345

#Creating Socket

try:
    netsoc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print("Socket created successfully")
except socket.error as msg:
    print(msg)

#Binding Socket

try:
    netsoc.bind(('',port))
    print("socket is binded to port no " + str(port))
except socket.error as msg:
    print(msg)

#listening to incoming connections

netsoc.listen(connectionlimit)

#Auction details

productname = None
productid = None
startprice = None
finalprice = None
description = None
buyerid = None
sellerid = None

#Seller Page
def Seller_Page(connection,address,username):
    global sellerid
    sellerid = username
    connection.send("Upload product details".encode("UTF-8"))
    connection.send("Product name : r".encode("UTF-8"))
    global productname
    productname = connection.recv(1024).decode("UTF-8")
    connection.send("Starting Price : r".encode("UTF-8"))
    global startprice
    startprice = int(connection.recv(1024).decode("UTF-8"))
    global finalprice
    finalprice = startprice
    connection.send("Description : r".encode("UTF-8"))
    global description
    description  = connection.recv(1024).decode("UTF-8")
    try:
        dbmsconnect = cx_Oracle.connect('SYSTEM/vishnu123@localhost:1521/xe')
        dbmscursor = dbmsconnect.cursor()
    except cx_Oracle.Error as msg:
        print(msg)
    dbmscursor.execute("select max(productid) from products") 
    dbmsconnect.commit()
    global productid   
    for row in dbmscursor.fetchone():
        productid = row
    productid = int(productid) + 1
    send = "Auction starts now with ID : " + str(productid)
    connection.send(send.encode("UTF-8"))
    Stop_Auction(connection,address)
    dbmscursor.close()
    dbmsconnect.close()

#stop_auction
def Stop_Auction(connection,address):
    connection.send("To close the Auction(Press 1) r".encode("UTF-8"))
    end = connection.recv(1024).decode("UTF-8")
    if int(end) == 1:
        global productname
        global productid 
        global startprice
        global finalprice
        global description 
        global buyerid 
        global sellerid 
        try:
            dbmsconnect = cx_Oracle.connect('SYSTEM/vishnu123@localhost:1521/xe')
            dbmscursor = dbmsconnect.cursor()
        except cx_Oracle.Error as msg:
            print(msg)
        try:
            send = "Your product got sold at Rs." + str(finalprice) + "to" + str(buyerid) + " "
            connection.send(send.encode("UTF-8"))
            insert = "insert into products values('" + str(productname) + "'," + str(productid) + "," + str(startprice) + "," + str(finalprice) + ",'" + str(description) + "','" + str(buyerid) + "','" + str(sellerid) + "')"
            dbmscursor.execute(insert) 
            dbmsconnect.commit()
            productname = None
            productid = None
            startprice = None
            finalprice = None
            description = None
            buyerid = None
            sellerid = None
        except cx_Oracle.DatabaseError:
            print("Database Error")
        print("connection closed : " + str(address))
        connection.close()

#Buyer Page
def Buyer_page(connection,address,username):
    global productname
    global productid 
    global startprice
    global finalprice
    global description 
    global buyerid 
    global sellerid
    connection.send("Enter Auction ID : r".encode("UTF-8"))
    auctionid = int(connection.recv(1024).decode("UTF-8"))
    while(auctionid != productid):
        connection.send("Invalid Auction ID".encode("UTF-8"))
        connection.send("Enter Auction ID : r".encode("UTF-8"))
        auctionid = connection.recv(1024).decode("UTF-8")
    name = "Product Name : " + str(productname) + " "
    connection.send(name.encode("UTF-8"))
    stpr = "Starting Price : " + str(startprice) + "\n"
    connection.send(stpr.encode("UTF-8"))
    desc = "Description : " + str(description) + "\n"
    connection.send(desc.encode("UTF-8"))
    bidding = None
    connection.send("Note : Type exit to quit auction \n".encode("UTF-8"))
    while bidding != "exit":
        cpr = "Current Price : " + str(finalprice) + "\n"
        connection.send(cpr.encode("UTF-8"))
        connection.send("Enter Amount : r".encode("UTF-8"))
        bidding = connection.recv(1024).decode("UTF-8")
        if bidding == "exit":
            break
        if int(bidding) > finalprice:
            finalprice = int(bidding)
            buyerid = username
    connection.send("Thankyou for you participation".encode("UTF-8"))
    connection.close()

#Seller Login
def seller_login(connection,address):
    option = 0
    while option != 1:
        connection.send("Seller Login".encode("UTF-8"))
        connection.send("Username : r".encode("UTF-8"))
        username = connection.recv(1024).decode("UTF-8")
        connection.send("Password : r".encode("UTF-8"))
        password = connection.recv(1024).decode("UTF-8")
        try:
            dbmsconnect = cx_Oracle.connect('SYSTEM/vishnu123@localhost:1521/xe')
            dbmscursor = dbmsconnect.cursor()
        except cx_Oracle.Error as msg:
            print(msg)
        dbmscursor.execute("select sellerid,password from selling where sellerid = '"  + username + "' and password = '" + password + "'")
        dbmsconnect.commit()
        result = dbmscursor.fetchone()
        if result == None:
            connection.send("Login or Password is invalid".encode("UTF-8"))
        else:
            connection.send("Login Successfull".encode("UTF-8"))
            dbmscursor.close()
            dbmsconnect.close()
            option = 1
            Seller_Page(connection,address,username)
        if option==0:
            dbmscursor.close()
            dbmsconnect.close()

#Seller Register
def seller_Register(connection,address):
    option = 0
    while option != 1:
        connection.send("Seller Register ".encode("UTF-8"))
        connection.send("Enter your name : r".encode("UTF-8"))
        name = connection.recv(1024).decode("UTF-8")
        connection.send("Enter Username : r".encode("UTF-8"))
        username = connection.recv(1024).decode("UTF-8")
        connection.send("Enter password : r".encode("UTF-8"))
        password = connection.recv(1024).decode("UTF-8")
        try:
            dbmsconnect = cx_Oracle.connect('SYSTEM/vishnu123@localhost:1521/xe')
            dbmscursor = dbmsconnect.cursor()
        except cx_Oracle.Error as msg:
            print(msg)
        try:
            dbmscursor.execute("insert into selling values('" + name + "','" + username + "','" + password + "')")
            dbmsconnect.commit()
            connection.send("Accound Created".encode("UTF-8"))
            option = 1
            dbmscursor.close()
            dbmsconnect.close()
            Seller_Page(connection,address,username)
        except cx_Oracle.DatabaseError:
            connection.send("Username already exists".encode("UTF-8"))
        if option==0:
            dbmscursor.close()
            dbmsconnect.close()

#Buyer Login
def buyer_login(connection,address):
    option = 0
    while option != 1:
        connection.send("Buyer Login".encode("UTF-8"))
        connection.send("Username : r".encode("UTF-8"))
        username = connection.recv(1024).decode("UTF-8")
        connection.send("Password : r".encode("UTF-8"))
        password = connection.recv(1024).decode("UTF-8")
        try:
            dbmsconnect = cx_Oracle.connect('SYSTEM/vishnu123@localhost:1521/xe')
            dbmscursor = dbmsconnect.cursor()
        except cx_Oracle.Error as msg:
            print(msg)
        dbmscursor.execute("select buyerid,password from buying where buyerid = '"  + username + "' and password = '" + password + "'")
        dbmsconnect.commit()
        result = dbmscursor.fetchone()
        if result == None:
            connection.send("Login or Password is invalid".encode("UTF-8"))
        else:
            connection.send("Login Successfull".encode("UTF-8"))
            dbmscursor.close()
            dbmsconnect.close()
            option = 1
            Buyer_page(connection,address,username)
        if option==0:
            dbmscursor.close()
            dbmsconnect.close()

#Buyer Register
def buyer_Register(connection,address):
    option = 0
    while option != 1:
        connection.send("Buyer Register ".encode("UTF-8"))
        connection.send("Enter your name : r".encode("UTF-8"))
        name = connection.recv(1024).decode("UTF-8")
        connection.send("Enter Username : r".encode("UTF-8"))
        username = connection.recv(1024).decode("UTF-8")
        connection.send("Enter password : r".encode("UTF-8"))
        password = connection.recv(1024).decode("UTF-8")
        try:
            dbmsconnect = cx_Oracle.connect('SYSTEM/vishnu123@localhost:1521/xe')
            dbmscursor = dbmsconnect.cursor()
        except cx_Oracle.Error as msg:
            print(msg)
        try:
            dbmscursor.execute("insert into buying values('" + name + "','" + username + "','" + password + "')")
            dbmsconnect.commit()
            connection.send("Accound Created".encode("UTF-8"))
            option = 1
            dbmscursor.close()
            dbmsconnect.close()
            Buyer_page(connection,address,username)
        except cx_Oracle.DatabaseError:
            connection.send("Username already exists".encode("UTF-8"))
        if option==0:
            dbmscursor.close()
            dbmsconnect.close()

while True:
    connection,address = netsoc.accept()
    print("Got connection from address " + str(address))
    connection.send("Buyer(Press 1) or Seller(Press 2) : r".encode("UTF-8"))
    bors = connection.recv(1024).decode("UTF-8")
    connection.send("Login(Press 1) or Register(Press 2) : r".encode("UTF-8"))
    lorr = connection.recv(1024).decode("UTF-8")
    if int(bors) == 1 and int(lorr) == 1:
        thread1 = threading.Thread(target=buyer_login, args=(connection,address))
        thread1.start()
    elif int(bors) == 1 and int(lorr) == 2:
        thread1 = threading.Thread(target=buyer_Register, args=(connection,address))
        thread1.start()
    elif int(bors) == 2 and int(lorr) == 1:
        thread1 = threading.Thread(target=seller_login, args=(connection,address))
        thread1.start()
    else:
        thread1 = threading.Thread(target=seller_Register, args=(connection,address))
        thread1.start()

#Server Shutdown
netsoc.close()