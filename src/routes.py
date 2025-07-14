from flask import Blueprint, render_template, request, redirect, session, flash
from .utils import dbConnection, login_required
import sqlite3
import jsonify

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
    try:
        conn = dbConnection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM posts ORDER BY id DESC")
        posts = cur.fetchall()
        conn.close()

        # Optionally format posts into dicts if you're using column access in Jinja
        posts_data = [
            {
                "id": row[0],
                "title": row[1],
                "userid": row[2],
                "username": row[3],
                "body": row[4],
                "img": row[5],
                "upvotes": row[6],
                "downvotes": row[7],
                "tags": row[8],
            }
            for row in posts
        ]

        return render_template("pages/feed.html", posts=posts_data)

    except Exception as e:
        print("Error loading feed:", e)
        return render_template("pages/feed.html", posts=[])


@routes.route("/vote", methods=["POST"])
def vote():
    data = request.get_json()
    post_id = data["post_id"]
    vote_type = data["vote_type"]  # 'up' or 'down'
    action = data["action"]        # 'add' or 'remove'

    column = "upvotes" if vote_type == "up" else "downvotes"

    db = dbConnection()
    cursor = db.cursor()

    if action == "add":
        cursor.execute(f"UPDATE posts SET {column} = {column} + 1 WHERE id = ?", (post_id,))
    elif action == "remove":
        cursor.execute(f"""
            UPDATE posts
            SET {column} = CASE
                WHEN {column} > 0 THEN {column} - 1
                ELSE 0
            END
            WHERE id = ?
        """, (post_id,))

    db.commit()
    return jsonify(success=True)



@routes.route("/post", methods=["GET", "POST"])
@login_required
def post():
    if request.method == "POST":
        # Extract form data
        title = request.form.get("title")
        tags = request.form.get("tags")
        body = request.form.get("body")
        
        # User session data
        userid = session.get("roll")
        username = session.get("username")

        if not userid or not username:
            flash("You must be logged in to post.")
            return redirect("/login")

        try:
            conn = dbConnection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO posts (title, userid, username, body, img, upvotes, downvotes, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, userid, username, body, None, 0, 0, tags))
            conn.commit()
            conn.close()
            flash("Post submitted successfully!")
            return redirect("/feed")  # or wherever your posts are displayed
        except Exception as e:
            print("Error posting:", e)
            flash("Something went wrong while posting.")
            return redirect("/post")
    
    else:
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
    user_id = session["roll"]

    db = dbConnection()
    cursor = db.cursor()
    cursor.execute("""
        SELECT username, name, email, phone, branch, grad_year
        FROM users WHERE roll = ?
    """, (user_id,))

    row = cursor.fetchone()

    if not row:
        return redirect("/login")

    user = {
        "username": row[0],
        "name": row[1],
        "email": row[2],
        "phone": row[3],
        "branch": row[4],
        "grad_year": row[5]
    }

    return render_template("pages/profile.html", user=user)

