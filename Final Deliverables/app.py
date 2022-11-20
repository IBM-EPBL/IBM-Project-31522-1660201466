from flask import Flask, render_template,request,redirect,session 
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import random
import ibm_db
import re

hostname = ""
uid = ""
pwd = ""
database = ""
port = ""

app = Flask(__name__)

app.secret_key = "Madan"

conn = ibm_db.connect(f"DATABASE={database};HOSTNAME={hostname};PORT={port};SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID={uid};PWD={pwd};", "", "")

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/dash")
def dash():
    return render_template("dash.html")

@app.route("/signin")
def signin():
    return render_template("signin.html")

@app.route("/signinvalid",methods = ["POST","GET"])
def signinv():
    if request.method == "POST":
        global username
        global password
        username = request.form.get("usernamel")
        password = request.form.get("passwdl")
        msgl = ""
        stringl = ""
        sqll = "SELECT * FROM REGISTER WHERE USERNAME =? AND PASSWORD =?"
        stmtl = ibm_db.prepare(conn, sqll)
        ibm_db.bind_param(stmtl,1,username)
        ibm_db.bind_param(stmtl,2,password)
        ibm_db.execute(stmtl)
        accountl = ibm_db.fetch_assoc(stmtl)
        print(accountl)

        if accountl:
            session["username"] = accountl["USERNAME"]
            session["mail"] = accountl["MAIL"]
            stringl = f"{username} login success"
            return render_template("dash.html",stringl=stringl)
        else:
            msgl = "Incorrect Username and Password"
    return render_template("signin.html",msgl=msgl)


@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/signupvalid",methods = ["POST","GET"])
def signupv():
    if request.method == "POST":
        global mail
        global user
        global passwd
        global limit
        mail = request.form.get("emailaddress")
        user = request.form.get("username")
        passwd = request.form.get("passwd")
        limit = "0"
        msg = ""
        userstatus = ""
        mailstatus = ""
        passwdstatus = ""

        sql = "SELECT * FROM REGISTER WHERE USERNAME =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,user)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)

        if account:
            msg = "Account already exists"
        elif not re.match(r'[A-Za-z0-9]+', user):
            userstatus = "Please enter valid username"
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', mail):
            mailstatus = "Please enter valid email"
        elif (passwd==""):
            passwdstatus = "Please enter valid password"
        else:
            sentotp(user,mail)
            return render_template("validate.html")
        return render_template("signup.html",mailstatus=mailstatus,userstatus=userstatus,passwdstatus=passwdstatus,msg=msg)

@app.route("/checkotp",methods = ["POST","GET"])
def checkotp():
    if request.method == "POST":
        rotp = request.form.get("otp")
        if (str(rotp)==str(sotp)):

            sql1="INSERT INTO REGISTER(USERNAME,PASSWORD,MAIL,EXPLIMIT) VALUES(?,?,?,?)"
            stmt1 = ibm_db.prepare(conn, sql1)
            
            ibm_db.bind_param(stmt1,1,user)
            ibm_db.bind_param(stmt1,2,passwd)
            ibm_db.bind_param(stmt1,3,mail)
            ibm_db.bind_param(stmt1,4,limit)
            ibm_db.execute(stmt1)

            result = "Account Created Succesfully"
            return render_template("result.html",result=result)
        else:
            status = "Please enter valid OTP"
            return render_template("validate.html",status=status)


def sentotp(user,mail):
    global sotp
    sotp = random.randint(1000,9999)
    message = Mail(
    from_email='madanmn1742@gmail.com',
    to_emails=mail,
    subject='Otp verification',
    html_content=f'Hello {user} This is OTP - {sotp}')
    sg = SendGridAPIClient("")
    response = sg.send(message)

@app.route("/add")
def add():
    return render_template("add.html")

@app.route("/addexpense",methods = ["POST","GET"])
def addexpense():
    if request.method == "POST":
        date = request.form.get("date")
        time = request.form.get("time")
        expensename = request.form.get("expensename")
        amount = request.form.get("amount")
        mode = request.form.get("mode")
        datemsg = ""
        timemsg = ""
        expnamemsg = ""
        expamntmsg = ""
        modemsg = ""
        if (date==""):
            datemsg = "Enter valid date"
        elif (time==""):
            timemsg = "Enter valid time"
        elif (expensename==""):
            expnamemsg = "Enter valid expense name"
        elif (amount=="0") or (amount==""):
            expamntmsg = "Enter amount"
        elif (mode=="Mode"):
            modemsg = "Select a mode"   
        else:
            sql2 = "INSERT INTO EXPENSES(USERNAME,DATE,TIME,EXPENSENAME,AMOUNT,MODE) VALUES(?,?,?,?,?,?)"
            stmt2 = ibm_db.prepare(conn, sql2)
            ibm_db.bind_param(stmt2,1,session["username"])
            ibm_db.bind_param(stmt2,2,date)
            ibm_db.bind_param(stmt2,3,time)
            ibm_db.bind_param(stmt2,4,expensename)
            ibm_db.bind_param(stmt2,5,amount)
            ibm_db.bind_param(stmt2,6,mode)
            ibm_db.execute(stmt2)

            return redirect("/view")

        return render_template("add.html",datemsg=datemsg,timemsg=timemsg,expnamemsg=expnamemsg,expamntmsg=expamntmsg,modemsg=modemsg)

def gettotal():
    sql4 = "SELECT * FROM EXPENSES WHERE USERNAME=?"
    stmt4 = ibm_db.prepare(conn, sql4)
    ibm_db.bind_param(stmt4,1,session["username"])
    ibm_db.execute(stmt4)
    lst3=[]
    row1 = ibm_db.fetch_tuple(stmt4)
    while(row1):
        lst3.append(row1)
        row1 = ibm_db.fetch_tuple(stmt4)
    print(lst3)
    total = 0
    for x in lst3:
        total += int(x[4])
    currentvalue()
    if (total>int(current)):
        sentalert()
    return total


@app.route("/view")
def view():
    sql3 = "SELECT * FROM EXPENSES WHERE USERNAME=?"
    stmt3 = ibm_db.prepare(conn, sql3)
    ibm_db.bind_param(stmt3,1,session["username"])
    ibm_db.execute(stmt3)
    lst2=[]
    row = ibm_db.fetch_tuple(stmt3)
    while(row):
        lst2.append(row)
        row = ibm_db.fetch_tuple(stmt3)
    print(lst2)
    vtotal = gettotal()
    return render_template("view.html",lst2=lst2,vtotal=vtotal)

def currentvalue():
    global current
    sql6 = "SELECT EXPLIMIT FROM REGISTER WHERE USERNAME=?"
    stmt6 = ibm_db.prepare(conn, sql6)
    ibm_db.bind_param(stmt6,1,session["username"])
    ibm_db.execute(stmt6)
    currentt = ibm_db.fetch_assoc(stmt6)
    current = currentt["EXPLIMIT"]

@app.route("/limit")
def limit():
    currentvalue()
    return render_template("limit.html" ,current=current)

@app.route("/addlimit", methods= ["POST","GET"])
def addlimit():
    if request.method == "POST":
        limit = request.form.get("limit")
        global limitmsg
        limitmsg = ""
        if (limit==""):
            limitmsg = "Please enter valid limit"
        else:
            sql5 = "UPDATE REGISTER SET EXPLIMIT=? WHERE USERNAME=?"
            stmt5 = ibm_db.prepare(conn, sql5)
            ibm_db.bind_param(stmt5,1,limit)
            ibm_db.bind_param(stmt5,2,session["username"])
            ibm_db.execute(stmt5)
            return redirect("/view")

        return render_template("limit.html" ,limitmsg=limitmsg,current=current)

def sentalert():
    message = Mail(
    from_email='madanmn1742@gmail.com',
    to_emails=session["mail"],
    subject='Alert',
    html_content=f'Hello {session["username"]} You crossed your expense limit')
    sg = SendGridAPIClient("")
    response = sg.send(message)

@app.route("/graph")
def graph():
    sql7 = "SELECT * FROM EXPENSES WHERE USERNAME=?"
    stmt7 = ibm_db.prepare(conn, sql7)
    ibm_db.bind_param(stmt7,1,session["username"])
    ibm_db.execute(stmt7)
    lst3=[]
    row3 = ibm_db.fetch_tuple(stmt7)
    while(row3):
        lst3.append(row3)
        row3 = ibm_db.fetch_tuple(stmt7)
    print(lst3)

    g_cash = 0
    g_online = 0
    g_debit = 0
    g_credit = 0

    for z in lst3:
        if z[5] == "cash":
            g_cash += int(z[4])
        elif z[5] == "onlinepayment":
            g_online += int(z[4])
        elif z[5] == "debitcard":
            g_debit += int(z[4])
        elif z[5] == "creditcard":
            g_credit += int(z[4])


    return render_template("graph.html",g_cash=g_cash,g_online=g_online,g_credit=g_credit,g_debit=g_debit)


@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("mail", None)
    return render_template("/index.html")    


if __name__ == "__main__":
    app.run(debug=True)

