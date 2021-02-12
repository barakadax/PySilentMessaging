import re
import xlsxwriter
from getpass import getpass
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, TEXT, Column, SMALLINT


class CLIDBHandler:
    __db = create_engine("postgresql+psycopg2://postgres:1234@localhost:5432/postgres")
    __base = declarative_base()
    __base.metadata.create_all(__db)
    __Session = sessionmaker(__db)
    __session = __Session()
    #O(1)

    def __init__(self):
        self.__regexUsernameAndPassword = "^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*[;\"\'])\S{7,}$"
        self.__regexPermission = "^(?=.*[0-2])\S{1,}$"
        #O(1)

    class __userObj(__base):
        __tablename__ = 'silentUsers'
        Username = Column(TEXT, primary_key=True, nullable=False)
        Password = Column(TEXT, primary_key=False, nullable=False)
        PermissionLevel = Column(SMALLINT, primary_key=False, nullable=False)
        #O(1)

    def __getUsername(self):
        while True:
            print(">>> Username: ", end='')
            username = input()
            if re.search(self.__regexUsernameAndPassword, username) is not None:
                return username
            print("<<< Incorrect input, please try again.")
            #O(N)

    def __getPassword(self):
        while True:
            print(">>> ", end='')
            password = getpass()
            if re.search(self.__regexUsernameAndPassword, password) is not None:
                return password
            print("<<< Incorrect input, please try again.")
            #O(N)

    def __getPermission(self):
        while True:
            print(">>> Permission level: ", end='')
            permission = input()
            if re.search(self.__regexPermission, permission) is not None:
                return permission
            print("<<< Incorrect input, please try again.")
            #O(N)

    def adminLogin(self):
        username = self.__getUsername()
        password = self.__getPassword()
        self.__Session = sessionmaker(self.__db)
        self.__session = self.__Session()
        adminUser = self.__session.query(self.__userObj).filter(
            self.__userObj.Username == username, self.__userObj.Password == password,
            self.__userObj.PermissionLevel == 2)
        self.__session.close()
        if adminUser.count() == 1:
            return True
        return False
        # O(1)

    def getUserInfo(self):
        username = self.__getUsername()
        self.__Session = sessionmaker(self.__db)
        self.__session = self.__Session()
        user = self.__session.query(self.__userObj).filter(self.__userObj.Username == username)
        self.__session.close()
        if user.count() == 1:
            return user[0]
        return None
        # O(1)

    def updateUserPermissions(self):
        userToUpdate = self.getUserInfo()
        if userToUpdate is None:
            return "<<< User wasn't found."
        permission = self.__getPermission()
        self.__Session = sessionmaker(self.__db)
        self.__session = self.__Session()
        userToUpdate = self.__session.query(self.__userObj).filter(self.__userObj.Username == userToUpdate.Username)
        userToUpdate[0].PermissionLevel = int(permission)
        self.__session.commit()
        self.__session.close()
        return "<<< User permission has changed."
        # O(1)

    def saveDBasXlsxFile(self, fileNameAndPath):
        self.__Session = sessionmaker(self.__db)
        self.__session = self.__Session()
        workbook = xlsxwriter.Workbook(fileNameAndPath)
        worksheet = workbook.add_worksheet("users")
        bold = workbook.add_format({'bold': True})
        worksheet.write('A1', 'Username', bold)
        worksheet.write('B1', 'Password', bold)
        worksheet.write('C1', 'Permission level', bold)
        rowCounter = 2
        for User in self.__session.query(self.__userObj):
            worksheet.write('A' + rowCounter.__str__(), User.Username)
            worksheet.write('B' + rowCounter.__str__(), User.Password)
            worksheet.write('C' + rowCounter.__str__(), User.PermissionLevel)
            rowCounter += 1
        workbook.close()
        self.__session.close()
        return "<<< check your desktop"
        # O(N)

    def delExistingUser(self):
        userToDelete = self.getUserInfo()
        if userToDelete is None:
            return "<<< User wasn't found."
        password = self.__getPassword()
        if password != userToDelete.Password:
            return "<<< Incorrect password for this user."
        self.__Session = sessionmaker(self.__db)
        self.__session = self.__Session()
        userToDelete = self.__session.query(self.__userObj).filter(self.__userObj.Username == userToDelete.Username)
        userName = userToDelete[0].Username
        self.__session.delete(userToDelete[0])
        self.__session.commit()
        self.__session.close()
        return f'<<< User {userName} has been deleted.'
        # O(1)

    def addNewUser(self):
        username = self.__getUsername()
        password = self.__getPassword()
        self.__Session = sessionmaker(self.__db)
        self.__session = self.__Session()
        isUserExists = self.__session.query(self.__userObj).filter(self.__userObj.Username == username)
        if isUserExists.count() == 0:
            newUser = self.__userObj(Username=username, Password=password, PermissionLevel=0)
            self.__session.add(newUser)
            self.__session.commit()
            self.__session.close()
            return "<<< User had been added into the service."
        self.__session.close()
        return "<<< Couldn't add user, the user already exists in the service."
        # O(1)

    def countAmountOfClients(self):
        self.__Session = sessionmaker(self.__db)
        self.__session = self.__Session()
        amountOfUsers = self.__session.query(self.__userObj)
        self.__session.close()
        return amountOfUsers.count()
        # O(1)
