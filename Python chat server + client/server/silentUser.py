import abc
import time
import socket
from Crypto.PublicKey import RSA
from serverFunctions import transferSendMes, sendAndEncryptMessage


class silentUser(abc.ABC):
    def __init__(self, mySocket, name, reader, myKey, dhHandler):
        self.inUse = False
        self.reader = reader
        self.__pubKey = myKey
        self.__command = None
        self.__DB = dhHandler
        self.__socket = mySocket
        self.__username = name

    def getUser(self):
        return self.__username
        # O(1)

    def getSocket(self):
        return self.__socket
        # O(1)

    def getPubKey(self):
        return RSA.import_key(self.__pubKey)
        # O(1)

    def getDB(self):
        return self.__DB
        # O(1)

    def _contact(self, privateKey, peasants, kings, gods):
        raise NotImplementedError()
        # O(Unknown)

    def run(self, privateKey, peasants, kings, gods):
        raise NotImplementedError()
        # O(Unknown)

    def deleteAndDisconnect(self, privateKey):
        username = self.reader.receiveMesEnc(privateKey, self.getSocket())
        password = self.reader.receiveMesEnc(privateKey, self.getSocket())
        if self.getUser() == username:
            self.getDB().delExistingUser(username, password)
            self.getSocket().close()
            return True
        return False
        # O(1)

    def transfer(self, sendTo):
        while sendTo.inUse:
            time.sleep(0.5)
        sendTo.inUse = True
        try:
            sendAndEncryptMessage(sendTo.getPubKey(), self.getUser(), sendTo.getSocket())
            transferSendMes(self.reader.transferReceiveMes(self.getSocket()), sendTo.getSocket())
            sendTo.inUse = False
        except socket.error:
            sendTo.inUse = False
            while self.inUse:
                time.sleep(0.5)
            self.inUse = True
            try:
                sendAndEncryptMessage(self.getPubKey(), "disCon", self.getSocket())
                sendAndEncryptMessage(self.getPubKey(), sendTo.getUser(), self.getSocket())
            except socket.error:
                pass
            self.inUse = False
        # O(1) + semaphore
