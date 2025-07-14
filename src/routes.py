from flask import Blueprint, render_template, request, redirect, session
from .utils import dbConnection, login_required
import sqlite3

routes = Blueprint('routes', __name__)


@routes.route('/')
def index():
    return render_template("index.html")



@routes.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        roll = request.form.get("roll")
        username = request.form.get("username")
        password = request.form.get("password")
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        branch = request.form.get("branch")
        grad_year = request.form.get("grad-year")

        conn = dbConnection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (roll, username, password, name, email, phone, branch, grad_year, section)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (roll, username, password, name, email, phone, branch, grad_year, None))

            conn.commit()
        except sqlite3.IntegrityError:
            return "User already exists or invalid data", 400
        finally:
            conn.close()

        return redirect("/")
    else:
        return render_template("register.html")
    


@routes.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = dbConnection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["username"] = username
            session["roll"] = user[0]
            return redirect("/feed")
        else:
            return "Invalid username or password", 401
    else:
        return render_template("login.html")
    


@routes.route('/logout')
def logout():
    session.clear()
    return redirect("/")



@routes.route("/feed")
@login_required
def feed():
    if "username" not in session:
        return redirect("/login")
    return render_template("pages/feed.html")



@routes.route("/post")
@login_required
def post():
    if "username" not in session:
        return redirect("/login")
    return render_template("pages/post.html")



@routes.route("/placements")
@login_required
def placements():
    if "username" not in session:
        return redirect("/login")
    return render_template("pages/placements.html")



@routes.route("/profile")
@login_required
def profile():
    if "username" not in session:
        return redirect("/login")
    return render_template("pages/profile.html")