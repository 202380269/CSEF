from flask import Flask, jsonify, request, Response
from flask_mysqldb import MySQL
import jwt
import dicttoxml
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)

# ================= CONFIG =================
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'  
app.config['MYSQL_DB'] = 'sm_mall'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = 'finals-secret-key'

mysql = MySQL(app)

DEMO_USER = {'username': 'admin', 'password': 'password'}

# ================= JWT =================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

# ================= FORMAT =================
def format_response(data, status=200):
    fmt = request.args.get('format', 'json')
    if fmt == 'xml':
        xml = dicttoxml.dicttoxml(data, custom_root='response', attr_type=False)
        return Response(xml, mimetype='application/xml', status=status)
    return jsonify(data), status

# ================= LOGIN =================
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data'}), 400

    if data['username'] == DEMO_USER['username'] and data['password'] == DEMO_USER['password']:
        token = jwt.encode({
            'user': 'admin',
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})

    return jsonify({'error': 'Invalid credentials'}), 401

# ================= CUSTOMERS =================
@app.route('/customers', methods=['GET'])
@token_required
def get_customers():
    cur = mysql.connection.cursor()
    q = request.args.get('q')
    if q:
        cur.execute("SELECT * FROM customers WHERE first_name LIKE %s OR last_name LIKE %s",
                    (f"%{q}%", f"%{q}%"))
    else:
        cur.execute("SELECT * FROM customers")
    data = cur.fetchall()
    cur.close()
    return format_response({'customers': data})

@app.route('/customers', methods=['POST'])
@token_required
def create_customer():
    data = request.get_json()
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO customers (customer_id, first_name, last_name, store_id) VALUES (%s,%s,%s,%s)",
        (None, data['first_name'], data['last_name'], data['store_id'])
    )
    mysql.connection.commit()
    cur.close()
    return format_response({'message': 'Customer created'}, 201)

@app.route('/customers/<int:id>', methods=['PUT'])
@token_required
def update_customer(id):
    data = request.get_json()
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE customers SET first_name=%s,last_name=%s,store_id=%s WHERE customer_id=%s",
        (data['first_name'], data['last_name'], data['store_id'], id)
    )
    mysql.connection.commit()
    cur.close()
    return format_response({'message': 'Customer updated'})

@app.route('/customers/<int:id>', methods=['DELETE'])
@token_required
def delete_customer(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM customers WHERE customer_id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    return format_response({'message': 'Customer deleted'})

# ================= STORES =================
@app.route('/stores', methods=['GET'])
@token_required
def get_stores():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM stores")
    data = cur.fetchall()
    cur.close()
    return format_response({'stores': data})

# ================= PRODUCTS =================
@app.route('/products', methods=['GET'])
@token_required
def get_products():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products")
    data = cur.fetchall()
    cur.close()
    return format_response({'products': data})

# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)
