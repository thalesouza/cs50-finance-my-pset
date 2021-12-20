# CS50 Finance

![Portfolio](https://i.imgur.com/CSfTwO2.png)

## Introduction

CS50 Finance was the problem set from Week 9 of Harvard CS50 — Introduction to Computer Science.
You can learn more about [here](https://cs50.harvard.edu/x/2021/).

The proposal of this exercise was:
* Complete the implementation of **[register](#register)**
* Complete the implementation of **[quote](#quote)**
* Complete the implementation of **[buy](#buy)**
* Complete the implementation of **[index](#index)**
* Complete the implementation of **[sell](#sell)**
* Complete the implementation of **[history](#history)**

### Register
> Require that a user input a username, rendering an apology if it's empty or username already exists

> Require user input a password and a confirmation, rendering an apology if it's blank or doesn't match.

>Submit via POST to `/register`

>Insert into table `users` storing a hash of the user's password 
### Quote
>Require that user input a stock's symbol and submit via POST to /quote
### Buy
> Require user input a stock's symbol, rendering if it's blank or symbol doesn't exist.

>Require user input a number of shares, rendering an apology if the input is not a positive integer.

> Submit via POST to `/buy`

> Render apology if user cannot afford.

> Return to `index` page if success
### Index
> Displays an HTML table summarizing, for the user logged in, which stocks the user owns, the numbers of shares owned, the current price of each stock, and the total value of each holding. Also display the user’s current cash balance along with a grand total
### Sell
> Require that a user input a stock’s symbol, implemented as a select menu whose name is symbol. Render an apology if the user fails to select a stock or if (somehow, once submitted) the user does not own any shares of that stock.

>Require that a user input a number of shares, implemented as a field whose name is shares. Render an apology if the input is not a positive integer or if the user does not own that many shares of the stock.

> Submit the user’s input via *POST* to `/sell`.

> When a sale is complete, redirect the user back to the index page.

### History
> Complete the implementation of history in such a way that it displays an HTML table summarizing all of a user’s transactions ever, listing row by row each and every buy and every sell.

# **Stack used**
This application was created with HTML, CSS + [Bootstrap](https://getbootstrap.com/) and Python, using [Flask](https://flask.palletsprojects.com/en/2.0.x/) as framework, and SQLite for database.

Also all the data is provided by [IEX](https://iextrading.com/developer), using their API to get stocks current price, it's name and symbol.

# **In production**
You can access this application at [cs50finance.uaicode.com](https://cs50finance.uaicode.com) // SOON

# **RUN**
## How to run:
**[Python3](https://docs.python.org/3/)** and **[pip](https://pip.pypa.io/en/stable/installation/)** are needed to run in your machine.

`sudo apt install python`

`sudo apt install python3-pip `

### **I strongly suggest that you create a virtual environment to test.**

`cd cs50-finance-my-pset`

`sudo apt install python3-venv`

To run the `venv`:

`python3 -m venv .venv`

To start your virtual env:

`source /.venv/bin/activate `

### With you virtual env set, install the project's dependencies.
`pip3 install -r requirements.txt`

Remember to redefine FLASK_APP to

`export FLASK_APP=application.py`

and export your API_KEY

`export API_KEY=token`

## If everything is correct
`flask run`