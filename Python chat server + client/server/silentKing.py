import os
import time
import socket
from silentPeasant import silentPeasant
from serverFunctions import sendAndEncryptMessage, sendFile


class silentKing(silentPeasant):
    def _contact(self, privateKey, peasants, kings, gods):
        while True:
            try:
                self.__command = self.reader.receiveMesEnc(privateKey, self.getSocket())
            except (socket.error, ValueError):
                continue
            if self.__command == "delMe":
                if self.deleteAndDisconnect(privateKey):
                    return
            elif self.__command == "askCon":
                self.checkIfConnected(privateKey, peasants, kings, gods)
            elif self.__command == "gtAll":
                self._userGetDB()
            elif self.__command in peasants.keys():
                self.transfer(peasants[self.__command])
            elif self.__command in kings.keys():
                self.transfer(kings[self.__command])
            elif self.__command in gods.keys():
                self.transfer(gods[self.__command])
        # O(N) - runs as long as client is connected

    def _userGetDB(self):  # create xlsx with DB information file & send the file to the user
        fileNameAndPath = "clients.xlsx"
        self.getDB().getAll(fileNameAndPath)
        file = open(fileNameAndPath, "rb")
        binaryFile = file.read()
        file.close()
        os.remove(fileNameAndPath)
        while self.inUse:
            time.sleep(0.5)
        self.inUse = True
        try:
            sendAndEncryptMessage(self.getPubKey(), "file", self.getSocket())
            sendAndEncryptMessage(self.getPubKey(), fileNameAndPath, self.getSocket())
            sendFile(self.getPubKey(), binaryFile, self.getSocket())
        except socket.error:
            pass
        self.inUse = False
        # O(1) + semaphore
