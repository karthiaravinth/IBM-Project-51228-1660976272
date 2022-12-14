import os
import re
import pet_categories

from flask import request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
from pet_extra import convertSQLToDict

mysqldb = 'mysql+pymysql://root:root@localhost:3306/ibmsample'
engine = create_engine(mysqldb)
db = scoped_session(sessionmaker(bind=engine))

def getBudgets(userID):
    results = db.execute(
        "SELECT id, name, year, amount FROM budgets WHERE user_id = :usersID ORDER BY name ASC", {"usersID": userID}).fetchall()

    budgets_query = convertSQLToDict(results)
    if budgets_query:
        budgets = {budget['year']: [] for budget in budgets_query}
        for budget in budgets_query:
            budgets[budget['year']].append({'amount': budget['amount'], 'id': budget['id'], 'name': budget['name']})
        return budgets
    return None

def getBudgetByID(budgetID, userID):
    budget = convertSQLToDict(db.execute(
        "SELECT name, amount, year, id FROM budgets WHERE user_id = :usersID AND id = :budgetID", {"usersID": userID, "budgetID": budgetID}).fetchall())
    return budget[0]

def getTotalBudgetedByYear(userID, year=None):
    if not year:
        year = datetime.now().year

    amount = db.execute(
        "SELECT SUM(amount) AS amount FROM budgets WHERE user_id = :usersID AND year = :year", {"usersID": userID, "year": year}).fetchone()[0]

    if amount is None:
        return 0
    else:
        return amount

def generateBudgetFromForm(formData):
    budget = {"name": None, "year": None, "amount": None, "categories": []}
    counter = 0
    for key, value in formData:
        counter += 1
        if counter <= 3:
            if key == "name":
                validBudgetName = re.search("^([a-zA-Z0-9_\s\-]*)$", value)
                if validBudgetName:
                    budget[key] = value.strip()
                else:
                    return {"apology": "Please enter a budget name without special characters except underscores, spaces, and hyphens"}
            elif key == "year":
                budgetYear = int(value)
                currentYear = datetime.now().year

                if 2020 <= budgetYear <= currentYear:
                    budget[key] = budgetYear
                else:
                    return {"apology": f"Please select a valid budget year: 2020 through {currentYear}"}
            else:
                amount = float(value.strip())
                budget[key] = amount
        else:
            if value == '':
                continue

            # Need to split the key since the HTML elements are loaded dynamically and named like 'categories.1', 'categories.2', etc.
            cleanKey = key.split(".")

            # Store the category name and associated % the user wants budgetd for the category
            category = {"name": None, "percent": None}
            if cleanKey[0] == "categories":
                category["name"] = value.strip()

                # Get the percent value and convert to decimal
                percent = (int(formData[counter][1].strip()) / 100)
                category["percent"] = percent

                # Add the category to the list of categories within the dict
                budget[cleanKey[0]].append(category)
            # Pass on this field because we grab the percent above (Why? It's easier to keep these 2 lines than rewrite many lines. This is the lowest of low pri TODOs)
            elif cleanKey[0] == "categoryPercent":
                pass
            else:
                return {"apology": "Only categories and their percentage of the overall budget are allowed to be stored"}

    return budget


# Create a new budget
# Note: due to DB design, this is a 2 step process: 1) create a budget (name/year/amount) in budgets table, 2) create 1:M records in budgetCategories (budgetID + categoryID + percentAmount)
def createBudget(budget, userID):
    # Verify the budget name is not a duplicate of an existing budget
    uniqueBudgetName = isUniqueBudgetName(budget["name"], None, userID)
    if not uniqueBudgetName:
        return {"apology": "Please enter a unique budget name, not a duplicate."}

    # Insert new budget into DB
    db.execute("INSERT INTO budgets (name, year, amount, user_id) VALUES (:budgetName, :budgetYear, :budgetAmount, :usersID)",
                             {"budgetName": budget["name"], "budgetYear": budget["year"], "budgetAmount": budget["amount"], "usersID": userID})
    newBudgetID = db.execute("SELECT LAST_INSERT_ID()").fetchone()[0]
    db.commit()

    # Get category IDs from DB for the new budget
    categoryIDS = getBudgetCategoryIDS(budget["categories"], userID)

    # Insert a record for each category in the new budget
    addCategory(newBudgetID, categoryIDS)

    return budget


# When creating or updating a budget, add the spending categories and % budgeted per category to a budgets record in the DB
def addCategory(budgetID, categoryIDS):
    # Insert a record for each category in the new budget
    for categoryID in categoryIDS:
        db.execute("INSERT INTO budgetCategories (budgets_id, category_id, amount) VALUES (:budgetID, :categoryID, :percentAmount)",
                   {"budgetID": budgetID, "categoryID": categoryID["id"], "percentAmount": categoryID["amount"]})
    db.commit()


# Update an existing budget
# Note: due to DB design, this is a 3 step process: 1) update a budget (name/year/amount) in budgets table, 2) delete the existing spending categories for the budget, 3) create 1:M records in budgetCategories (budgetID + categoryID + percentAmount)
def updateBudget(oldBudgetName, budget, userID):
    # Query the DB for the budget ID
    oldBudgetID = getBudgetID(oldBudgetName, userID)

    # Verify the budget name is not a duplicate of an existing budget
    uniqueBudgetName = isUniqueBudgetName(
        budget["name"], oldBudgetID, userID)
    if not uniqueBudgetName:
        return {"apology": "Please enter a unique budget name, not a duplicate."}

    # Update the budget name, year, and amount in DB
    db.execute("UPDATE budgets SET name = :budgetName, year = :budgetYear, amount = :budgetAmount WHERE id = :oldBudgetID AND user_id = :usersID",
               {"budgetName": budget["name"], "budgetYear": budget["year"], "budgetAmount": budget["amount"], "oldBudgetID": oldBudgetID, "usersID": userID})
    db.commit()

    # Delete existing category records for the budget
    db.execute("DELETE FROM budgetCategories WHERE budgets_id = :oldBudgetID",
               {"oldBudgetID": oldBudgetID})
    db.commit()

    # Get category IDs from DB for the new budget
    categoryIDS = getBudgetCategoryIDS(budget["categories"], userID)

    # Insert a record for each category in the new budget
    addCategory(oldBudgetID, categoryIDS)

    return budget


# Get a budgets associated category ids
def getBudgetCategoryIDS(categories, userID):
    # Get the category IDs from the DB for the updated budget
    categoryIDS = []
    for category in categories:
        # Get the category ID
        categoryID = db.execute("SELECT categories.id FROM userCategories INNER JOIN categories ON userCategories.category_id = categories.id WHERE userCategories.user_id = :usersID AND categories.name = :categoryName",
                                {"usersID": userID, "categoryName": category["name"]}).fetchone()[0]

        # Store the category ID and associated percent amount into a dict
        id_amount = {"id": None, "amount": None}
        id_amount["id"] = categoryID
        id_amount["amount"] = category["percent"]

        # Add the dictionary to the list of categoryIDs
        categoryIDS.append(id_amount)

    return categoryIDS


# Delete an existing budget
def deleteBudget(budgetName, userID):
    # Query the DB for the budget ID
    budgetID = getBudgetID(budgetName, userID)

    if budgetID:
        # Delete the records for budgetCategories
        db.execute("DELETE FROM budgetCategories WHERE budgets_id = :budgetID",
                   {"budgetID": budgetID})
        db.commit()

        # Delete the budget
        db.execute("DELETE FROM budgets WHERE id = :budgetID",
                   {"budgetID": budgetID})
        db.commit()

        return budgetName
    else:
        return None


# Get budget ID from DB
def getBudgetID(budgetName, userID):
    # Query the DB for a budget ID based on the user and the supplied budget name
    budgetID = db.execute("SELECT id FROM budgets WHERE user_id = :usersID AND name = :budgetName",
                          {"usersID": userID, "budgetName": budgetName}).fetchone()[0]

    if not budgetID:
        return None
    else:
        return budgetID


# Get and return a bool based on whether or not a new/updated budget name already exists for the user
def isUniqueBudgetName(budgetName, budgetID, userID):
    if budgetID == None:
        # Verify the net-new created budget name is not already existing in the users existing budgets
        results = db.execute(
            "SELECT name FROM budgets WHERE user_id = :usersID", {"usersID": userID}).fetchall()
        existingBudgets = convertSQLToDict(results)
    else:
        # Verify the updated budget name is not already existing in the users existing budgets
        results = db.execute(
            "SELECT name FROM budgets WHERE user_id = :usersID AND NOT id = :oldBudgetID", {"usersID": userID, "oldBudgetID": budgetID}).fetchall()
        existingBudgets = convertSQLToDict(results)

    # Loop through all budgets and compare names
    isUniqueName = True
    for budget in existingBudgets:
        if budgetName.lower() == budget["name"].lower():
            isUniqueName = False
            break

    if isUniqueName:
        return True
    else:
        return False


# Generate a complete, updatable budget that includes the budget name, amount, and all categories (selected/unselected categories and % budgeted for)
def getUpdatableBudget(budget, userID):

    # Get the users library of spend categories
    categories = pet_categories.getSpendCategories(userID)

    # Get the budget's spend categories and % amount for each category
    results = db.execute("SELECT DISTINCT categories.name, budgetCategories.amount FROM budgetCategories INNER JOIN categories ON budgetCategories.category_id = categories.id INNER JOIN budgets ON budgetCategories.budgets_id = budgets.id WHERE budgets.id = :budgetsID",
                         {"budgetsID": budget["id"]}).fetchall()
    budgetCategories = convertSQLToDict(results)

    # Add 'categories' as a new key/value pair to the existing budget dict
    budget["categories"] = []

    # Populate the categories by looping through and adding all their categories
    for category in categories:
        for budgetCategory in budgetCategories:
            # Mark the category as checked/True if it exists in the budget that the user wants to update
            if category["name"] == budgetCategory["name"]:
                # Convert the percentage (decimal) into a whole integer to be consistent with UX
                amount = round(budgetCategory["amount"] * 100)
                budget["categories"].append(
                    {"name": category["name"], "amount": amount, "checked": True})
                break
        else:
            budget["categories"].append(
                {"name": category["name"], "amount": None, "checked": False})

    return budget
