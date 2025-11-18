from flask import Flask, redirect, url_for
import sqlite3

app = Flask(__name__)

# helper function to connect with the database
def get_db_connection():
    conn = sqlite3.connect("shelter_database.db")
    conn.row_factory = sqlite3.Row
    return conn

# Redirect root URL to /animals
@app.route("/")
def home():
    return redirect(url_for('animals'))

# fetch all of the animal name and species records from the Animals table
@app.route("/animals")
def animals():
    conn = get_db_connection()
    animals = conn.execute("SELECT * FROM Animals").fetchall()
    conn.close()
    return "<br>".join([f"{a['name']} ({a['species']})" for a in animals])

if __name__ == "__main__":
    app.run(debug=True)


