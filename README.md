# 💰 Smart-Fin AI

### AI-Powered Personal Finance Advisor

**Smart-Fin AI** is a full-stack personal finance management and advisory web application built with **Python, Flask, SQLite, SQLAlchemy, HTML, CSS, and Bootstrap**.

The platform helps users manage their income and expenses, monitor their financial health, set savings goals, and receive personalized financial insights based on their transaction data.

🚀 **The project is completely functional and has been successfully deployed on Render.**

### 🌐 Live Demo

**Live Application:**  
https://smart-fin-ai.onrender.com

The deployed application supports user registration, login, dashboard access, transaction management, savings goals, financial analysis, and password recovery.

---

## 📌 Project Overview

Managing personal finances manually can make it difficult to understand spending patterns, savings progress, and overall financial health.

**Smart-Fin AI** provides a simple and user-friendly platform where users can:

- Create and manage their personal account
- Track income and expenses
- Monitor total savings
- Calculate savings rate
- Check their financial health score
- Set and monitor savings goals
- View recent transactions
- Receive smart financial recommendations
- Delete incorrect transactions
- Reset their password when required

The goal of the project is to make personal finance management **simple, organized, and data-driven**.

---

## ✨ Key Features

### 🔐 User Authentication

- User registration
- Secure login system
- Password hashing using Flask-Bcrypt
- Session-based authentication
- Logout functionality
- Forgot Password / Password Reset functionality
- Validation for username, email, and password

### 💸 Transaction Management

Users can record individual financial transactions.

Each transaction contains:

- Transaction type — Income / Expense
- Category
- Amount
- Description
- Date

Users can also delete transactions when they are no longer required.

### 📊 Financial Dashboard

The dashboard provides an overview of the user's financial condition.

It displays:

- Total Income
- Total Expenses
- Current Savings
- Saving Rate
- Financial Health Score
- Financial Health Status
- Recommended Monthly Saving
- Recent Transactions

### ❤️ Financial Health Analysis

Smart-Fin AI calculates a financial health score based on the user's financial activity.

The dashboard provides an easy-to-understand financial status such as:

- Excellent
- Good
- Needs Improvement

This helps users quickly understand their current financial position.

### 🎯 Savings Goals

Users can create a savings goal by specifying:

- Target amount
- Current saved amount

The application calculates:

- Remaining amount
- Estimated completion time

This helps users track their progress toward major financial goals.

### 💡 Smart Financial Advice

The application generates personalized financial recommendations using the user's income, expenses, savings, and saving rate.

Examples include recommendations related to:

- Increasing savings
- Controlling expenses
- Maintaining a healthy saving rate
- Achieving financial goals

### 🔒 Security

The application includes:

- Password hashing
- Session-based authentication
- Protected dashboard routes
- User-specific transaction access
- Input validation
- Secure database operations

---

## 🛠️ Technology Stack

### Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript

### Backend

- Python
- Flask

### Database

- SQLite
- SQLAlchemy / Flask-SQLAlchemy

### Security

- Flask-Bcrypt
- Flask Sessions

### Deployment

- Render
- Gunicorn

### Version Control

- Git
- GitHub

---

## 🏗️ Project Architecture

```text
Smart-Fin-AI/
│
├── app.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── home.html
│   ├── about.html
│   ├── contact.html
│   ├── login.html
│   ├── register.html
│   ├── forgot_password.html
│   └── dashboard.html
│
├── static/
│   └── ...
│
└── instance/
    └── users.db
```

### Main Components

**app.py**

Contains the main Flask application, database models, authentication routes, transaction management, dashboard logic, savings goal functionality, and password reset functionality.

**templates/**

Contains the HTML templates used to build the application's user interface.

**static/**

Contains frontend assets such as CSS, JavaScript, images, and other static resources.

**instance/**

Contains the local SQLite database used by the application.

---

## 🔄 Application Workflow

```text
User
  ↓
Registration
  ↓
Login
  ↓
Personal Dashboard
  ↓
Add Income / Expense
  ↓
Transaction Database
  ↓
Financial Calculations
  ↓
Financial Health Analysis
  ↓
Smart Financial Advice
  ↓
Savings Goal Tracking
```

---

## 📈 Financial Calculations

The application calculates important financial metrics from the user's transactions.

### Current Savings

```text
Current Savings = Total Income - Total Expenses
```

### Saving Rate

```text
Saving Rate = (Current Savings / Total Income) × 100
```

### Remaining Goal Amount

```text
Remaining Amount = Target Amount - Saved Amount
```

The dashboard uses these values to provide a simple understanding of the user's financial position.

---

## 🗄️ Database Design

The application uses SQLAlchemy ORM with SQLite.

### User

Stores user account information such as:

- Username
- Email
- Password Hash
- Monthly Income
- Primary Financial Goal

### Finance

Stores individual financial transactions such as:

- Transaction ID
- Username
- Transaction Type
- Category
- Amount
- Description
- Date

### Goal

Stores savings goal information such as:

- Goal ID
- Username
- Target Amount
- Saved Amount

The database structure allows each user to access only their own financial information.

---

## 🚀 Local Installation

### 1. Clone the repository

```bash
git clone https://github.com/priyanshi-ux/Smart-Fin-AI.git
```

### 2. Navigate into the project

```bash
cd Smart-Fin-AI
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python app.py
```

The application will be available at:

```text
http://127.0.0.1:5000
```

---

## 📦 Requirements

The project uses the following Python packages:

```text
Flask
Flask-SQLAlchemy
Flask-Bcrypt
gunicorn
```

---

## ☁️ Deployment

Smart-Fin AI has been successfully deployed using **Render**.

### Deployment Configuration

```text
Platform: Render
Environment: Python
Branch: main
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

### Live Deployment

🌐 **https://smart-fin-ai.onrender.com**

The production deployment is connected to the GitHub repository and can be updated through Git pushes.

---

## 🧪 Project Status

### ✅ Completed

- [x] User Registration
- [x] User Login
- [x] Logout
- [x] Password Hashing
- [x] Forgot Password
- [x] Transaction Management
- [x] Income Tracking
- [x] Expense Tracking
- [x] Transaction Deletion
- [x] Financial Health Score
- [x] Saving Rate Calculation
- [x] Smart Financial Advice
- [x] Savings Goal
- [x] Recent Transactions
- [x] Responsive User Interface
- [x] SQLite Database Integration
- [x] GitHub Repository
- [x] Render Deployment
- [x] Live Production Application

### 🚀 Current Status

**Project Status: COMPLETED & DEPLOYED**

The application is fully functional and available through the live Render deployment.

---

## 🎯 Future Enhancements

Possible future improvements include:

- AI-powered spending prediction
- Interactive financial analytics
- Monthly and yearly expense reports
- PDF financial reports
- Email notifications
- Advanced data visualization
- Budget planning
- Recurring transactions
- Multi-currency support
- Personalized AI financial chatbot
- Cloud database integration
- Mobile application

---

## 💼 Skills Demonstrated

This project demonstrates practical experience in:

- Python Development
- Flask Web Development
- Backend Development
- REST-style Routing
- SQLAlchemy ORM
- SQLite Database Management
- Authentication & Authorization
- Password Hashing
- CRUD Operations
- Form Validation
- Financial Data Processing
- Responsive Web Design
- Git & GitHub
- Cloud Deployment
- Render Deployment
- Full-Stack Application Development

---

## 👩‍💻 Developer

**Priyanshi Kushwaha**

### Project

**Smart-Fin AI — AI-Powered Personal Finance Advisor**

### Repository

https://github.com/priyanshi-ux/Smart-Fin-AI

### Live Demo

https://smart-fin-ai.onrender.com

---

## ⭐ Conclusion

Smart-Fin AI is designed to provide users with a simple and practical way to understand and manage their personal finances.

The project combines **Flask backend development, database management, authentication, financial calculations, responsive UI design, and cloud deployment** into a complete working web application.

🚀 **Smart-Fin AI is completely working and successfully deployed on Render.**
