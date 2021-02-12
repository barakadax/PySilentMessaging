import time
import select
import random
import hashlib
from enum import Enum
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


def getCommonValue():  # Read a file & create a number from its text
    text = open("common.txt", "rb")
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


def getKeys():
    privateKey = RSA.generate(dictionary.RSAkeyBitsSize.value)
    return privateKey, privateKey.publickey()
    # O(1)


def sendMes(message, socket):  # Send message to client
    socket.send(bytes(str(message), "utf-8") + b"\n\\\x03")
    # O(1)


def sendAndEncryptMessage(publicKey, message, socket):  # Encrypt & then send message to client
    message = str(message)
    message = [(message[i: i + dictionary.encryptMessageSize.value]) for i in range(
        dictionary.set.value, len(message), dictionary.encryptMessageSize.value)]
    cipher = PKCS1_OAEP.new(key=publicKey)
    temp = bytes("", "utf-8")
    for part in message:
        temp += cipher.encrypt(bytes(part, "utf-8"))
    socket.send(temp + b"\n\\\x03")
    # O(N)


def transferSendMes(message, socket):  # Send bytes to client
    socket.send(message + b"\n\\\x03")
    # O(1)


def sendFile(publicKey, fileInfo, socket):  # Encrypt & send file to user
    message = [(fileInfo[i: i + dictionary.encryptMessageSize.value]) for i in range(
        dictionary.set.value, len(fileInfo), dictionary.encryptMessageSize.value)]
    cipher = PKCS1_OAEP.new(key=publicKey)
    temp = bytes("", "utf-8")
    for part in message:
        temp += cipher.encrypt(part)
    socket.send(temp + b"\n\\\x03")
    # O(N)


class receiver(object):  # Object to hold receiving messages from clients with semaphore & mutex
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

    def transferReceiveMes(self, client):  # Receive message in other client encrypt so server can't decrypt it
        return self.__receiveMessage(client)
    # O(1)

    def receiveFile(self, privateKey, client):  # Receive file in other client encrypt so server can't decrypt it
        return self.__decrypt(privateKey, self.__receiveMessage(client))
    # O(1)
