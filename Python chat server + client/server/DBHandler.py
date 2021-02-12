import re
import time
import xlsxwriter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, SMALLINT, TEXT
from sqlalchemy.ext.declarative import declarative_base


class DBHandler:
    __db = create_engine("postgresql+psycopg2://postgres:1234@localhost:5432/postgres")
    __base = declarative_base()
    __base.metadata.create_all(__db)
    __Session = sessionmaker(__db)
    __session = __Session()
    #O(1)

    def __init__(self):
        self.__FuncInUse = False
        self.__regexUsernameAndPassword = "^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*[;\"\'])\S{7,}$"
        self.__regexPermission = "^(?=.*[0-2])\S{1}$"
        #O(1)

    class __servicePersonal(__base):
        __tablename__ = 'silentUsers'
        Username = Column(TEXT, primary_key=True, nullable=False)
        Password = Column(TEXT, primary_key=False, nullable=False)
        PermissionLevel = Column(SMALLINT, primary_key=False, nullable=False)

    def isExists(self, username, password):  # Returns the user if exists in the DB otherwise returns False
        if re.search(self.__regexUsernameAndPassword, username) is None or \
                re.search(self.__regexUsernameAndPassword, password) is None:
            return True, False
        target = self.__session.query(self.__servicePersonal).filter(
            self.__servicePersonal.Username == username, self.__servicePersonal.Password == password)
        if target.count() == 1:
            return False, target[0]
        return True, False
        # O(1)

    def addNewUser(self, username, password):  # Adds new User to the DB only if none exists in the DB
        if re.search(self.__regexUsernameAndPassword, username) is None or \
                re.search(self.__regexUsernameAndPassword, password) is None:
            return False
        self.__Session = sessionmaker(self.__db)
        self.__session = self.__Session()
        status, _ = self.isExists(username, password)
        if status:
            newUser = self.__servicePersonal(Username=username, Password=password, PermissionLevel=0)
            self.__session.add(newUser)
            self.__session.commit()
            self.__session.close()
            return True
        self.__session.close()
        return False
        # O(1)

    def delExistingUser(self, username, password):  # Deletes a user only if exists in the DB
        if re.search(self.__regexUsernameAndPassword, username) is None or \
                re.search(self.__regexUsernameAndPassword, password) is None:
            return False
        self.__Session = sessionmaker(self.__db)
        self.__session = self.__Session()
        _, target = self.isExists(username, password)
        if target:
            self.__session.delete(target)
            self.__session.commit()
            self.__session.close()
            return True
        self.__session.close()
        return False
        # O(1)

    def getAll(self, fileNameAndPath):  # Creates xlsx file with all the DB users info under the name 'clients.xlsx'
        while self.__FuncInUse:
            time.sleep(0.5)
        self.__FuncInUse = True
        self.__Session = sessionmaker(self.__db)
        self.__session = self.__Session()
        workbook = xlsxwriter.Workbook(fileNameAndPath)
        worksheet = workbook.add_worksheet("users")
        bold = workbook.add_format({'bold': True})
        worksheet.write('A1', 'Username', bold)
        worksheet.write('B1', 'Password', bold)
        rowCounter = 2
        for User in self.__session.query(self.__servicePersonal):
            worksheet.write('A' + rowCounter.__str__(), User.Username)
            worksheet.write('B' + rowCounter.__str__(), User.Password)
            rowCounter += 1
        workbook.close()
        self.__FuncInUse = False
        self.__session.close()
        # O(N) + semaphore

    def updatePermissions(self, username, password, newLevel):  # Update existing user permission level
        if re.search(self.__regexUsernameAndPassword, username) is None or \
                re.search(self.__regexUsernameAndPassword, password) is None or \
                re.search(self.__regexPermission, newLevel) is None:
            return False
        self.__Session = sessionmaker(self.__db)
        self.__session = self.__Session()
        _, target = self.isExists(username, password)
        if target:
            target.PermissionLevel = int(newLevel)
            self.__session.commit()
            self.__session.close()
            return True
        self.__session.close()
        return False
        # O(1)
