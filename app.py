from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# helper function to connect with the database
def get_db_connection():
    conn = sqlite3.connect("shelter_database.db")
    conn.row_factory = sqlite3.Row
    return conn

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
    # For now, a simple placeholder
    return "Login page works!"

@app.route("/logout", methods=["GET", "POST"])
def logout():
    # For now, a simple placeholder
    return "logout page works!"

@app.route("/register", methods=["GET", "POST"])
def register():
    # For now, a simple placeholder
    return "Register page works!"

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


