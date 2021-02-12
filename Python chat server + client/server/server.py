import socket
import datetime
from DBHandler import DBHandler
from silentGod import silentGod
from Crypto.PublicKey import RSA
from silentKing import silentKing
from silentPeasant import silentPeasant
from multiprocessing import Process, Manager
from serverFunctions import getCommonValue, sendMes, hide, getKeys, sendAndEncryptMessage, randomPrivate, receiver


class server(object):
    def __init__(self, port, amountOfUsersAllow):
        self.threads = {}
        self.DBUsage = DBHandler()
        self.gods = Manager().dict()
        self.kings = Manager().dict()
        self.peasants = Manager().dict()
        self.username = ""
        self.password = ""
        self.address = None
        self.clientSocket = None
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind(('0.0.0.0', port))
        self.serverSocket.listen(amountOfUsersAllow)
        self.privateKey, self.publicKey = getKeys()
        # O(1), constructor

    def __handleClients(self):  # connecting users to service & other users (client/user login/connect)
        receiveObj = receiver()
        self.clientSocket, address = self.serverSocket.accept()
        clientPublicKey = RSA.import_key(receiveObj.receiveMes(self.clientSocket))
        sendMes(self.publicKey.export_key().decode(), self.clientSocket)  # No need here try/except, summoner have

        diffie = self.__diffieHellman(clientPublicKey, receiveObj)  # From here starts 2 way authentication
        hellman = receiveObj.receiveMes(self.clientSocket)
        self.username = receiveObj.receiveMesEnc(self.privateKey.export_key().decode('utf-8'), self.clientSocket)
        self.password = receiveObj.receiveMesEnc(self.privateKey.export_key().decode('utf-8'), self.clientSocket)
        isUserExists, client = self.DBUsage.isExists(self.username, self.password)
        if hellman != diffie or isUserExists:
            self.__saveAttackerInfo()
            return  # Ends here if was some kind of breach

        self.__connectNewUserToOtherUsers(receiveObj, client, clientPublicKey)
        self.__createNewUserObject(client, receiveObj, clientPublicKey)
        self.threads[client.Username].start()
        # O(1)

    def __diffieHellman(self, clientPublicKey, receive):  # verifying user is legit a client of this service
        commonValue = getCommonValue()
        privateValue = randomPrivate()
        sendAndEncryptMessage(clientPublicKey, privateValue * commonValue, self.clientSocket)
        clientResult = int(receive.receiveMesEnc(self.privateKey.export_key().decode('utf-8'), self.clientSocket))
        return str(hide(privateValue, clientResult))
        # O(1)

    def __saveAttackerInfo(self):  # save user failed authorise information
        file = open("breached.txt", "ab")
        date = datetime.datetime.now()
        file.write(bytes(f"{self.address} " + " Username: \"" + self.username + "\" Password: \""
                         + self.password + "\" Date: " + str(date) + " Info: " + f" {self.clientSocket}\n", "utf-8"))
        file.close()
        # O(1)

    def __connectNewUserToOtherUsers(self, receiveObj, client, clientPublicKey):  # receive list of friendList & connect
        userFriendList = receiveObj.receiveMesEnc(
            self.privateKey.export_key().decode('utf-8'), self.clientSocket).split()
        isUserConnected = ""
        othersPubKey = ""
        for friend in userFriendList:
            if friend in self.peasants.keys():
                isUserConnected, othersPubKey = self.__updateNewConnection(
                    self.peasants[friend], client.Username, clientPublicKey, isUserConnected, othersPubKey)
            elif friend in self.kings.keys():
                isUserConnected, othersPubKey = self.__updateNewConnection(
                    self.kings[friend], client.Username, clientPublicKey, isUserConnected, othersPubKey)
            elif friend in self.gods.keys():
                isUserConnected, othersPubKey = self.__updateNewConnection(
                    self.gods[friend], client.Username, clientPublicKey, isUserConnected, othersPubKey)
            else:
                isUserConnected += " F"
        sendAndEncryptMessage(clientPublicKey, isUserConnected, self.clientSocket)
        sendAndEncryptMessage(clientPublicKey, othersPubKey, self.clientSocket)
        sendAndEncryptMessage(clientPublicKey, client.PermissionLevel, self.clientSocket)
        # O(1)

    @staticmethod  # collect connected & their publicKey to send to connecting user, also inform them who connected
    def __updateNewConnection(informUser, newConnectedUsername, clientPublicKey, isUserConnected, othersPubKey):
        try:
            sendAndEncryptMessage(informUser.getPubKey(), "newCon", informUser.getSocket())
            sendAndEncryptMessage(informUser.getPubKey(), newConnectedUsername, informUser.getSocket())
            sendAndEncryptMessage(informUser.getPubKey(),
                                  clientPublicKey.export_key().decode('utf-8'), informUser.getSocket())
            isUserConnected += " T"
            othersPubKey += f'{informUser.getPubKey().export_key().decode("utf-8")}!!!'
        except socket.error:
            isUserConnected += " F"
        finally:
            return isUserConnected, othersPubKey
        # O(1)

    def __createNewUserObject(self, client, receiveObj, clientPublicKey):  # creating user object & user thread
        usersObjectList = [silentPeasant, silentKing, silentGod]
        usersGroupsDictionaries = [self.peasants, self.kings, self.gods]
        usersGroupsDictionaries[client.PermissionLevel][client.Username] = usersObjectList[client.PermissionLevel](
            self.clientSocket, client.Username, receiveObj, clientPublicKey.export_key().decode('utf-8'), self.DBUsage)
        self.threads[client.Username] = Process(
                target=usersGroupsDictionaries[client.PermissionLevel][client.Username].run,
                args=(self.privateKey.export_key().decode('utf-8'), self.peasants, self.kings, self.gods))
        # O(1)

    def __checkConnected(self):  # every thread which is down means users disconnected, delete user object and inform
        deletelist = []  # others who has disconnected
        for client in self.threads.keys():
            if self.threads[client].is_alive() is False:
                deletelist.append(client)
                if client in self.peasants.keys():
                    del self.peasants[client]
                elif client in self.kings.keys():
                    del self.kings[client]
                elif client in self.gods.keys():
                    del self.gods[client]
        while len(deletelist) != 0:
            userName = deletelist.pop()
            del self.threads[userName]
            for client in self.peasants.keys():
                self.__informOtherUserSomeoneDisconnect(userName, self.peasants[client])
            for client in self.kings.keys():
                self.__informOtherUserSomeoneDisconnect(userName, self.kings[client])
            for client in self.gods.keys():
                self.__informOtherUserSomeoneDisconnect(userName, self.gods[client])
        # O(N)

    @staticmethod
    def __informOtherUserSomeoneDisconnect(userName, client):  # send command to connected users who disconnected
        try:
            sendAndEncryptMessage(client.getPubKey(), "disCon", client.getSocket())
            sendAndEncryptMessage(client.getPubKey(), userName, client.getSocket())
        except socket.error:
            pass
        # O(1)

    def __didNotCreateThreadCleanup(self):  # if couldn't run thread to handle client delete client, other users will
        for username in self.peasants.keys():  # get he disconnected only when trying to contact him.
            if username not in self.threads:
                self.peasants[username].getSocket().close()
                del self.peasants[username]
        for username in self.kings.keys():
            if username not in self.threads:
                self.kings[username].getSocket().close()
                del self.kings[username]
        for username in self.gods.keys():
            if username not in self.threads:
                self.gods[username].getSocket().close()
                del self.gods[username]
        # O(N)

    # noinspection PyBroadException
    def run(self):
        while True:
            try:
                self.__handleClients()
            except (socket.error, multiprocessing.ProcessError, BaseException):  # can crash because many reasons
                self.__saveAttackerInfo()  # Something happened & function crashed, saving information about breaching
            self.username = ""
            self.password = ""
            self.clientSocket.close()
            self.__didNotCreateThreadCleanup()
            self.__checkConnected()
        # O(infinite) ~ it's a server... it should always be online...
