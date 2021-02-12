import time
import select
import random
import socket as socketError
import hashlib
from os import path
from enum import Enum
from getpass import getpass
from contactDB import isThereContactNamed, deleteContact, addContact
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


class dictionary(Enum):  # No number written without any meaning
    tillEOF = -1
    set = 0
    randomMinimum = 1
    amountOfSplit = 1
    startOfFile = 2
    timeLimit = 5
    randomMaximum = 30
    encryptMessageSize = 86
    decryptMessageSize = 128
    RSAkeyBitsSize = 1024
    maxBytes = 1500


def getAddress():  # Gets server address
    dnsFileHolder = open("dnsAddress.txt", "rb")
    address = dnsFileHolder.readline().decode("utf-8")
    dnsFileHolder.close()
    return address
    # O(1)


def getCommonValue():  # Read a file & create a number from its text
    text = open("dnsAddress.txt", "rb")
    common_value = dictionary.set.value
    for run in str(text.read())[dictionary.startOfFile.value:dictionary.tillEOF.value]:
        common_value += ord(run)
    return common_value
    # O(N)


def randomPrivate():  # Random a number for diffie hellman algorithm
    return random.randint(dictionary.randomMinimum.value, dictionary.randomMaximum.value)
    # O(1)


def hide(myRes, otherRes):  # Encrypt number into bytes with scrypt
    return hashlib.scrypt(bytearray(str(myRes * otherRes % 10000), "utf-8"),
                          salt=bytearray("8", "utf-8"), n=2048, r=8, p=1)
    # O(1)


def getKeys():  # Gets RSA private key to decrypt & public key to send so other can encrypt for the user
    privateKey = RSA.generate(dictionary.RSAkeyBitsSize.value)
    return privateKey, privateKey.publickey()
    # O(1)


def validate():  # Makes sure there is an address to connect to
    while not path.exists("dnsAddress.txt"):
        print("<<< Please write down your server address.\n>>> Server address: ", end='')
        file = open("dnsAddress.txt", "wb")
        file.write(bytes(input().strip(), "utf-8"))
        file.close()
    # O(N)


def removeContact(connected):  # Get contact name & remove him
    name = ""
    while len(name) == 0:
        print(">>> Contact name: ", end='')
        name = input()
    deleteContact(name)
    if name in connected.keys():
        del connected[name]
        print(f"<<< {name} was deleted from your phonebook.")
    else:
        print("<<< Name wasn't found in phonebook.")
    # O(N)


##############################################MESSAGING FUNCTIONS#######################################################


def publicKeyShare(serverConnect, receiveObj, myPublicKey):  # Share my public Key & receive hosting server's
    try:
        sendMes(myPublicKey.export_key().decode(), serverConnect)
    except (socketError.error, ValueError):
        print("\n<<< Couldn't send message to server for unknown issue.\n>>> ", end='')
    return RSA.import_key(receiveObj.receiveMes(serverConnect))
    # O(1)


def diffieHellman(serverConnect, receiveObj, privateKey, serverPublicKey):  # Preform authentication
    common = getCommonValue()
    private = randomPrivate()
    serverAnswer = int(receiveObj.receiveMesEnc(privateKey.export_key().decode('utf-8'), serverConnect))
    try:
        sendAndEncryptMessage(serverPublicKey, private * common, serverConnect)
        encrypt = hide(private, serverAnswer)
        sendMes(encrypt, serverConnect)
    except (socketError.error, ValueError):
        print("\n<<< Couldn't send message to server for unknown issue.\n>>> ", end='')
    # O(1)


def login():  # Second authentication
    username = password = ""  # Didn't use regex because server side does that anyways, same check twice is pointless
    while len(username.strip()) == 0 or len(password.strip()) == 0:
        print("<<< Login.\n>>> Username: ", end='')  # If log in failed client will wait forever for a message from
        username = input()  # the server to continue the usage, but server will add him to breached & disconnect client
        print(">>> ", end='')
        password = getpass()
    return username, password
    # O(N)


def sendLogin(serverConnect, serverPublicKey, username, password):  # Send login information
    try:
        sendAndEncryptMessage(serverPublicKey, username, serverConnect)
        sendAndEncryptMessage(serverPublicKey, password, serverConnect)
    except (socketError.error, ValueError):
        print("\n<<< Couldn't send message to server for unknown issue.\n>>> ", end='')
    # O(1)


def checkPhonebook(serverConnect, receiveObj, connected, serverPublicKey, privateKey, phonebook):
    sendAndEncryptMessage(serverPublicKey, phonebook, serverConnect)  # Check who is connected
    phonebook = phonebook.split()
    whoIsConnected = receiveObj.receiveMesEnc(privateKey.export_key().decode('utf-8'), serverConnect).split()
    connectedPubKeys = receiveObj.receiveMesEnc(privateKey.export_key().decode('utf-8'), serverConnect).split("!!!")
    connectedPubKeys.pop()
    connectedPubKeys.reverse()
    for friend in range(0, len(whoIsConnected)):
        if whoIsConnected[friend] == "T":
            connected[phonebook[friend]] = connectedPubKeys.pop()
    print("<<< All users connected list: ", end='')
    for friendName in connected.keys():
        print(friendName + " ", end='')
    print("")  # Used as row down ("\n"), that's all.
    # O(N)


def deleteAndDisconnectMyself(serverConnect, serverPublicKey, username, password):  # Self destruct of user
    try:
        sendAndEncryptMessage(serverPublicKey, "delMe", serverConnect)
        sendAndEncryptMessage(serverPublicKey, username, serverConnect)
        sendAndEncryptMessage(serverPublicKey, password, serverConnect)
    except (socketError.error, ValueError):
        print("\n<<< Couldn't send message to server for unknown issue.\n>>> ", end='')
    return "exit"
    # O(1)


def sendMessageToContact(serverConnect, serverPublicKey, command, friend):  # Send to whom & message
    print(">>> to " + command + ": ", end='')
    messageToSend = input()
    while len(messageToSend.strip()) == 0:
        print(f"<<< Can't send empty messages.\n>>> to {command}: ", end='')
        messageToSend = input()
    try:
        sendAndEncryptMessage(serverPublicKey, command, serverConnect)
        sendAndEncryptMessage(RSA.import_key(friend), messageToSend, serverConnect)
    except (socketError.error, ValueError):
        print("\n<<< Couldn't send message to contact for unknown issue.\n>>> ", end='')
    # O(N)


def newConnection(serverSocket, myPriKey, receive, phonebook):  # Add new connection & it private key
    name = receive.receiveMesEnc(myPriKey.export_key().decode('utf-8'), serverSocket)
    publicKey = receive.receiveMesEnc(myPriKey.export_key().decode('utf-8'), serverSocket)
    if isThereContactNamed(name):
        phonebook[name] = publicKey
        print("\n<<< New user connected: " + name + ".\n>>> ", end='')
    # O(1)


def friendDisconnected(serverSocket, myPriKey, receive, phonebook):  # If I know the guy who disconnected I'm informed
    key = receive.receiveMesEnc(myPriKey.export_key().decode('utf-8'), serverSocket)
    if key in phonebook.keys():
        print("\n<<< Users " + key + " has disconnected.\n>>> ", end='')
        del phonebook[key]
    # O(1)


def gotMessage(serverSocket, myPriKey, receive, whomSent):  # If known contact show its message
    print("\n<<< From: " + whomSent + ", Message: ", end='')
    message = receive.receiveMesEnc(myPriKey.export_key().decode('utf-8'), serverSocket)
    print(message + "\n>>> ", end='')
    # O(1)


def serverMessage(serverSocket, myPriKey, receive):  # Server notifies message
    message = receive.receiveMesEnc(myPriKey.export_key().decode('utf-8'), serverSocket)
    print("\n<<< " + message, "\n>>> ", end='')
    # O(1)


def addContactToPhonebook(serverConnect, serverPublicKey):  # Add new contact & connect to
    name = ""  # Contact Won't get my messages if he doesn't add me
    while len(name) == 0:
        print("<<< Please write down contact name to add.\n>>> Name: ", end='')
        name = input()
    addContact(name)
    try:
        sendAndEncryptMessage(serverPublicKey, "askCon", serverConnect)
        sendAndEncryptMessage(serverPublicKey, name, serverConnect)
    except (socketError.error, ValueError):
        print("\n<<< Couldn't add new contact for unknown issue, please reconnect to the server.\n>>> ", end='')
    # O(N)


def sendMes(message, socket):  # Send message
    socket.send(bytes(str(message), "utf-8") + b"\n\\\x03")
    # O(1)


def sendAndEncryptMessage(publicKey, message, socket):  # Encrypt & then send message
    message = str(message)
    message = [(message[i: i + dictionary.encryptMessageSize.value]) for i in range(
        dictionary.set.value, len(message), dictionary.encryptMessageSize.value)]
    cipher = PKCS1_OAEP.new(key=publicKey)
    temp = bytes("", "utf-8")
    for part in message:
        temp += cipher.encrypt(bytes(part, "utf-8"))
    socket.send(temp + b"\n\\\x03")
    # O(N)


class receiver(object):  # Object to hold receiving messages with semaphore & mutex
    def __init__(self):
        self.__overdraft = bytes("", "utf-8")
        self.__isReadingMessage = False
    # O(1), constructor

    def __receiveMessage(self, client):  # Receiver of messages from client
        while self.__isReadingMessage:
            time.sleep(0.05)  # Waiting so it won't hold thread on a long loop & let other programs run instead
        self.__isReadingMessage = True  # Not on Enum because it's float type
        message = self.__overdraft
        self.__overdraft = bytes("", "utf-8")
        while b"\n\\\x03" not in message:
            time.sleep(0.05)
            recv_ready, _, _ = select.select([client], [], [], dictionary.timeLimit.value)
            try:
                if len(recv_ready) != 0:
                    message += client.recv(dictionary.maxBytes.value)
            except ValueError:
                return b""
        message, self.__overdraft = message.split(b"\n\\\x03", dictionary.amountOfSplit.value)
        self.__isReadingMessage = False
        return message
    # O(N)

    @staticmethod  # Made static because no "self" was used, PEP8
    def __decrypt(privateKey, message):  # Decrypt the message that had been received
        message = [(message[i: i + dictionary.decryptMessageSize.value]) for i in range(
            dictionary.set.value, len(message), dictionary.decryptMessageSize.value)]
        decrypt = PKCS1_OAEP.new(key=RSA.import_key(privateKey))
        temp = bytes("", "utf-8")
        for part in message:
            temp += decrypt.decrypt(part)
        return temp
    # O(N)

    def receiveMes(self, client):  # Receive message & decode it in utf-8
        return self.__receiveMessage(client).decode("utf-8")
    # O(1)

    def receiveMesEnc(self, privateKey, client):  # Receive message & decrypt it & then decode in utf-8
        return self.__decrypt(privateKey, self.__receiveMessage(client)).decode("utf-8")
    # O(1)

    def receiveFile(self, privateKey, client):  # Receive file & decrypt it
        return self.__decrypt(privateKey, self.__receiveMessage(client))
    # O(1)
