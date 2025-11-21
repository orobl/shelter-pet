from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin 
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm
from flask_wtf.csrf import CSRFProtect
import json
from datetime import datetime, timedelta

app = Flask(__name__)

app.secret_key = "your_secret_key_here" #update later
CSRFProtect(app)

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
    user_row = conn.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
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
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

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

    return render_template("login.html", form=form)



@app.route("/animals")
@login_required
def animals():
    conn = get_db_connection()
    animals = conn.execute("SELECT * FROM Animals").fetchall()
    conn.close()
    return render_template("animals.html", animals=animals)

@app.route("/animals/new", methods=["GET", "POST"])
@login_required
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
            "INSERT INTO Animals (name, species, sex, age, intake_date, status, adoptable) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, species, sex, age, intake_date, status, adoptable)
        )
        conn.commit()
        conn.close()

        flash("New animal added!", "success")
        return redirect(url_for("animals"))

    return render_template("animals_form.html", animal=None)

@app.route("/animals/<animal_id>/edit", methods=["GET", "POST"])
@login_required
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

@app.route("/animals/<animal_id>/delete", methods=["GET", "POST"])
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
        flash("Animal deleted!", "success")
        return redirect(url_for("animals"))
    # If GET, show confirmation page
    conn.close()
    return render_template("animals_delete.html", animal=animal)

@app.route("/employees", endpoint="employees")
@login_required
def employees():
    conn = get_db_connection()
    employees = conn.execute("SELECT * FROM Employees").fetchall()
    conn.close()
    return render_template("employees.html", employees=employees)

@app.route("/employees/new", methods=["GET", "POST"])
@login_required
def new_employee():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        supervisor_id = request.form["supervisor_id"]
        job_title = request.form["job_title"]
        phone = request.form["phone"]
        email = request.form["email"]
    
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO Employees (first_name, last_name, supervisor_id, job_title, phone, email) VALUES (?, ?, ?, ?, ?, ?)",
            (first_name, last_name, supervisor_id, job_title, phone, email)
        )
        conn.commit()
        conn.close()

        flash("New employee added!", "success")
        return redirect(url_for("employees"))

    return render_template("employees_form.html", employee=None)

@app.route("/employees/<employee_id>/edit", methods=["GET", "POST"])
@login_required
def edit_employee(employee_id):
    conn = get_db_connection()
    employee = conn.execute("SELECT * FROM Employees WHERE employee_id = ?", (employee_id,)).fetchone()

    if not employee:
        return "Employee not found", 404

    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        supervisor_id = request.form["supervisor_id"]
        job_title = request.form["job_title"]
        phone = request.form["phone"]
        email = request.form["email"]
    
        conn.execute("""
            UPDATE Employees
            SET first_name=?, last_name=?, supervisor_id=?, job_title=?, phone=?, email=?
            WHERE employee_id=?
        """, (first_name, last_name, supervisor_id, job_title, phone, email, employee_id))

        conn.commit()
        conn.close()
        return redirect(url_for("employees"))

    # GET → show form pre-filled
    conn.close()
    return render_template("employees_form.html", employee=employee)

@app.route("/employees/<employee_id>/delete", methods=["GET", "POST"])
@login_required
def delete_employee(employee_id):
    conn = get_db_connection()
    employee = conn.execute("SELECT * FROM Employees WHERE employee_id = ?", (employee_id,)).fetchone()

    if employee is None:
        conn.close()
        flash("Employee not found.", "danger")
        return redirect(url_for("employees"))

    # If POST, confirm delete
    if request.method == "POST":
        conn.execute("DELETE FROM Employees WHERE employee_id = ?", (employee_id,))
        conn.commit()
        conn.close()
        flash("Employee deleted!", "success")
        return redirect(url_for("employees"))
    
    # If GET, show confirmation page
    conn.close()
    return render_template("employees_delete.html", employee=employee)

@app.route("/adopters", endpoint="adopters")
@login_required
def adopters():
    conn = get_db_connection()
    adopters = conn.execute("SELECT * FROM Adopters").fetchall()
    conn.close()
    return render_template("adopters.html", adopters=adopters)
        
@app.route("/adopters/new", methods=["GET", "POST"])
@login_required
def new_adopter():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        address = request.form["address"]
        phone = request.form["phone"]
        email = request.form["email"]
    
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO Adopters (first_name, last_name, address, phone, email) VALUES (?, ?, ?, ?, ?)",
            (first_name, last_name, address, phone, email)
        )
        conn.commit()
        conn.close()

        flash("New adopter added!", "success")
        return redirect(url_for("adopters"))

    return render_template("adopters_form.html", adopter=None)

@app.route("/adopters/<adopter_id>/edit", methods=["GET", "POST"])
@login_required
def edit_adopter(adopter_id):
    conn = get_db_connection()
    adopter = conn.execute("SELECT * FROM Adopters WHERE adopter_id = ?", (adopter_id,)).fetchone()

    if not adopter:
        return "adopter not found", 404

    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        address = request.form["address"]
        phone = request.form["phone"]
        email = request.form["email"]
    
        conn.execute("""
            UPDATE Adopters
            SET first_name=?, last_name=?, address=?, phone=?, email=?
            WHERE adopter_id=?
        """, (first_name, last_name, address, phone, email, adopter_id))

        conn.commit()
        conn.close()
        return redirect(url_for("adopters"))

    # GET → show form pre-filled
    conn.close()
    return render_template("adopters_form.html", adopter=adopter)

@app.route("/adopters/<adopter_id>/delete", methods=["GET", "POST"])
@login_required
def delete_adopter(adopter_id):
    conn = get_db_connection()
    adopter = conn.execute("SELECT * FROM Adopters WHERE adopter_id = ?", (adopter_id,)).fetchone()

    if adopter is None:
        conn.close()
        flash("Adopter not found.", "danger")
        return redirect(url_for("adopters"))

    # If POST, confirm delete
    if request.method == "POST":
        conn.execute("DELETE FROM Adopters WHERE adopter_id = ?", (adopter_id,))
        conn.commit()
        conn.close()
        flash("Adopter deleted!", "success")
        return redirect(url_for("adopters"))
    
    # If GET, show confirmation page
    conn.close()
    return render_template("adopters_delete.html", adopter=adopter)

@app.route("/adoptions", endpoint="adoptions")
@login_required
def adoptions():
    conn = get_db_connection()
    adoptions = conn.execute("SELECT * FROM Adoptions").fetchall()
    conn.close()
    return render_template("adoptions.html", adoptions=adoptions)

@app.route("/adoptions/new", methods=["GET", "POST"])
@login_required
def new_adoption():
    if request.method == "POST":
        animal_id = request.form["animal_id"]
        adopter_id = request.form["adopter_id"]
        employee_id = request.form["employee_id"]
        adoption_date = request.form["adoption_date"]
        adoption_fee = request.form["adoption_fee"]
    
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO Adoptions (animal_id, adopter_id, employee_id, adoption_date, adoption_fee) VALUES (?, ?, ?, ?, ?)",
            (animal_id, adopter_id, employee_id, adoption_date, adoption_fee)
        )
        conn.commit()
        conn.close()

        flash("New adoption added!", "success")
        return redirect(url_for("adoptions"))

    return render_template("adoptions_form.html", adoption=None)

@app.route("/adoptions/<adoption_id>/edit", methods=["GET", "POST"])
@login_required
def edit_adoption(adoption_id):
    conn = get_db_connection()
    adoption = conn.execute("SELECT * FROM Adoptions WHERE adoption_id = ?", (adoption_id,)).fetchone()

    if not adoption:
        return "adoption not found", 404

    if request.method == "POST":
        animal_id = request.form["animal_id"]
        adopter_id = request.form["adopter_id"]
        employee_id = request.form["employee_id"]
        adoption_date = request.form["adoption_date"]
        adoption_fee = request.form["adoption_fee"]
    
        conn.execute("""
            UPDATE Adoptions
            SET animal_id=?, adopter_id=?, employee_id=?, adoption_date=?, adoption_fee=?
            WHERE adoption_id=?
        """, (animal_id, adopter_id, employee_id, adoption_date, adoption_fee, adoption_id))

        conn.commit()
        conn.close()
        return redirect(url_for("adoptions"))

    # GET → show form pre-filled
    conn.close()
    return render_template("adoptions_form.html", adoption=adoption)

@app.route("/adoptions/<adoption_id>/delete", methods=["GET", "POST"])
@login_required
def delete_adoption(adoption_id):
    conn = get_db_connection()
    adoption = conn.execute("SELECT * FROM Adoptions WHERE adoption_id = ?", (adoption_id,)).fetchone()

    if adoption is None:
        conn.close()
        flash("Adoption not found.", "danger")
        return redirect(url_for("adoptions"))

    # If POST, confirm delete
    if request.method == "POST":
        conn.execute("DELETE FROM Adoptions WHERE adoption_id = ?", (adoption_id,))
        conn.commit()
        conn.close()
        flash("Adoption deleted!", "success")
        return redirect(url_for("adoptions"))
    
    # If GET, show confirmation page
    conn.close()
    return render_template("adoptions_delete.html", adoption=adoption)

@app.route("/healthrecords", endpoint="healthrecords")
@login_required
def healthrecords():
    conn = get_db_connection()
    healthrecords = conn.execute("SELECT * FROM HealthRecords").fetchall()
    conn.close()
    return render_template("healthrecords.html", healthrecords=healthrecords)

@app.route("/healthrecords/new", methods=["GET", "POST"])
@login_required
def new_healthrecord():
    if request.method == "POST":
        animal_id = request.form["animal_id"]
        employee_id = request.form["employee_id"]
        record_type = request.form["record_type"]
        diagnosis = request.form["diagnosis"]
        treatment = request.form["treatment"]
        date = request.form["date"]
    
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO HealthRecords (animal_id, employee_id, record_type, diagnosis, treatment, date) VALUES (?, ?, ?, ?, ?, ?)",
            (animal_id, employee_id, record_type, diagnosis, treatment, date)
        )
        conn.commit()
        conn.close()

        flash("New health record added!", "success")
        return redirect(url_for("healthrecords"))

    return render_template("healthrecords_form.html", healthrecord=None)

@app.route("/healthrecords/<record_id>/edit", methods=["GET", "POST"])
@login_required
def edit_healthrecord(record_id):
    conn = get_db_connection()
    healthrecord = conn.execute("SELECT * FROM HealthRecords WHERE record_id = ?", (record_id,)).fetchone()

    if not healthrecord:
        return "health record not found", 404

    if request.method == "POST":
        animal_id = request.form["animal_id"]
        employee_id = request.form["employee_id"]
        record_type = request.form["record_type"]
        diagnosis = request.form["diagnosis"]
        treatment = request.form["treatment"]
        date = request.form["date"]
    
        conn.execute("""
            UPDATE HealthRecords
            SET animal_id=?, employee_id=?, record_type=?, diagnosis=?, treatment=?, date=?
            WHERE record_id=?
        """, (animal_id, employee_id, record_type, diagnosis, treatment, date, record_id))

        conn.commit()
        conn.close()
        return redirect(url_for("healthrecords"))

    # GET → show form pre-filled
    conn.close()
    return render_template("healthrecords_form.html", healthrecord=healthrecord)

@app.route("/healthrecords/<record_id>/delete", methods=["GET", "POST"])
@login_required
def delete_healthrecord(record_id):
    conn = get_db_connection()
    healthrecord = conn.execute("SELECT * FROM HealthRecords WHERE record_id = ?", (record_id,)).fetchone()

    if healthrecord is None:
        conn.close()
        flash("Health record not found.", "danger")
        return redirect(url_for("healthrecords"))

    # If POST, confirm delete
    if request.method == "POST":
        conn.execute("DELETE FROM HealthRecords WHERE record_id = ?", (record_id,))
        conn.commit()
        conn.close()
        flash("Health record deleted!", "success")
        return redirect(url_for("healthrecords"))
    
    # If GET, show confirmation page
    conn.close()
    return render_template("healthrecords_delete.html", healthrecord=healthrecord)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        hashed_pw = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO Users (username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed_pw)
            )
            conn.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("Username or email already exists.", "danger")

        finally:
            conn.close()

    return render_template("register.html", form=form)

@app.route("/analytics")
@login_required
def analytics():
    conn = get_db_connection()
    
    # --- Intakes over time ---
    intakes = conn.execute("SELECT intake_date FROM Animals").fetchall()
    adoptions = conn.execute("SELECT adoption_date FROM Adoptions").fetchall()
    
    # helper to count per month
    def get_month_counts(dates):
        counts = {}
        for row in dates:
            date_str = row[0]
            if date_str:
                month = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m")
                counts[month] = counts.get(month, 0) + 1
        sorted_months = sorted(counts.keys())
        return sorted_months, [counts[m] for m in sorted_months]
    
    months_intakes, intakes_counts = get_month_counts(intakes)
    months_adoptions, adoptions_counts = get_month_counts(adoptions)

    all_months = sorted(set(months_intakes + months_adoptions))
    intakes_counts = [intakes_counts[months_intakes.index(m)] if m in months_intakes else 0 for m in all_months]
    adoptions_counts = [adoptions_counts[months_adoptions.index(m)] if m in months_adoptions else 0 for m in all_months]

    # Status pie chart
    statuses = conn.execute("SELECT status, COUNT(*) as count FROM Animals GROUP BY status").fetchall()
    status_labels = [row["status"] for row in statuses]
    status_counts = [row["count"] for row in statuses]

    # Health & spay/neuter

    total_animals = conn.execute("SELECT COUNT(*) AS total FROM Animals").fetchone()["total"]

    health_done = conn.execute("""
        SELECT COUNT(*) AS done
        FROM Animals a
        WHERE EXISTS (
            SELECT 1
            FROM HealthRecords h
            WHERE h.animal_id = a.animal_id
            AND h.record_type = 'health check'
        )
    """).fetchone()["done"]

    spay_done = conn.execute("""
        SELECT COUNT(*) AS done
        FROM Animals a
        WHERE EXISTS (
            SELECT 1
            FROM HealthRecords h
            WHERE h.animal_id = a.animal_id
            AND h.record_type = 'spay/neuter'
        )
    """).fetchone()["done"]

    health_pct = round((health_done / total_animals) * 100, 1) if total_animals else 0
    spay_pct = round((spay_done / total_animals) * 100, 1) if total_animals else 0

    # Long-stay
    long_stay_threshold = datetime.now() - timedelta(days=90)
    long_stays = conn.execute("SELECT name, intake_date, status FROM Animals WHERE intake_date <= ?", 
                              (long_stay_threshold.strftime("%Y-%m-%d"),)).fetchall()

    conn.close()

    return render_template("analytics.html",
                       months=all_months,
                       intakes_counts=intakes_counts,
                       adoptions_counts=adoptions_counts,
                       status_labels=status_labels,
                       status_counts=status_counts,
                       health_pct=health_pct,
                       spay_pct=spay_pct,
                       long_stays=long_stays)



if __name__ == "__main__":
    app.run(debug=True)


