from flask import Flask, jsonify, request, render_template, session, redirect
from flask_cors import CORS
import bcrypt
from db import get_db_connection

# ---------------------------------
# APP SETUP
# ---------------------------------
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "super-secret-key"
CORS(app, supports_credentials=True)

# ---------------------------------
# FRONTEND ROUTES
# ---------------------------------

@app.route("/")
def root():
    return redirect("/login")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/dashboard")
def dashboard_page():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("dashboard.html")


@app.route("/account")
def account_page():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("account.html")


@app.route("/deposit")
def deposit_page():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("deposit.html")


@app.route("/fund-transfer")
def fund_transfer_page():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("fundtransfer.html")


@app.route("/transactions")
def transaction_page():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("transaction-history.html")


@app.route("/deactivate")
def deactivate_page():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("deactivate.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------------------------
# AUTH API
# ---------------------------------

@app.route("/api/login", methods=["POST"])
def login_user():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email=%s", (data["email"],))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user and bcrypt.checkpw(
        data["password"].encode(),
        user["password_hash"].encode()
    ):
        session["user_id"] = user["user_id"]
        session["full_name"] = user["full_name"]

        return jsonify({
            "user_id": user["user_id"],
            "full_name": user["full_name"]
        }), 200

    return jsonify({"error": "Invalid credentials"}), 401


# ---------------------------------
# ACCOUNTS API
# ---------------------------------

@app.route("/api/accounts")
def get_accounts():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT account_id, account_type, balance, status
        FROM accounts
        WHERE user_id=%s
        ORDER BY account_id ASC
    """, (session["user_id"],))

    accounts = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({"accounts": accounts}), 200


@app.route("/api/account/create", methods=["POST"])
def create_account():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    account_type = request.json.get("account_type")
    if account_type not in ["Savings", "Current"]:
        return jsonify({"error": "Invalid account type"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO accounts (user_id, account_type, balance, status)
        VALUES (%s, %s, 0.00, 'ACTIVE')
    """, (session["user_id"], account_type))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Account created successfully"}), 201


# ---------------------------------
# DEPOSIT API (FIXED)
# ---------------------------------

@app.route("/api/account/deposit", methods=["POST"])
def deposit_money():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    account_id = request.json.get("account_id")
    amount = float(request.json.get("amount", 0))

    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE accounts
        SET balance = balance + %s
        WHERE account_id=%s AND user_id=%s AND status='ACTIVE'
    """, (amount, account_id, session["user_id"]))

    if cursor.rowcount == 0:
        return jsonify({"error": "Account not found or blocked"}), 400

    cursor.execute("""
        INSERT INTO transactions (to_account, amount, transaction_type)
        VALUES (%s, %s, 'deposit')
    """, (account_id, amount))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Deposit successful"}), 200


# ---------------------------------
# FUND TRANSFER API (FIXED)
# ---------------------------------

@app.route("/api/account/transfer", methods=["POST"])
def fund_transfer():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    from_acc = data.get("from_account")
    to_acc = data.get("to_account")
    amount = float(data.get("amount", 0))

    if not from_acc or not to_acc or amount <= 0:
        return jsonify({"error": "Invalid input"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT balance
        FROM accounts
        WHERE account_id=%s AND user_id=%s AND status='ACTIVE'
    """, (from_acc, session["user_id"]))

    row = cursor.fetchone()
    if not row or row[0] < amount:
        return jsonify({"error": "Insufficient balance"}), 400

    cursor.execute(
        "UPDATE accounts SET balance = balance - %s WHERE account_id=%s",
        (amount, from_acc)
    )
    cursor.execute(
        "UPDATE accounts SET balance = balance + %s WHERE account_id=%s",
        (amount, to_acc)
    )

    cursor.execute("""
        INSERT INTO transactions (from_account, to_account, amount, transaction_type)
        VALUES (%s, %s, %s, 'transfer')
    """, (from_acc, to_acc, amount))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Transfer successful"}), 200


# ---------------------------------
# DEACTIVATE ACCOUNT API (FIXED)
# ---------------------------------

@app.route("/api/account/deactivate", methods=["POST"])
def deactivate_account():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    account_id = request.json.get("account_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE accounts
        SET status='BLOCKED'
        WHERE account_id=%s AND user_id=%s
    """, (account_id, session["user_id"]))

    if cursor.rowcount == 0:
        return jsonify({"error": "Account not found"}), 404

    conn.commit()
    cursorurs = None
    cursor.close()
    conn.close()

    return jsonify({"message": "Account deactivated successfully"}), 200


# ---------------------------------
# TRANSACTION HISTORY API (FINAL FIX)
# ---------------------------------

@app.route("/api/account/<int:account_id>/transactions")
def transaction_history(account_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT account_id
        FROM accounts
        WHERE account_id=%s AND user_id=%s
    """, (account_id, session["user_id"]))

    if not cursor.fetchone():
        return jsonify({"error": "Invalid account"}), 403

    cursor.execute("""
        SELECT
            transaction_type,
            amount,
            DATE_FORMAT(created_at, '%d-%m-%Y %h:%i %p') AS created_at
        FROM transactions
        WHERE from_account=%s OR to_account=%s
        ORDER BY created_at DESC
    """, (account_id, account_id))

    transactions = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({"transactions": transactions}), 200


# ---------------------------------
# RUN SERVER
# ---------------------------------
if __name__ == "__main__":
    app.run(debug=True)
