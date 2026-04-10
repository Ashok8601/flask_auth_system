from distutils.command.config import config

from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
from datetime import timedelta
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
   create_refresh_token
)
app = Flask(__name__)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)
app.config["JWT_SECRET_KEY"] ="ashokkumaryadav"
jwt = JWTManager(app)


# Home Route
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Welcome to the home page"
    }), 200


# Signup Route
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Please enter some data"
        }), 400

    name = data.get("name")
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # Validation
    if not name or not username or not email or not password:
        return jsonify({
            "message": "All fields are required"
        }), 400

    # Hash Password
    hash_pass = generate_password_hash(password)

    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO user(name, email, username, password) VALUES (?, ?, ?, ?)",
            (name, email, username, hash_pass)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "message": "User created successfully"
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "message": "User already exists"
        }), 400

    except Exception as e:
        return jsonify({
            "message": str(e)
        }), 500


# Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Please enter some data"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400

    conn = get_db()
    cur = conn.cursor()

    user = cur.execute(
        "SELECT * FROM user WHERE email = ?",
        (email,)
    ).fetchone()

    conn.close()

    if user is None:
        return jsonify({
            "message": "User does not exist"
        }), 404

    if not check_password_hash(user['password'], password):
        return jsonify({
            "message": "Wrong credentials"
        }), 401
    access_token = create_access_token(identity=user['id'])
    refresh_token = create_refresh_token(identity=user['id'])
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200
@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()

    new_access_token = create_access_token(identity=current_user)

    return jsonify({
        "access_token": new_access_token
    }), 200

@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    conn = get_db()
    cur = conn.cursor()
    users= cur.execute("SELECT * FROM user WHERE id=?",(current_user,)).fetchone()
    conn.close()
    return jsonify({"user name":users['name'],
                    "email":users["email"],
                    "username":users["username"]}), 200
if __name__ == '__main__':
    app.run(debug=True)