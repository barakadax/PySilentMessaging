__author__ = "Barak Taya"
__credits__ = ["Saar *****", "Lee *********", "Matan *********", "Koren ********", "Ron ******"]
__license__ = "GNU Affero General Public License v3.0"
__version__ = "1"
__maintainer__ = "Barak Taya"
__email__ = "barakadax@gmail.com"

import re
import os
from os import path
from server import server
from multiprocessing import Process
from cliDBHandler import CLIDBHandler


def login(DBHandlerObject):
    print("<<< LOGIN")
    for amountOfTries in range(3):
        if DBHandlerObject.adminLogin():
            os.system('cls' if os.name == 'nt' else 'clear')
            return False
        print("<<< USERNAME AND/OR PASSWORD INCORRECT.")
    os.system('cls' if os.name == 'nt' else 'clear')
    os.remove("server.py")
    print("<<< Too many tries for login, service denied.")
    return True
    # O(1)


def banServiceFromRunning():
    if not path.exists("server.py"):
        print("illegal activity was found, contact barakadax@gmail.com for farther information")
        return True
    return False
    # O(1)


def guide():
    amountOfSpace = "   " * 4
    guideText = "<<< OPTIONS:\n<<<" + amountOfSpace + \
                "find - enter a user username & receive that user password & permission level.\n<<<" + amountOfSpace + \
                "change status options to write: cngSt, change status.\n<<<" + amountOfSpace + \
                "cngSt - enter a user username & new permission level to update.\n<<<" + amountOfSpace + \
                "Getting all users options to write: gtAll, get all, get users, print all.\n<<<" + amountOfSpace + \
                "gtAll - saves whole users information in xlsx file on your desktop.\n<<<" + amountOfSpace + \
                "delete user options to write: del, delete.\n<<<" + amountOfSpace + \
                "del - enter desired user to delete username & password.\n<<<" + amountOfSpace + \
                "add - enter username & password to create new user (created with lowest permission level)."
    return guideText
    # O(1)


def printSpecificUser(DBHandlerObject):
    searchedUser = DBHandlerObject.getUserInfo()
    if searchedUser is not None:
        return "<<< Username: " + str(searchedUser.Username) + " Password: " + str(searchedUser.Password) + \
               " Permission level " + str(searchedUser.PermissionLevel) + "."
    return "<<< User wasn't found."
    # O(1)


def firstTimeRun():
    if not path.exists("common.txt"):
        createDNSFile()
        print("<<< Please make sure you did every step on the firstRun.info file.")
        DBHandlerObject = CLIDBHandler()
        if DBHandlerObject.countAmountOfClients() != 0:
            print("<<< Something is wrong, please check your DB & firewall.")
            return True
        else:
            print(DBHandlerObject.addNewUser())
    return False
    # O(1)


def createDNSFile():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("<<< Please write down your DNS address, if you write it wrong the server won't run!.")
    DNSFile = open("common.txt", "wb")
    DNSAddress = ""
    DNSRegex = "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*" + \
               "([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
    while len(DNSAdrress) == 0 or re.search(DNSRegex, DNSAddress) is None:
        print(">>> address: ", end='')
        DNSAddress = input().strip()
        if len(DNSAdrress) == 0 or re.search(DNSRegex, DNSAddress) is None:
            print("<<< ERROR, please type a valid DNS.")
    DNSFile.write(bytes(DNSAddress, "utf-8"))
    DNSFile.close()
    #O(N)


def runCommand(DBHandlerObject, actionToTake):
    desktopPathAndFile = f'C:\\Users\\{os.getlogin()}\\Desktop\\clients.xlsx' \
        if os.name == 'nt' else f'/home/{os.getlogin()}/Desktop/clients.xlsx'
    if actionToTake.lower() in ["help", "guide", "-h", "-g", "h", "g", "?", "man"]:
        return guide()
    elif actionToTake.lower() == "find":
        return printSpecificUser(DBHandlerObject)
    elif actionToTake.lower() in ["change status", "cngst"]:
        return DBHandlerObject.updateUserPermissions()
    elif actionToTake.lower() in ["get users", "print all", "gtall", "get all"]:
        return DBHandlerObject.saveDBasXlsxFile(desktopPathAndFile)
    elif actionToTake.lower() in ["delete", "del"]:
        return DBHandlerObject.delExistingUser()
    elif actionToTake.lower() == "add":
        return DBHandlerObject.addNewUser()
    return "<<< Command was not found, if need help please type \"help\"."
    # O(1)


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("<<<SERVER>>>")
    if banServiceFromRunning() or firstTimeRun():
        exit(1)
    DBHandlerObject = CLIDBHandler()
    if login(DBHandlerObject):
        exit(1)
    os.system('cls' if os.name == 'nt' else 'clear')
    silentMessagesServer = server(port=1234, amountOfUsersAllow=3000)
    serverThread = Process(target=silentMessagesServer.run)
    serverThread.start()
    while path.exists("server.py"):
        for amountOfActionAllowed in range(3):
            print(">>> ", end='')
            actionToTake = input()
            print(runCommand(DBHandlerObject, actionToTake))
        if login(DBHandlerObject):
            serverThread.kill()
            exit(1)
    # O(∞)


if __name__ == "__main__":
    main()
    # O(1)
