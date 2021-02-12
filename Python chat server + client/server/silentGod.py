import time
import socket
from silentKing import silentKing
from serverFunctions import sendAndEncryptMessage


class silentGod(silentKing):
    def _contact(self, privateKey, peasants, kings, gods):
        while True:
            try:
                self.__command = self.reader.receiveMesEnc(privateKey, self.getSocket())
            except (socket.error, ValueError):
                continue
            if self.__command == "delMe":  # Delete myself and disconnect
                if self.deleteAndDisconnect(privateKey):
                    return
            elif self.__command == "askCon":
                self.checkIfConnected(privateKey, peasants, kings, gods)
            elif self.__command == "cngSt":  # Change a user permission status
                self.__changePermission(privateKey, peasants, kings, gods)
            elif self.__command == "gtAll":  # Create DB data xslx file send & delete file locally
                self._userGetDB()
            elif self.__command == "delOt":  # Delete other user
                self.__deleteSomeoneElse(privateKey, peasants, kings, gods)
            elif self.__command == "add":  # Add a new user to the service
                self.__addNewUserToService(privateKey)
            elif self.__command in peasants.keys():
                self.transfer(peasants[self.__command])
            elif self.__command in kings.keys():
                self.transfer(kings[self.__command])
            elif self.__command in gods.keys():
                self.transfer(gods[self.__command])
        # O(N) - runs as long as client is connected

    def __changePermission(self, privateKey, peasants, kings, gods):  # Changer other user permission level
        username = self.reader.receiveMesEnc(privateKey, self.getSocket())
        password = self.reader.receiveMesEnc(privateKey, self.getSocket())
        status = self.reader.receiveMesEnc(privateKey, self.getSocket())
        message = "User wasn't found or required status isn't possible, can't change your own permission."
        if username != self.getUser() and self.getDB().updatePermissions(username, password, status):
            message = "User " + username + " permission has changed."
            self.inUse = False
            if username in peasants:
                self.__messageAndDisconnect(peasants[username], "Permission level changed please reconnect.")
            elif username in kings:
                self.__messageAndDisconnect(kings[username], "Permission level changed please reconnect.")
            elif username in gods:
                self.__messageAndDisconnect(gods[username], "Permission level changed please reconnect.")
        while self.inUse:
            time.sleep(0.5)
        self.inUse = True
        try:
            sendAndEncryptMessage(self.getPubKey(), "serMes", self.getSocket())
            sendAndEncryptMessage(self.getPubKey(), message, self.getSocket())
        except socket.error:
            pass
        self.inUse = False
        # O(1) + semaphore

    def __messageAndDisconnect(self, user, message):  # Tell user he was disconnected
        while user.inUse:
            time.sleep(0.5)
        user.inUse = True
        try:
            sendAndEncryptMessage(user.getPubKey(), "serMes", user.getSocket())
            sendAndEncryptMessage(user.getPubKey(), message, user.getSocket())  # tell someone else he disconnected
            sendAndEncryptMessage(user.getPubKey(), "bye", user.getSocket())
        except socket.error:
            try:
                while self.inUse:
                    time.sleep(0.5)
                self.inUse = True
                sendAndEncryptMessage(self.getPubKey(), "disCon", self.getSocket())  # tell user the other user isn't
                sendAndEncryptMessage(self.getPubKey(), user.getUser(), self.getSocket())  # isn't connected
                self.inUse = False
            except socket.error:
                pass
        user.inUse = False
        # O(1) + semaphore

    def __deleteSomeoneElse(self, privateKey, peasants, kings, gods):  # Delete other user & if connected disconnect it
        username = self.reader.receiveMesEnc(privateKey, self.getSocket())
        password = self.reader.receiveMesEnc(privateKey, self.getSocket())
        message = "User was not deleted."
        if self.getUser() != username and self.getDB().delExistingUser(username, password):
            message = "User " + username + " was deleted from the service."
            if username in peasants:
                self.__messageAndDisconnect(peasants[username], "You have been denied of service.")
            elif username in kings:
                self.__messageAndDisconnect(kings[username], "You have been denied of service.")
            elif username in gods:
                self.__messageAndDisconnect(gods[username], "You have been denied of service.")
        while self.inUse:
            time.sleep(0.5)
        self.inUse = True
        try:
            sendAndEncryptMessage(self.getPubKey(), "serMes", self.getSocket())
            sendAndEncryptMessage(self.getPubKey(), message, self.getSocket())
        except socket.error:
            pass
        self.inUse = False
        # O(1) + semaphore

    def __addNewUserToService(self, privateKey):  # Adding new user to the service
        username = self.reader.receiveMesEnc(privateKey, self.getSocket())
        password = self.reader.receiveMesEnc(privateKey, self.getSocket())
        if self.getDB().addNewUser(username, password):
            message = "User been added into the service"
        else:
            message = "User wasn't added into the service"
        while self.inUse:
            time.sleep(0.5)
        self.inUse = True
        try:
            sendAndEncryptMessage(self.getPubKey(), "serMes", self.getSocket())
            sendAndEncryptMessage(self.getPubKey(), message, self.getSocket())
        except socket.error:
            pass
        self.inUse = False
        # O(1) + semaphore
