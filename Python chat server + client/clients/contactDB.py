import re
from sqlite3 import connect  # Auto close connection when function dies


def addContact(username):  # Add new contact into the phonebook
    sqlInjectionProtect = "^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*[;\"\'])\S{7,}$"
    if re.search(sqlInjectionProtect, username) is None:
        return "Invalid input"
    try:
        with connect(r"contactBook.db") as con:
            con.execute(f"INSERT INTO contacts(name) SELECT \'{username}\' WHERE NOT EXISTS(SELECT * FROM contacts " +
                        f"WHERE name = \'{username}\')")
            return "Added."
    except ValueError:
        return "Couldn't add."
    #O(N)


def getContacts(username):  # Returns all contacts in 1 string separated with space
    sqlInjectionProtect = "^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*[;\"\'])\S{7,}$"
    if re.search(sqlInjectionProtect, username) is None:
        return ""
    try:
        with connect(r"contactBook.db") as con:
            contacts = con.execute(f"SELECT * FROM contacts WHERE name != \'{username}\'")
            allMyContacts = ""
            for friend in contacts:
                allMyContacts += friend[0] + " "
            return allMyContacts[0:-1]
    except ValueError:
        return ""
    #O(N)


def deleteContact(username):  # Delete contact from the phonebook, if contact none existence nothing changes
    sqlInjectionProtect = "^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*[;\"\'])\S{7,}$"
    if re.search(sqlInjectionProtect, username) is None:
        return
    try:
        with connect(r"contactBook.db") as con:
            con.execute(f"DELETE FROM contacts WHERE name = \'{username}\'")
    except ValueError:
        pass
    #O(1)


def isThereContactNamed(name):  # Check if contact already exists in the phonebook
    sqlInjectionProtect = "^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*[;\"\'])\S{7,}$"
    if re.search(sqlInjectionProtect, name) is None:
        return "Invalid input"
    try:
        with connect(r"contactBook.db") as con:
            isThere = con.execute(f"SELECT * FROM contacts WHERE name = \'{name}\'")
            if isThere.fetchone() is not None:
                return True
            return False
    except ValueError:
        return False
    # O(1)
