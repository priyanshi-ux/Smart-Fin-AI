from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "smart-fin-demo-secret")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


# ---------------- MODELS ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    monthly_income = db.Column(db.Float, default=0)
    financial_goal = db.Column(db.String(200), default="")


class Finance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    income = db.Column(db.Float, default=0)
    expense = db.Column(db.Float, default=0)


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    target = db.Column(db.Float, default=0)
    saved = db.Column(db.Float, default=0)


# ---------------- DATABASE ----------------

with app.app_context():
    db.create_all()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return redirect("/login")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        monthly_income = request.form.get("monthly_income", 0)
        financial_goal = request.form.get("financial_goal", "").strip()

        if not full_name or not email or not username or not password:
            flash("Please fill all required fields.", "danger")
            return redirect("/register")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect("/register")

        if len(password) < 6:
            flash("Password must contain at least 6 characters.", "danger")
            return redirect("/register")

        try:
            monthly_income = float(monthly_income or 0)

            if monthly_income < 0:
                raise ValueError

        except ValueError:
            flash("Please enter a valid monthly income.", "danger")
            return redirect("/register")

        existing_username = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_username:
            flash("Username already exists. Please choose another.", "danger")
            return redirect("/register")

        if existing_email:
            flash("Email already registered. Please login.", "danger")
            return redirect("/register")

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User(
            full_name=full_name,
            email=email,
            username=username,
            password=hashed_password,
            monthly_income=monthly_income,
            financial_goal=financial_goal
        )

        try:
            db.session.add(user)
            db.session.commit()

            flash("Account created successfully! Please login.", "success")
            return redirect("/login")

        except IntegrityError:
            db.session.rollback()
            flash("Username or email already exists.", "danger")
            return redirect("/register")

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):

            session["user"] = user.username

            return redirect("/dashboard")

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    username = session["user"]

    user = User.query.filter_by(username=username).first()

    data = Finance.query.filter_by(user=username).all()

    goal = Goal.query.filter_by(user=username).first()

    income_list = [d.income or 0 for d in data]
    expense_list = [d.expense or 0 for d in data]

    total_income = sum(income_list)
    total_expense = sum(expense_list)
    savings = total_income - total_expense

    if user:
        monthly_income = user.monthly_income or 0
        financial_goal = user.financial_goal or ""
        full_name = user.full_name
    else:
        monthly_income = 0
        financial_goal = ""
        full_name = username

    # Smart financial advice
    if total_income == 0:
        advice = "Start by adding your income and expenses to receive personalized financial insights."
    elif savings > 0:
        saving_rate = (savings / total_income) * 100

        if saving_rate >= 20:
            advice = "Great job! You are maintaining a healthy savings rate. Keep building your financial safety net."
        else:
            advice = "You are saving money. Try reducing unnecessary expenses and aim to save at least 20% of your income."
    else:
        advice = "Your expenses are higher than your income. Review your spending and prioritize essential expenses."

    return render_template(
        "dashboard.html",
        user=username,
        full_name=full_name,
        monthly_income=monthly_income,
        financial_goal=financial_goal,
        data=data,
        income_list=income_list,
        expense_list=expense_list,
        total_income=total_income,
        total_expense=total_expense,
        savings=savings,
        goal=goal,
        advice=advice
    )


# ---------------- ADD FINANCE RECORD ----------------

@app.route("/add", methods=["POST"])
def add():

    if "user" not in session:
        return redirect("/login")

    try:
        income = float(request.form.get("income", 0) or 0)
        expense = float(request.form.get("expense", 0) or 0)

        if income < 0 or expense < 0:
            flash("Income and expense cannot be negative.", "danger")
            return redirect("/dashboard")

        record = Finance(
            user=session["user"],
            income=income,
            expense=expense
        )

        db.session.add(record)

        goal = Goal.query.filter_by(user=session["user"]).first()

        if goal:
            goal.saved += income - expense

            if goal.saved < 0:
                goal.saved = 0

        db.session.commit()

        flash("Financial record added successfully!", "success")

    except ValueError:
        flash("Please enter valid numbers.", "danger")

    return redirect("/dashboard")


# ---------------- SET GOAL ----------------

@app.route("/set_goal", methods=["POST"])
def set_goal():

    if "user" not in session:
        return redirect("/login")

    try:
        target = float(request.form.get("target", 0))

        if target <= 0:
            flash("Please enter a valid savings goal.", "danger")
            return redirect("/dashboard")

        goal = Goal.query.filter_by(user=session["user"]).first()

        if goal:
            goal.target = target
        else:
            goal = Goal(
                user=session["user"],
                target=target,
                saved=0
            )
            db.session.add(goal)

        db.session.commit()

        flash("Savings goal updated successfully!", "success")

    except ValueError:
        flash("Please enter a valid amount.", "danger")

    return redirect("/dashboard")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)
