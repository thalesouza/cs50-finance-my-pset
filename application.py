import os

from cs50 import SQL
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from time import time
from sqlalchemy.sql.expression import null, update
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Remember logged user
    user_id = session["user_id"]

    # List to get TOTAL value
    sum_total = []

    stocks = db.execute("SELECT symbol, sum(shares), name, price FROM history WHERE user_id = ? GROUP BY symbol HAVING sum(shares) > 0 ORDER BY symbol", user_id)

    for stock in stocks:
        shares = stock['sum(shares)']
        symbol = stock['symbol']
        name = stock['name']
        price = lookup(symbol)['price']
        total = shares * price
        stock['name'] = name
        stock['symbol'] = symbol
        stock['sum(shares)'] = shares
        stock['price'] = price
        stock['total'] = total
        sum_total.append(total)

     # rows = db.execute("SELECT user_id, stock_symbol, stock_name, stocks_bought, price_bought, cash, timestamp, purchase_id FROM users JOIN purchases ON users.id = purchases.user_id WHERE user_id = ?", session["user_id"])
   
    av_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    cash = sum(sum_total)
    cash_total = av_cash[0]['cash'] + cash

    return render_template("index.html", stocks=stocks, av_cash=av_cash, cash_total=cash_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    stock_symbol = request.form.get("symbol")

    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Missing stock symbol")
        if not request.form.get("shares"):
            return apology("Missing shares's amount")

        read = lookup(stock_symbol)
        stock_price = read['price']
        stock_name = read['name']
        user_cash = rows[0]["cash"]
        n_shares = int(request.form.get("shares"))

        if (n_shares * stock_price) > user_cash:
            return apology("Can't afford.")
        else:
            update_cash = user_cash - (n_shares * stock_price)
            time_bought = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

            # add to history
            db.execute("INSERT INTO history (user_id, operation, symbol, name, price, shares, timestamp) VALUES(?, 'BUY', ?, ?, ?, ?, ?)", session["user_id"], stock_symbol.upper(), stock_name, stock_price, n_shares, time_bought)
            
            # add to portifolio
            # db.execute("INSERT INTO portifolio (user_id, symbol, name, shares) VALUES(?, ?, ?, ?)", session["user_id"], stock_symbol.upper(), stock_name, n_shares)
            
            # Update cash
            db.execute("UPDATE users SET cash = ? WHERE id = ?", update_cash, session["user_id"])
            
            flash(f"Bought {read['symbol']} at ${stock_price:.2f}")
            
            return redirect("/")


    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    stocks = db.execute("SELECT purchase_id, symbol, shares, price, timestamp FROM history WHERE user_id = ?", session['user_id'])


    return render_template("history.html", stocks=stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    stock_symbol = request.form.get("symbol")
    
    if request.method == "POST":

        if stock_symbol == "":
            return apology("Missing stocks's symbol")
        
        stocks = lookup(stock_symbol)

        if stocks == None:
            return apology("Symbol not found", 404)

        return render_template("quoted.html", stocks=stocks)

    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        validate_username = db.execute("SELECT username from users WHERE username = ?", request.form.get("username"))
        if not username:
            return apology("Missing username", 400)
        if not password:
            return apology("Missing password", 400)
        if confirmation != password:
            return apology("Password doesn't match", 400)
        pw = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        if len(validate_username) > 0:
            return apology("Someone is using this username", 400)

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, pw)

        # Start session
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        session['user_id'] = rows[0]['id']
        flash(f"Registered, welcome {username.upper()} !", username)
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    symbols = db.execute("SELECT symbol, sum(shares) FROM history WHERE user_id = ? GROUP BY symbol", session['user_id'])
    user = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])

    # for shares in symbols:
    #     symbol = shares['symbol']
    #     share = shares['sum(shares)']

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        SYMBOLS = []

        for row in symbols:
            SYMBOLS.append(row['symbol'])

        if symbol not in SYMBOLS:
            return apology("You don't have this stock.")
        if not shares:
            return apology("I can't figure how many shares want.")
        stock_shares = db.execute("SELECT sum(shares) FROM history WHERE symbol = ? AND user_id = ?", symbol, session['user_id'])
        if int(shares) > stock_shares[0]['sum(shares)']:
            return apology("You don't have this amount.")

        read = lookup(symbol)
        stock_name = read['name']
        price = read['price']
        sell_amount = price * float(shares)
        update_cash = user[0]['cash'] + float(sell_amount)
        update_share = -abs(int(shares))
        time_operation = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        # Insert into history table the sell operation
        db.execute("INSERT INTO history (user_id, operation, symbol, name, price, shares, timestamp) VALUES (?, 'SELL', ?, ?, ?, ?, ?)", session['user_id'], symbol, stock_name, price, update_share, time_operation)

        # Updates user cash after sell.
        db.execute("UPDATE users SET cash = ? WHERE id = ?", update_cash, session['user_id'])

        flash(f"Sold {symbol} at ${price:.2f}")
        SYMBOLS.clear()
        return redirect("/")

    return render_template("sell.html", symbols=symbols)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
