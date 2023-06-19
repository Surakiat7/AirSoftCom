from os import name
from flask import Flask, render_template, request, redirect, url_for, session, send_file
import re
import pymysql
from pymysql import cursors
import generate


app = Flask(__name__)
app.secret_key = 'qwertyuiop[]1=2-30495867'

def getConnection ():
    return pymysql.connect(
        host = 'localhost',
        db = 'project',
        user = 'root',
        password = '',
        charset = 'utf8',
        cursorclass = pymysql.cursors.DictCursor
		)

def show_name():
	connection = getConnection()
	sql = "SELECT name FROM accounts"
	cursor = connection.cursor()
	cursor.execute(sql)
	acs = cursor.fetchall()
	return acs

def orders():
	connection = getConnection()
	sql = "SELECT order_details.order_name, orders.name, orders.systemin FROM orders INNER JOIN order_details ON orders.order_id=order_details.repair_id"
	cursor = connection.cursor()
	cursor.execute(sql)
	ord = cursor.fetchall()
	return ord

def order_details():
	connection = getConnection()
	sql = "SELECT * FROM order_details"
	cursor = connection.cursor()
	cursor.execute(sql)
	det = cursor.fetchall()
	return det 

def order_x():
	connection = getConnection()
	sql = "SELECT order_details.status, orders.order_name, orders.detail, orders.order_id, order_details.repair_id, orders.price  FROM order_details, orders WHERE orders.order_id = order_details.repair_id GROUP BY orders.order_id Order by orders.order_id"
	cursor = connection.cursor()
	cursor.execute(sql)
	det = cursor.fetchall()
	return det

def total():
    connection = getConnection()
    sql = "SELECT COUNT(repair_id) AS Total FROM order_details"
    cursor = connection.cursor()
    cursor.execute(sql)
    tot = cursor.fetchall()
    return tot


@app.route('/')
def repair():
   return render_template('repair.html')

@app.route('/report')
def report():
    acs = show_name()
    return render_template('report.html', acs = acs)

@app.route('/show')
def show():
	ord = orders()
	return render_template('show.html', ord=ord)

@app.route('/pythonlogin/edit', methods=['POST', 'GET'])
def edit():
   order_id = request.form['order_id']
   price = request.form['price']
   name = request.form['name']
   ids = request.form['ids']
   detail = request.form['detail']
   return render_template('edit.html',order_id= order_id, price=price, name=name, ids=ids, detail=detail)

@app.route('/editprofile', methods=['POST', 'GET'])
def editprofile():
   name = request.form['name']
   ids = request.form['ids']
   email = request.form['email']
   address = request.form['address']
   phone = request.form['phone']
   return render_template('editprofile.html', name= name, ids=ids, email=email, address=address, phone=phone)

@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['account_id']
            session['username'] = account['username']
            session['name'] = account['name']
            session['email'] = account['email']
            session['address'] = account['address']
            session['phone'] = account['phone']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg=msg)

@app.route('/pythonlogin/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('repair'))

@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'address' in request.form and 'phone' in request.form and 'gender' in request.form:
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        address = request.form['address']
        phone = request.form['phone']
        gender = request.form['gender']
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            connection = getConnection()
            cursor = connection.cursor()
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)', (name,username, password, email, address, phone, gender))
            connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/pythonlogin/home')
def home():
    acs = show_name()
    n = session['name']
    detd = order_x()
    de = order_details()
    tot = total()
    if 'loggedin' in session:
        return render_template('home.html', name=session['name'], ids=session['id'], email=session['email'], address=session['address'], phone=session['phone'],detd=detd,acs=acs,n=n,de=de,tot=tot)   
    return redirect(url_for('login'))

@app.route('/pythonlogin/profile')
def profile():
    if 'loggedin' in session:
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))

@app.route('/insertdb',methods = ['POST', 'GET'])
def insertdb():
    name = request.form['name']
    order_name = request.form['order_name']
    detail = request.form['detail']
    connection = getConnection()
    sql1 = "INSERT INTO orders(name, order_name, detail, price, systemin) VALUES('%s', '%s', '%s', '0','รับเข้าระบบแล้ว')" % (name, order_name, detail)
    sql2 = "INSERT INTO order_details(order_name, detail, status, price) VALUES('%s', '%s','ยังไม่เสร็จ', '0')" % (order_name, detail)
    sql3 = "INSERT INTO repair(price) VALUES('0')"
    cursor = connection.cursor()
    cursor.execute(sql1)
    cursor.execute(sql2)
    cursor.execute(sql3)
    connection.commit()
    return show()

@app.route('/searchname', methods=['POST', 'GET'])
def searchname():
	search = request.form['search']
	connection = getConnection()
	cursor = connection.cursor()
	sql = f"SELECT o.order_name, o.name, t.detail, t.status, o.price, o.repair_name, o.order_id FROM orders as o, order_details as t WHERE o.name LIKE '{search}' AND o.order_id=t.repair_id GROUP BY o.order_name "
	cursor = connection.cursor()
	cursor.execute(sql)
	ord = cursor.fetchall()
	return render_template('showpay.html', ord=ord)
        
@app.route('/update/<price>/<order_id>/<name>/<ids>/<detail>',methods = ['POST', 'GET'])
def update(price, order_id, name, ids, detail):
    p = request.form['price']
    r = request.form['order_id']
    n = request.form['name']
    i = request.form['ids']
    d = request.form['detail']
    connection = getConnection()
    sql1 = f"UPDATE orders SET price = '{p}', repair_name='{n}' WHERE price = '{price}' AND order_id = '{order_id}'"
    sql2 = f"UPDATE order_details SET price = '{p}', status = 'เสร็จแล้ว', detail = '{d}' WHERE price = '{price}' AND repair_id = '{order_id}'"
    sql3 = f"UPDATE repair SET price = '{p}', accounts_id = '{i}' WHERE repair_id = '{order_id}'"
    cursor = connection.cursor()
    cursor.execute(sql1)
    cursor.execute(sql2)
    cursor.execute(sql3)
    connection.commit()
    return home()

@app.route('/update/<name>/<email>/<address>/<phone>',methods = ['POST', 'GET'])
def updateuser(name,email,address,phone):
    n = request.form['name']
    e = request.form['email']
    a = request.form['address']
    p = request.form['phone']
    connection = getConnection()
    sql = f"UPDATE accounts SET name = '{n}', email='{e}', address = '{a}', phone='{p}' WHERE name = '{name}' AND email = '{email}' AND address = '{address}' AND phone = '{phone}'"
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    return login()

@app.route('/pythonlogin/pay', methods=['POST', 'GET'])
def pay():
   template = 'InvoiceTpl.docx'
   signature = 'signature.png'
   order_id = request.form['order_id']
   invoice = {
        'invoice_no': request.form['order_id'],
        'detail' : request.form['detail'],
        'order_name' : request.form['order_name'],
        'name': request.form['name'],
        'repair_name': request.form['repair_name'],
        'total': request.form['price'],
    
    }
   print(invoice)
   document = generate.from_template(template, signature, invoice)
   document.seek(0)

   return send_file(
        document, mimetype='application/vnd.openxmlformats-'
        'officedocument.wordprocessingml.document', as_attachment=True,
        attachment_filename=f'ใบเสร็จที่ {order_id}.docx')



if __name__ == '__main__':
   app.run(debug = True)