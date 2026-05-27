from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------- DATABASE ----------------
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Your Password",
    "database": "health_tracker"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# ---------------- BMI LOGIC ----------------
def calculate_bmi(weight, height):
    return round(weight / ((height / 100) ** 2), 2)

def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def workout_plan(category):
    if category == "Underweight":
        return {
            "Monday": "Light strength (full body)",
            "Wednesday": "Yoga & mobility",
            "Friday": "Core + resistance bands"
        }
    elif category == "Normal":
        return {
            "Monday": "Chest + Triceps",
            "Tuesday": "Back + Biceps",
            "Thursday": "Legs",
            "Saturday": "Cardio + Core"
        }
    else:
        return {
            "Monday": "Cardio (30 min)",
            "Wednesday": "HIIT",
            "Friday": "Fast walking + stretching"
        }

def diet_plan(category):
    if category == "Underweight":
        return "High-calorie diet with milk, nuts, rice, chicken, paneer."
    elif category == "Normal":
        return "Balanced diet: fruits, vegetables, lean protein."
    else:
        return "Calorie deficit diet, avoid sugar & junk food."

# ---------------- ROUTES ----------------
@app.route("/")
def intro():
    return render_template("intro.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        height = request.form["height"]
        weight = request.form["weight"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, age, gender, height_cm, weight_kg) VALUES (%s,%s,%s,%s,%s)",
            (name, age, gender, height, weight)
        )
        conn.commit()
        user_id = cur.lastrowid
        cur.close()
        conn.close()

        session["user_id"] = user_id
        return redirect(url_for("dashboard"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form["user_id"]
        session["user_id"] = user_id
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE user_id=%s", (session["user_id"],))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        return redirect(url_for("login"))

    bmi = calculate_bmi(user["weight_kg"], user["height_cm"])
    category = bmi_category(bmi)

    workout = workout_plan(category)
    diet = diet_plan(category)

    return render_template(
        "dashboard.html",
        user=user,
        bmi=bmi,
        category=category,
        workout=workout,
        diet=diet
    )

@app.route("/update", methods=["POST"])
def update():
    if "user_id" not in session:
        return redirect(url_for("login"))

    age = request.form["age"]
    gender = request.form["gender"]
    height = request.form["height"]
    weight = request.form["weight"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET age=%s, gender=%s, height_cm=%s, weight_kg=%s
        WHERE user_id=%s
    """, (age, gender, height, weight, session["user_id"]))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True)
