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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user_row = conn_execute("SELECT * FROM Users WHERE user_id = ?", (user_id,)).fetchone()
    conn_close()
    if user_row: 
        return User(user_row["user_id"], user_row["username"], user_row["email"], user_row["password"])
    return None

class User(UserMixin): 
    def __init__(self, user_id, username, email, password):
        self.id = user_id
        self.username = username
        self.email = email
        self.password = password

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/dashboard")
def dashboard():
    # later you'll check if user is logged in
    return render_template("dashboard.html")

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
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/animals")
def animals():
    conn = get_db_connection()
    animals = conn.execute("SELECT * FROM Animals").fetchall()
    conn.close()
    return render_template("animals.html", animals=animals)

@app.route("/animals/new", methods=["GET", "POST"])
def new_animal():
    if request.method == "POST":
        name = request.form["name"]
        sex = request.form["sex"]
        age = request.form["age"]
        species = request.form["species"]
        intake_date = request.form["intake_date"]
        status = request.form["status"]
        adoptable = 1 if request.form.get("adoptable") else 0

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO Animals (name, species, sex, age, status, adoptable) VALUES (?, ?, ?, ?, ?, ?)",
            (name, species, sex, age, intake_date, status, adoptable)
        )
        conn.commit()
        conn.close()

        flash("New animal added!", "success")
        return redirect(url_for("animals"))

    return render_template("animals_form.html", animal=None)

@app.route("/animals/<int:animal_id>/edit", methods=["GET", "POST"])
def edit_animal(animal_id):
    conn = get_db_connection()
    animal = conn.execute("SELECT * FROM Animals WHERE animal_id = ?", (animal_id,)).fetchone()

    if not animal:
        return "Animal not found", 404

    if request.method == "POST":
        name = request.form["name"]
        species = request.form["species"]
        sex = request.form["sex"]
        age = request.form["age"]
        intake_date = request.form["intake_date"]
        status = request.form["status"]
        adoptable = 1 if "adoptable" in request.form else 0

        conn.execute("""
            UPDATE Animals
            SET name=?, species=?, sex=?, age=?, intake_date=?, status=?, adoptable=?
            WHERE animal_id=?
        """, (name, species, sex, age, intake_date, status, adoptable, animal_id))

        conn.commit()
        conn.close()
        return redirect(url_for("animals"))

    # GET → show form pre-filled
    conn.close()
    return render_template("animals_form.html", animal=animal)

@app.route("/animals/<int:animal_id>/delete", methods=["GET", "POST"])
@login_required
def delete_animal(animal_id):
    conn = get_db_connection()
    animal = conn.execute("SELECT * FROM Animals WHERE animal_id = ?", (animal_id,)).fetchone()

    if animal is None:
        conn.close()
        flash("Animal not found.", "danger")
        return redirect(url_for("animals"))

    # If POST, confirm delete
    if request.method == "POST":
        conn.execute("DELETE FROM Animals WHERE animal_id = ?", (animal_id,))
        conn.commit()
        conn.close()
        flash("Animal deleted successfully.", "success")
        return redirect(url_for("animals"))

    conn.close()
    return render_template("animals_delete.html", animal=animal)

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

if __name__ == "__main__":
    app.run(debug=True)


