from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import os

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "smart-fin-demo-secret"
)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


# =========================
# MODELS
# =========================

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
    category = db.Column(db.String(100), default="Other")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    target = db.Column(db.Float, default=0)
    saved = db.Column(db.Float, default=0)


with app.app_context():
    db.create_all()


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


# =========================
# REGISTER
# =========================

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
            flash("Please fill all required fields.", "info")
            return redirect("/register")

        if password != confirm_password:
            flash("Passwords do not match.", "info")
            return redirect("/register")

        if len(password) < 8:
            flash(
                "For better account security, please use at least 8 characters.",
                "info"
            )
            return redirect("/register")

        try:
            monthly_income = float(monthly_income or 0)

            if monthly_income < 0:
                raise ValueError

        except ValueError:
            flash("Please enter a valid monthly income.", "info")
            return redirect("/register")

        if User.query.filter_by(username=username).first():
            flash(
                "Username already exists. Please choose another.",
                "info"
            )
            return redirect("/register")

        if User.query.filter_by(email=email).first():
            flash(
                "Email already registered. Please login.",
                "info"
            )
            return redirect("/register")

        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

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
                "info"
            )
            return redirect("/register")

    return render_template("register.html")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

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
            "info"
        )

    return render_template("login.html")


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    username = session["user"]

    user = User.query.filter_by(
        username=username
    ).first()

    data = Finance.query.filter_by(
        user=username
    ).order_by(
        Finance.created_at.desc()
    ).all()

    goal = Goal.query.filter_by(
        user=username
    ).first()

    # =========================
    # TOTALS
    # =========================

    total_income = round(
        sum((d.income or 0) for d in data),
        2
    )

    total_expense = round(
        sum((d.expense or 0) for d in data),
        2
    )

    savings = round(
        total_income - total_expense,
        2
    )

    # =========================
    # SAVING RATE
    # =========================

    if total_income > 0:

        saving_rate = round(
            (savings / total_income) * 100,
            1
        )

        # Never display a negative saving rate
        # as a positive-looking financial metric.
        saving_rate_display = max(
            saving_rate,
            0
        )

    else:

        saving_rate = 0
        saving_rate_display = 0

    # =========================
    # EXPENSE RATIO
    # =========================

    if total_income > 0:
        expense_ratio = (
            total_expense / total_income
        ) * 100
    else:
        expense_ratio = 0

    # =========================
    # FINANCIAL HEALTH SCORE
    # =========================

    if total_income <= 0:

        health_score = 0

    elif savings <= 0:

        # Expenses are equal to or greater than income.
        health_score = 25

    else:

        score = 50

        if saving_rate >= 20:
            score += 25

        elif saving_rate >= 10:
            score += 15

        elif saving_rate > 0:
            score += 5

        if expense_ratio <= 70:
            score += 15

        elif expense_ratio <= 85:
            score += 8

        if goal and goal.target > 0:

            goal_progress_for_score = min(
                (goal.saved / goal.target) * 100,
                100
            )

            if goal_progress_for_score >= 50:
                score += 10

            elif goal_progress_for_score > 0:
                score += 5

        health_score = min(
            round(score),
            100
        )

    # =========================
    # HEALTH STATUS
    # =========================

    if health_score >= 80:
        health_status = "Excellent"

    elif health_score >= 60:
        health_status = "Healthy"

    elif health_score >= 40:
        health_status = "Needs Attention"

    else:
        health_status = "Getting Started"

    # =========================
    # SMART ADVICE
    # =========================

    if total_income == 0:

        advice = (
            "Start by adding your income and expenses. "
            "Smart-Fin will analyze your financial habits "
            "and provide personalized insights."
        )

    elif savings <= 0:

        advice = (
            "Your expenses are currently equal to or higher "
            "than your income. Review non-essential spending "
            "and create a realistic monthly budget."
        )

    elif saving_rate < 10:

        advice = (
            "Your savings rate is currently below 10%. "
            "Try reducing unnecessary spending and gradually "
            "increase the amount you save each month."
        )

    elif saving_rate < 20:

        advice = (
            "You're saving money, which is a positive start. "
            "Try moving toward a 20% savings rate for stronger "
            "financial stability."
        )

    else:

        advice = (
            f"Great progress! You're saving around "
            f"{saving_rate_display}% of your recorded income. "
            "Keep maintaining this habit and continue building "
            "your financial safety net."
        )

    # =========================
    # GOAL ANALYSIS
    # =========================

    goal_remaining = 0
    goal_progress = 0
    estimated_months = 0

    if goal and goal.target > 0:

        goal_saved = max(
            goal.saved or 0,
            0
        )

        goal_remaining = max(
            goal.target - goal_saved,
            0
        )

        goal_progress = min(
            round(
                (goal_saved / goal.target) * 100,
                1
            ),
            100
        )

        # Estimate based on current positive monthly savings.
        if savings > 0 and goal_remaining > 0:

            estimated_months = max(
                1,
                round(
                    goal_remaining / savings
                )
            )

    # =========================
    # MONTHLY RECOMMENDATION
    # =========================

    monthly_income = (
        user.monthly_income
        if user
        else 0
    )

    if monthly_income and monthly_income > 0:

        recommended_saving = round(
            monthly_income * 0.20,
            2
        )

    else:

        recommended_saving = 0

    # =========================
    # CHART DATA
    # =========================

    recent_data = list(
        reversed(data[:7])
    )

    chart_labels = [
        d.created_at.strftime("%d %b")
        if d.created_at
        else ""
        for d in recent_data
    ]

    income_list = [
        round(d.income or 0, 2)
        for d in recent_data
    ]

    expense_list = [
        round(d.expense or 0, 2)
        for d in recent_data
    ]

    # =========================
    # RECENT TRANSACTIONS
    # =========================

    recent_transactions = data[:6]

    full_name = (
        user.full_name
        if user
        else username
    )

    financial_goal = (
        user.financial_goal
        if user
        else ""
    )

    return render_template(
        "dashboard.html",

        user=username,
        full_name=full_name,

        monthly_income=monthly_income,
        financial_goal=financial_goal,

        data=data,
        recent_transactions=recent_transactions,

        total_income=total_income,
        total_expense=total_expense,
        savings=savings,

        saving_rate=saving_rate_display,

        health_score=health_score,
        health_status=health_status,

        advice=advice,

        goal=goal,
        goal_remaining=goal_remaining,
        goal_progress=goal_progress,
        estimated_months=estimated_months,

        recommended_saving=recommended_saving,

        chart_labels=chart_labels,
        income_list=income_list,
        expense_list=expense_list
    )


# =========================
# ADD FINANCIAL RECORD
# =========================

@app.route("/add", methods=["POST"])
def add():

    if "user" not in session:
        return redirect("/login")

    # -------------------------
    # Get transaction type
    # -------------------------

    transaction_type = request.form.get(
        "transaction_type",
        ""
    ).strip().lower()

    category = request.form.get(
        "category",
        "Other"
    ).strip()

    # -------------------------
    # Validate transaction type
    # -------------------------

    if transaction_type not in [
        "income",
        "expense"
    ]:

        flash(
            "Please select Income or Expense.",
            "info"
        )

        return redirect("/dashboard")

    # -------------------------
    # Get amount
    # -------------------------

    amount_raw = request.form.get(
        "amount",
        ""
    ).strip()

    # -------------------------
    # Backward compatibility
    #
    # If old dashboard form is still
    # being used, support it temporarily.
    # -------------------------

    if not amount_raw:

        try:

            old_income = float(
                request.form.get(
                    "income",
                    0
                ) or 0
            )

            old_expense = float(
                request.form.get(
                    "expense",
                    0
                ) or 0
            )

        except ValueError:

            flash(
                "Please enter a valid amount.",
                "info"
            )

            return redirect("/dashboard")

        # Old form must never allow both.

        if old_income > 0 and old_expense > 0:

            flash(
                "Please add Income and Expense as separate transactions.",
                "info"
            )

            return redirect("/dashboard")

        if old_income > 0:

            transaction_type = "income"
            amount = old_income

        elif old_expense > 0:

            transaction_type = "expense"
            amount = old_expense

        else:

            flash(
                "Please enter an amount.",
                "info"
            )

            return redirect("/dashboard")

    else:

        try:

            amount = float(amount_raw)

        except ValueError:

            flash(
                "Please enter a valid amount.",
                "info"
            )

            return redirect("/dashboard")

    # -------------------------
    # Amount validation
    # -------------------------

    if amount <= 0:

        flash(
            "Amount must be greater than ₹0.",
            "info"
        )

        return redirect("/dashboard")

    # Prevent extremely unrealistic accidental input.
    if amount > 100000000:

        flash(
            "Please enter a realistic transaction amount.",
            "info"
        )

        return redirect("/dashboard")

    # -------------------------
    # Category validation
    # -------------------------

    allowed_categories = {
        "Food",
        "Transport",
        "Shopping",
        "Bills",
        "Education",
        "Entertainment",
        "Healthcare",
        "Other"
    }

    if category not in allowed_categories:

        category = "Other"

    # -------------------------
    # IMPORTANT:
    # One record = ONE transaction.
    #
    # Income record:
    # income = amount
    # expense = 0
    #
    # Expense record:
    # income = 0
    # expense = amount
    # -------------------------

    if transaction_type == "income":

        income = amount
        expense = 0

    else:

        income = 0
        expense = amount

    record = Finance(
        user=session["user"],
        income=income,
        expense=expense,
        category=category,
        created_at=datetime.utcnow()
    )

    try:

        db.session.add(record)
        db.session.commit()

        flash(
            "Financial record added successfully!",
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to save the financial record. Please try again.",
            "info"
        )

    return redirect("/dashboard")


# =========================
# SET GOAL
# =========================

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
                "info"
            )

            return redirect("/dashboard")

        if target > 100000000:

            flash(
                "Please enter a realistic savings goal.",
                "info"
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
            "info"
        )

    return redirect("/dashboard")

# =========================
# DELETE TRANSACTION
# =========================

@app.route("/delete_transaction/<int:transaction_id>", methods=["POST"])
def delete_transaction(transaction_id):

    if "user" not in session:
        return redirect("/login")

    transaction = Finance.query.filter_by(
        id=transaction_id,
        user=session["user"]
    ).first()

    if not transaction:
        flash(
            "Transaction not found.",
            "info"
        )
        return redirect("/dashboard")

    try:

        db.session.delete(transaction)
        db.session.commit()

        flash(
            "Transaction deleted successfully!",
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to delete transaction. Please try again.",
            "info"
        )

    return redirect("/dashboard")
# =========================
# FORGOT PASSWORD
# =========================

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        new_password = request.form.get(
            "new_password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # -------------------------
        # Validate required fields
        # -------------------------

        if not username or not email or not new_password or not confirm_password:

            flash(
                "Please fill all fields.",
                "info"
            )

            return redirect("/forgot-password")

        # -------------------------
        # Check password length
        # -------------------------

        if len(new_password) < 8:

            flash(
                "Password must contain at least 8 characters.",
                "info"
            )

            return redirect("/forgot-password")

        # -------------------------
        # Check password match
        # -------------------------

        if new_password != confirm_password:

            flash(
                "Passwords do not match.",
                "info"
            )

            return redirect("/forgot-password")

        # -------------------------
        # Find account
        # -------------------------

        user = User.query.filter_by(
            username=username,
            email=email
        ).first()

        if not user:

            flash(
                "No account found with this username and email.",
                "info"
            )

            return redirect("/forgot-password")

        # -------------------------
        # Update password
        # -------------------------

        user.password = bcrypt.generate_password_hash(
            new_password
        ).decode("utf-8")

        try:

            db.session.commit()

            flash(
                "Password reset successfully! Please login with your new password.",
                "success"
            )

            return redirect("/login")

        except Exception:

            db.session.rollback()

            flash(
                "Unable to reset password. Please try again.",
                "info"
            )

            return redirect("/forgot-password")

    return render_template(
        "forgot_password.html"
    )
# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.pop(
        "user",
        None
    )

    return redirect("/")


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)