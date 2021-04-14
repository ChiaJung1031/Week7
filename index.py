from flask import Flask,url_for,redirect,session,jsonify
from flask import render_template
from flask import request
import mysql.connector
from mysql.connector import errorcode
import time , json

mydb= mysql.connector.connect(
  host="localhost",
  user="root",
  password="12345",
  database="websystem"
)
cursor=mydb.cursor()

app=Flask(__name__)
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'
app.config['JSON_AS_ASCII'] = False

@app.route("/")
def index():
  return  render_template("index.html")

@app.route("/signup", methods=["POST"])   
def signup():
   name=request.form['username']
   account=request.form['useraccount']
   password=request.form['userpassword']
   datetime=time.localtime()
   if len(name)==0 or len(account)==0 or len(password)==0:
    # session["signup"] = "申請帳號資料請填寫完整"
     return redirect(url_for('errorpage'))
   else:
      Sql= "SELECT username FROM user WHERE username= %s"
      adr=(account,)
     # print(adr)
      cursor.execute(Sql,adr)
      myresult = cursor.fetchall()
      if len(myresult) == 0:
            sql = "INSERT INTO user(name,username,password,time) VALUES(%s,%s,%s,%s)"
            val = (name,account,password,datetime)
            cursor.execute(sql,val)
            mydb.commit()
            return redirect(url_for('index'))
      else:
        #    session["signup"] = "帳號已經被註冊"
            return redirect(url_for('errorpage'))



@app.route('/error')
def errorpage():
      errmsg = request.args.get("message","帳號或密碼輸入錯誤")
      if errmsg == "帳號或密碼輸入錯誤":
         return  render_template('error.html',errmsg="帳號或密碼輸入錯誤")
      else:
         return  render_template('error.html',errmsg=errmsg)

@app.route('/signin', methods=["POST"])
def signinpage():
      account = request.form['account']   
      session['account'] = account
      print(session['account'])
      psword = request.form['password']  
      Sql= "SELECT name FROM user WHERE username= %s AND password = %s"
      adr=(account,psword)
      #print(adr)   
      cursor.execute(Sql,adr)
      myresult = cursor.fetchall()  
      if len(account) == 0 or len(psword)== 0 :
        # session["signup"] = "帳號或密碼輸入錯誤"
         return redirect(url_for('errorpage'))
      else:
         if len(myresult) == 0:
      #       session["signup"] = "帳號或密碼輸入錯誤"
             return redirect(url_for('errorpage'))
         else:
            result =  myresult[0][0] 
            session['loginout'] = "已登入"
            session["username"] = result
            return redirect(url_for('memberpage'))

@app.route('/member')
def memberpage():
   if session['loginout'] == "已登入":
    return render_template('member.html',message = session["username"] )
   else:
    return redirect(url_for('index'))
     
@app.route('/signout')
def signoutpage():
     session.clear()
     session['loginout'] = "未登入"
     return redirect(url_for('index'))
     


@app.route('/api/users',methods=['GET', 'POST'])
def apiuser():
   if request.method == "GET" :
      #取得帳號
      account = request.args.get("username","")
      Sql= "SELECT id,name,username FROM user WHERE username= %s "
      adr=(account,)
      cursor.execute(Sql,adr)
      myresult = cursor.fetchall()  
      #print(myresult)
      if len(myresult) == 1: 
         for row in myresult:
            id = row[0]
            name = row[1]
            username = row[2]
            pydata = {"data":{"id":id,"name":name,"username":username}}
            new = json.dumps(pydata,ensure_ascii=False).encode('utf8')
          # print(new)
         return new
      else:
            SS = None  #use a variable that contains None will output null, whatever vairable you named ~
            data={"data":SS}
            nulldata =  json.dumps(data)
            return nulldata
   if request.method == "POST":
      data = request.json
      changename = data['name']  #要更改的姓名
      print(changename)
      account = session['account'] #帳號
      sql = "update user set name = %s where username = %s "
      adr=(changename,account)
      cursor.execute(sql,adr)
      mydb.commit()
      print(cursor.rowcount, "record(s) affected")
      newsql = "select name from user where username = %s"
      newadr=(account,)
      cursor.execute(newsql,newadr)
      myresult = cursor.fetchall()  
      if len(myresult) == 1:
         for i in myresult:
            aftername = i[0]
            print(aftername)
            if aftername == changename:
               data={"ok":True}
               backdata =  json.dumps(data)
               return backdata
      else:
          data={"error":True}
          backdata =  json.dumps(data)
          return backdata


app.run(port=3000)