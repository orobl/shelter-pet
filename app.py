from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin 
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "your_secret_key_here" #update later

# helper function to connect with the database
def get_db_connection():
    conn = sqlite3.connect("shelter_database.db")
    conn.row_factory = sqlite3.Row
    return conn

def load_user(user_id):
    conn = get_db_connection()
    user_row = conn_execute("SELECT * FROM Users WHERE user_id = ?", (user_id,)).fetchone()
    conn_close()
    if user_row: 
        return User(user_row["user_id"], user_row["username"], user_row["email"], user_row["password"])
    return None


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# fetch all of the animal name and species records from the Animals table
@app.route("/animals")
def animals():
    conn = get_db_connection()
    animals = conn.execute("SELECT * FROM Animals").fetchall()
    conn.close()
    return render_template("animals.html", animals=animals)
@app.route("/")
def home():
    return render_template("animals.html", animals=get_db_connection().execute("SELECT * FROM Animals").fetchall())

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        user_row = conn.execute("SELECT * FROM Users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user_row and check_password_hash(user_row["password"], password):
            user = User(user_row["user_id"], user_row["username"], user_row["email"], user_row["password"])
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("animals"))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_pw = generate_password_hash(password, method="sha256")

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO Users (username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed_pw)
            )
            conn.commit()
            conn.close()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            conn.close()
            flash("Username or email already exists.", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")

@app.route("/analytics", methods=["GET", "POST"])
def analytics():
    # For now, a simple placeholder
    return "Analytics page works!"

@app.route("/animals/new", methods=["GET", "POST"])
def new_animal():
    # For now, placeholder
    return "New Animal form goes here"

if __name__ == "__main__":
    app.run(debug=True)


