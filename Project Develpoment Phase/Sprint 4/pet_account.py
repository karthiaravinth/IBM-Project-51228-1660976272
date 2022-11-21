import os

from flask import request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from pet_extra import convertSQLToDict

# Create engine object to manage connections to DB, and scoped session to separate user interactions with DB
mysqldb = 'mysql+pymysql://root:root@localhost:3306/ibmsample'
engine = create_engine(mysqldb)
db = scoped_session(sessionmaker(bind=engine))


# Get the users account name
def getUsername(userID):
    return  db.execute("SELECT username FROM users WHERE id = :usersID", {"usersID": userID}).fetchone()[0]

def getIncome(userID):
    return float(db.execute( "SELECT income FROM users WHERE id = :usersID", {"usersID": userID}).fetchone()[0])

def updateIncome(income, userID):
    rows = db.execute("UPDATE users SET income = :newIncome WHERE id = :usersID", {"newIncome": income, "usersID": userID}).rowcount
    db.commit()

    if rows != 1:
        return {"apology": "Sorry, Update Income Error. Try again!"}
    else:
        return rows

def getPayers(userID):
    return convertSQLToDict(db.execute("SELECT name FROM payers WHERE user_id = :usersID ORDER BY name ASC", {"usersID": userID}).fetchall()) # payers

def addPayer(name, userID):
    # Make sure the user has no more than 5 payers (6 w/ default 'Self') (note: this max amount is arbitrary, 5 sounded good ¯\_(ツ)_/¯.
    # Also note that the payers report charts have 5 hardcoded color pallettes that will need to be updated if the max number of payers is changed in the future)
    if getTotalPayers(userID) >= 5:
        return {"apology": "You have the maximum number of payers. Try deleting one you aren't using or contact the admin."}

    if payerExistsForUser(name, userID):
        return {"apology": "You already have a payer with that name. Enter a new, unique name."}
    else:
        row = db.execute("INSERT INTO payers (user_id, name) VALUES (:usersID, :name)", {"usersID": userID, "name": name}).rowcount
        db.commit()
        return row

def renamePayer(existingName, newName, userID):
    if not payerExistsForUser(existingName, userID):
        return {"apology": "The payer you're trying to rename does not exist."}

    if payerExistsForUser(newName, userID):
        return {"apology": "You already have a payer with that name. Enter a new, unique name."}

    db.execute("UPDATE expenses SET payer = :name WHERE user_id = :usersID AND payer = :oldName",{"name": newName, "usersID": userID, "oldName": existingName})
    db.commit()

    rows = db.execute("UPDATE payers SET name = :name WHERE user_id = :usersID AND name = :oldName", {"name": newName, "usersID": userID, "oldName": existingName}).rowcount
    db.commit()

    if rows != 1:
        return {"apology": "Sorry, Rename Payer is having problems. Try again!"}
    else:
        return rows

def deletePayer(name, userID):
    if not payerExistsForUser(name, userID):
        return {"apology": "The payer you're trying to delete does not exist."}

    rows = db.execute("DELETE FROM payers WHERE name = :name AND user_id = :usersID",
                      {"name": name, "usersID": userID}).rowcount
    db.commit()

    if rows != 1:
        return {"apology": "Sorry, Delete payer isn't working for some reason. Try again!"}
    else:
        return rows

def updatePassword(oldPass, newPass, userID):
    userHash = db.execute(
        "SELECT hash FROM users WHERE id = :usersID", {"usersID": userID}).fetchone()[0]
    if not check_password_hash(userHash, oldPass):
        return {"apology": "invalid password"}

    hashedPass = generate_password_hash(newPass)

    rows = db.execute("UPDATE users SET hash = :hashedPass WHERE id = :usersID",
                      {"hashedPass": hashedPass, "usersID": userID}).rowcount
    db.commit()

    if rows != 1:
        return {"apology": "Sorry, Update Password is having issues. Try again!"}
    else:
        return rows

def payerExistsForUser(payerName, userID):
    if payerName.lower() == 'self':
        return True

    count = db.execute(
        "SELECT COUNT(*) AS count FROM payers WHERE user_id = :usersID AND LOWER(name) = :name", {"usersID": userID, "name": payerName.lower()}).fetchone()[0]

    if count > 0:
        return True
    else:
        return False

def getStatistics(userID):
    stats = {"registerDate": None, "totalExpenses": None,
             "totalBudgets": None, "totalCategories": None, "totalPayers": None}
    registerDate = db.execute(
        "SELECT registerDate FROM users WHERE id = :usersID", {"usersID": userID}).fetchone()[0]
    stats["registerDate"] = registerDate.split()[0]

    totalExpenses = db.execute(
        "SELECT COUNT(*) AS count FROM expenses WHERE user_id = :usersID", {"usersID": userID}).fetchone()[0]
    stats["totalExpenses"] = totalExpenses

    totalBudgets = db.execute(
        "SELECT COUNT(*) AS count FROM budgets WHERE user_id = :usersID", {"usersID": userID}).fetchone()[0]
    stats["totalBudgets"] = totalBudgets

    totalCategories = db.execute(
        "SELECT COUNT(*) AS count FROM userCategories INNER JOIN categories ON userCategories.category_id = categories.id WHERE userCategories.user_id = :usersID",
        {"usersID": userID}).fetchone()[0]
    stats["totalCategories"] = totalCategories
    stats["totalPayers"] = getTotalPayers(userID)
    return stats

def getTotalPayers(userID):
    count = db.execute(
        "SELECT COUNT(*) AS count FROM payers WHERE user_id = :usersID", {"usersID": userID}).fetchone()[0]
    return count

def getAllUserInfo(userID):
    user = {"name": None, "income": None, "payers": None, "stats": None}
    user["name"] = getUsername(userID)
    user["income"] = getIncome(userID)
    user["payers"] = getPayers(userID)
    user["stats"] = getStatistics(userID)
    return user
