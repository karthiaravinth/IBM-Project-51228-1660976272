import urllib.parse
import decimal

from flask import redirect, render_template, request, session
from functools import wraps

def apology(message, code=400):
    def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"), ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def usd(value):
    return f"₹{value:,.2f}"

def convertSQLToDict(listOfRowProxy):
    rows = [dict(row) for row in listOfRowProxy]
    for row in rows:
        for column in row:
            if type(row[column]) is decimal.Decimal:
                row[column] = float(row[column])
            elif type(row[column]) is memoryview:
                row[column] = bytes(row[column])
    return rows
