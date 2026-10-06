```python
from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
import os


# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "smart-fin-demo-secret"
)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


# =========================================================
# DATABASE MODELS
# =========================================================

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    full_name = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    monthly_income = db.Column(
        db.Float,
        default=0
    )

    financial_goal = db.Column(
        db.String(200),
        default=""
    )


class Finance(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user = db.Column(
        db.String(100),
        nullable=False
    )

    income = db.Column(
        db.Float,
        default=0
    )

    expense = db.Column(
        db.Float,
        default=0
    )


class Goal(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user = db.Column(
        db.String(100),
        nullable=False
    )

    target = db.Column(
        db.Float,
        default=0
    )

    saved = db.Column(
        db.Float,
        default=0
    )


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

with app.app_context():
    db.create_all()


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    # Show the professional landing page
    return render_template("index.html")


# =========================================================
# ABOUT
# =========================================================

@app.route("/about")
def about():

    return render_template("about.html")


# =========================================================
# CONTACT
# =========================================================

@app.route("/contact")
def contact():

    return render_template("contact.html")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # -----------------------------
        # Get form data
        # -----------------------------

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        monthly_income = request.form.get(
            "monthly_income",
            "0"
        )

        financial_goal = request.form.get(
            "financial_goal",
            ""
        ).strip()


        # -----------------------------
        # Required fields
        # -----------------------------

        if not full_name:
            flash(
                "Please enter your name.",
                "danger"
            )
            return redirect("/register")


        if not email:
            flash(
                "Please enter your email address.",
                "danger"
            )
            return redirect("/register")


        if not username:
            flash(
                "Please choose a username.",
                "danger"
            )
            return redirect("/register")


        if not password:
            flash(
                "Please create a password.",
                "danger"
            )
            return redirect("/register")


        # -----------------------------
        # Password validation
        # -----------------------------

        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "danger"
            )

            return redirect("/register")


        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect("/register")


        # -----------------------------
        # Income validation
        # -----------------------------

        try:

            monthly_income = float(
                monthly_income or 0
            )

            if monthly_income < 0:
                raise ValueError

        except ValueError:

            flash(
                "Please enter a valid monthly income.",
                "danger"
            )

            return redirect("/register")


        # -----------------------------
        # Duplicate username
        # -----------------------------

        existing_username = User.query.filter_by(
            username=username
        ).first()

        if existing_username:

            flash(
                "Username already exists. Please choose another.",
                "danger"
            )

            return redirect("/register")


        # -----------------------------
        # Duplicate email
        # -----------------------------

        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:

            flash(
                "This email is already registered. Please login.",
                "danger"
            )

            return redirect("/register")


        # -----------------------------
        # Password hashing
        # -----------------------------

        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")


        # -----------------------------
        # Create user
        # -----------------------------

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

            flash(
                "Account created successfully! Please login.",
                "success"
            )

            return redirect("/login")


        except IntegrityError:

            db.session.rollback()

            flash(
                "Username or email already exists.",
                "danger"
            )

            return redirect("/register")


    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        user = User.query.filter_by(
            username=username
        ).first()


        if user and bcrypt.check_password_hash(
            user.password,
            password
        ):

            session["user"] = user.username

            return redirect("/dashboard")


        flash(
            "Invalid username or password.",
            "danger"
        )


    return render_template(
        "login.html"
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:

        return redirect("/login")


    username = session["user"]


    user = User.query.filter_by(
        username=username
    ).first()


    if not user:

        session.pop("user", None)

        return redirect("/login")


    # -----------------------------
    # Finance records
    # -----------------------------

    data = Finance.query.filter_by(
        user=username
    ).all()


    # -----------------------------
    # Savings goal
    # -----------------------------

    goal = Goal.query.filter_by(
        user=username
    ).first()


    # -----------------------------
    # Chart data
    # -----------------------------

    income_list = [
        record.income or 0
        for record in data
    ]


    expense_list = [
        record.expense or 0
        for record in data
    ]


    # -----------------------------
    # Totals
    # -----------------------------

    total_income = sum(
        income_list
    )


    total_expense = sum(
        expense_list
    )


    savings = (
        total_income -
        total_expense
    )


    # -----------------------------
    # User profile
    # -----------------------------

    full_name = user.full_name

    monthly_income = (
        user.monthly_income or 0
    )

    financial_goal = (
        user.financial_goal or ""
    )


    # =====================================================
    # SMART FINANCIAL ADVICE
    # =====================================================

    if total_income == 0:

        advice = (
            "Start by adding your income and expenses "
            "to receive personalized financial insights."
        )

    else:

        saving_rate = (
            savings / total_income
        ) * 100


        if savings < 0:

            advice = (
                "Your expenses are currently higher than "
                "your income. Review non-essential spending "
                "and focus on bringing your monthly balance "
                "back into the positive."
            )

        elif saving_rate >= 30:

            advice = (
                "Excellent! You are maintaining a strong "
                "savings rate. Keep building your financial "
                "safety net and continue working towards "
                "your financial goals."
            )

        elif saving_rate >= 20:

            advice = (
                "Great job! You are maintaining a healthy "
                "savings rate. Keep tracking your expenses "
                "and stay consistent with your savings."
            )

        elif saving_rate > 0:

            advice = (
                "You are saving money, which is a good start. "
                "Try reducing unnecessary expenses and gradually "
                "increase your savings rate towards 20%."
            )

        else:

            advice = (
                "Your current income and expenses are balanced. "
                "Consider setting a monthly savings target to "
                "build stronger financial security."
            )


    # =====================================================
    # RENDER DASHBOARD
    # =====================================================

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


# =========================================================
# ADD FINANCIAL RECORD
# =========================================================

@app.route("/add", methods=["POST"])
def add():

    if "user" not in session:

        return redirect("/login")


    try:

        income = float(
            request.form.get(
                "income",
                0
            ) or 0
        )


        expense = float(
            request.form.get(
                "expense",
                0
            ) or 0
        )


        # -----------------------------
        # Validation
        # -----------------------------

        if income < 0 or expense < 0:

            flash(
                "Income and expense cannot be negative.",
                "danger"
            )

            return redirect("/dashboard")


        if income == 0 and expense == 0:

            flash(
                "Please enter an income or expense amount.",
                "warning"
            )

            return redirect("/dashboard")


        # -----------------------------
        # Create record
        # -----------------------------

        record = Finance(

            user=session["user"],

            income=income,

            expense=expense
        )


        db.session.add(record)


        # -----------------------------
        # Update goal savings
        # -----------------------------

        goal = Goal.query.filter_by(
            user=session["user"]
        ).first()


        if goal:

            goal.saved += (
                income - expense
            )


            if goal.saved < 0:

                goal.saved = 0


        db.session.commit()


        flash(
            "Financial record added successfully!",
            "success"
        )


    except ValueError:

        flash(
            "Please enter valid numbers.",
            "danger"
        )


    except Exception:

        db.session.rollback()

        flash(
            "Something went wrong while saving your record.",
            "danger"
        )


    return redirect("/dashboard")


# =========================================================
# SET SAVINGS GOAL
# =========================================================

@app.route("/set_goal", methods=["POST"])
def set_goal():

    if "user" not in session:

        return redirect("/login")


    try:

        target = float(
            request.form.get(
                "target",
                0
            )
        )


        if target <= 0:

            flash(
                "Please enter a valid savings goal.",
                "danger"
            )

            return redirect("/dashboard")


        goal = Goal.query.filter_by(
            user=session["user"]
        ).first()


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


        flash(
            "Savings goal updated successfully!",
            "success"
        )


    except ValueError:

        flash(
            "Please enter a valid amount.",
            "danger"
        )


    except Exception:

        db.session.rollback()

        flash(
            "Unable to update your savings goal.",
            "danger"
        )


    return redirect("/dashboard")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.pop(
        "user",
        None
    )

    return redirect("/")


# =========================================================
# LOCAL DEVELOPMENT
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
```
