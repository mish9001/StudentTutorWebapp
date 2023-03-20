from httplib2 import Credentials
import pyrebase
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from flask_mail import Mail, Message
from collections import OrderedDict
import firebase_admin
from firebase_admin import db
from firebase_admin import credentials, firestore
from firebase_admin import auth
from flask_session import Session
from firebase_admin import auth
import os
import smtplib




app=Flask(__name__)

config = {
  "apiKey": "AIzaSyBqzSqlvRFRnmD8QiTC4vpY82DzB7T2G4E",
  "authDomain": "tutordbauthenticate.firebaseapp.com",
  "databaseURL": "https://tutordbauthenticate-default-rtdb.firebaseio.com",
  "projectId": "tutordbauthenticate",
  "storageBucket": "tutordbauthenticate.appspot.com",
  "messagingSenderId": "928677714123",
  "appId": "1:928677714123:web:a7aebab830141d57a8234e",
  "measurementId": "G-0YRYZYELPH"
}

mailapp=Flask(__name__)


firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}

@app.route("/")
def login():
 
 
 return render_template("login.html")

#basic functionality to move from page to page with buttons 
@app.route("/adminlogin", methods=["POST","GET"])
def adminlogin():
 if request.method=="POST":
    return redirect(url_for("adminhome"))
 else:
   return render_template("adminlogin.html")
 
  
@app.route("/adminhome" ,methods=["GET","POST"])
def adminhome():
      #viewbankbtn= request.form["viewbankdetails"]
     
          
     
       return render_template("adminhome.html")    
   

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/welcome")
def welcome():
    if person["is_logged_in"] == True:
       
       
        return render_template("welcome.html", email = person["email"], name = person["name"])
       
    else:
        return redirect(url_for('login'))

@app.route("/result", methods = ["POST", "GET"])
def result():
    if request.method == "POST":        
        result = request.form           
        email = result["email"]
        password = result["pass"]
        try:
            
            user = auth.sign_in_with_email_and_password(email, password)
            
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            
            data = db.child("users").get()
            person["name"] = data.val()[person["uid"]]["name"]
            
            return redirect(url_for('welcome'))
        except:
           
            return redirect(url_for('login'))
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('login'))


@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":        
        result = request.form           
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        try:
            
            auth.create_user_with_email_and_password(email, password)
           
            user = auth.sign_in_with_email_and_password(email, password)
            
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
           
            
            data = {"name": name, "email": email}
            db.child("users").child(person["uid"]).set(data)
            adminclicked= request.form["link"]
            if adminclicked == 'link':
                
             return redirect(url_for('adminlogin'))
             
              
            return redirect(url_for('welcome'))
        except:
           
            return redirect(url_for('register'))

    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('register'))
        

@app.route("/applicationconfirm")
def applicationconfirm():
    return render_template("applicationconfirm.html")



@app.route("/application", methods = ["POST", "GET"]) 
def applicationpage():
    if request.method == "POST":
        
        
        #passing of data
        studemail = request.form["DUTemail"]  
        studfname= request.form["fname"]
        studlname=request.form["lname"]
        studNo= request.form["Snum"]
        studIDno=request.form["IDnum"]
        studcontact=request.form["Contact"]
        
        
        studbankname=request.form["bank_name"]
        studbranchcode=request.form["branch_code"]
        studaccnumber=request.form["account_number"]
        studworkexp=request.form["workexp"]
        studmotivation=request.form["Motivation"]
        
        #CV File upload
        studCV=request.files["CV"]
        filename=studCV.filename
        
        #banking details
        studtaxno=request.form["tax_number"]
        studaccholder=request.form["account_holder"]
        
        
        
        
        #studfile= request.files["file"] 
        
        studentapplication={"email":studemail,"First Name":studfname,"Last Name":studlname,"Student Number":studNo, "ID Number":studIDno, "Contact Number":studcontact,"Work Experience":studworkexp,"Motivation":studmotivation,"cv":filename}
        StudentBankDetails={"Bank Name":studbankname, "Branch Code":studbranchcode, "Acount Number":studaccnumber, "Tax Number":studtaxno, "Account Holder Name":studaccholder}
        studCV.save(os.path.join(app.root_path, 'static',filename))
        
        db.child("Financial Data").child(person["uid"]).set(StudentBankDetails)
        db.child("Tutors").child(person["uid"]).set(studentapplication)
  
     
        return redirect(url_for("applicationconfirm")) 
 
    else:
     return render_template("tutapplication.html")   
   
   
   
@app.route('/finance')
def finance():
 financedisp=db.child("Financial Data").get()
 
 orderedFinance= financedisp.val()

 return render_template('financaldata.html', orderedFinance=orderedFinance)   
    
    
    
   
 # View to display table of applicants   
@app.route('/table')
def table():
    
    
  disp=db.child("Tutors").get()
  files=db.child("Tutors").child("cv").get().val()      
        
  print(disp.val())
    
  ordered_dict = disp.val()

  return render_template('table.html', ordered_dict=ordered_dict,files=files)


#password reset being used is coded below 
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        try:
            auth.send_password_reset_email(email)
            flash("A password reset link has been sent to your email.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash("Failed to send password reset email. Please try again later.", "error")
            print(e)
            return redirect(url_for("forgot_password"))
    else:
        return render_template("forgot_password.html")
    

if __name__ == "__main__":
    app.run() 
    
    
    
    
    
    ######### test to see if it writes to table with Tutor child 
 #      studentdata = {"Age": 24, "Name": "Fred", "Tutor": True}
        #to create data
  #      db.child("Tutors").child(person["uid"]).set(studentdata)