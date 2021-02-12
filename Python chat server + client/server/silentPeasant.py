import time
import socket
from silentUser import silentUser
from multiprocessing import Process
from serverFunctions import sendAndEncryptMessage


class silentPeasant(silentUser):
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
            elif self.__command in peasants.keys():
                self.transfer(peasants[self.__command])
            elif self.__command in kings.keys():
                self.transfer(kings[self.__command])
            elif self.__command in gods.keys():
                self.transfer(gods[self.__command])
        # O(N) - runs as long as client is connected, not infinite, client will disconnected

    def checkIfConnected(self, privateKey, peasants, kings, gods):  # Added new contact & needs information to contact
        try:
            client = self.reader.receiveMesEnc(privateKey, self.getSocket())
        except (socket.error, ValueError):
            return
        if client in peasants.keys():
            self.sendInfoToContact(peasants[client])
        elif client in kings.keys():
            self.sendInfoToContact(kings[client])
        elif client in gods.keys():
            self.sendInfoToContact(gods[client])
        # O(1)

    def sendInfoToContact(self, targetClient):  # Send those information to client which added that user & vice versa
        while self.inUse and targetClient.inUse:  # if the client which was added didn't add back he will ignore the
            time.sleep(0.5)  # "newCon" request because that client isn't in his phonebook
        self.inUse = targetClient.inUse = True
        try:
            sendAndEncryptMessage(self.getPubKey(), "newCon", self.getSocket())
            sendAndEncryptMessage(self.getPubKey(), targetClient.getUser(), self.getSocket())
            sendAndEncryptMessage(self.getPubKey(),
                                  targetClient.getPubKey().export_key().decode('utf-8'), self.getSocket())
            sendAndEncryptMessage(targetClient.getPubKey(), "newCon", targetClient.getSocket())
            sendAndEncryptMessage(targetClient.getPubKey(), self.getUser(), targetClient.getSocket())
            sendAndEncryptMessage(targetClient.getPubKey(),
                                  self.getPubKey().export_key().decode('utf-8'), targetClient.getSocket())
            self.inUse = targetClient.inUse = False
        except (socket.error, ValueError):
            return
        # O(1)

    def run(self, privateKey, peasants, kings, gods):  # run client handler, after connection anything the client send
        proc = Process(target=self._contact, args=(privateKey, peasants, kings, gods))  # handles here
        proc.start()
        while True:
            time.sleep(3)
            try:
                self.getSocket().send(b"")
                if not proc.is_alive():
                    return
            except socket.error:
                proc.kill()
                return
        # O(infinity) ~ as long as client is still contactable
