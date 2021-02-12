import os
import socket
from Crypto.PublicKey import RSA
from multiprocessing import Process, Manager
from contactDB import getContacts
from clientFunctions import getKeys, receiver, validate, getAddress, publicKeyShare, diffieHellman, login, \
    checkPhonebook, deleteAndDisconnectMyself, sendMessageToContact, newConnection, friendDisconnected, gotMessage, \
serverMessage, removeContact, addContactToPhonebook, sendLogin


def getInput(receive, myPriKey, serverSocket, phonebook):  # Function for thread, receiving messages
    myPriKey = RSA.import_key(myPriKey)
    while True:
        message = receive.receiveMesEnc(myPriKey.export_key().decode('utf-8'), serverSocket)
        if message == "newCon":  # Someone connected & wanna contact
            newConnection(serverSocket, myPriKey, receive, phonebook)
        elif message == "disCon":  # Someone I might now disconnected
            friendDisconnected(serverSocket, myPriKey, receive, phonebook)
        elif message == "serMes":
            serverMessage(serverSocket, myPriKey, receive)
        elif message == "bye":  # Been disconnected from the service
            print("\nServer disconnected you.\n>>> ", end='')
            return
        elif message in phonebook.keys():  # Check if sent message is from contact list
            gotMessage(serverSocket, myPriKey, receive, message)
    # O(N), no one is connected forever


def cliInterface(serverConnect, serverPublicKey, connected, receiveProcess, username, password):  # User functionality
    command = ""
    while command.lower() not in ["exit", "quit", "disconnect"]:
        if command.lower() not in ["exit", "quit", "disconnect"]:
            print(">>> ", end='')
            command = input()
        if not receiveProcess.is_alive():  # If got disconnected via the service, closing everything from here
            command = "exit"
        elif command.lower() in ["h", "g", "-h", "-g", "help", "guide", "man", "?"]:
            guide()
        elif command.lower() in ["delete", "remove", "delete contact", "remove contact"]:
            removeContact(connected)
        elif command.lower() in ["add", "add contact", "add new contact", "add friend", "add new friend"]:
            addContactToPhonebook(serverConnect, serverPublicKey)
        elif command.lower() in ["delme", "delete me", "delete myself"]:  # Request permanent disconnection from service
            command = deleteAndDisconnectMyself(serverConnect, serverPublicKey, username, password)
        elif command in connected.keys():  # Send message to contact
            sendMessageToContact(serverConnect, serverPublicKey, command, connected[command])
        elif command.lower() not in ["exit", "quit", "disconnect"]:
            print("Error, no contact/command called: \"" + command + "\" was found, please try again.")
    # O(N), no one is connected forever


def guide():  # Prints list of commands + how to send message to user
    spaces = "   "
    text = "<<<OPTIONS:\n<<<" + 4 * spaces + " delete - deletes contact from your phonebook\n<<<" + 4 * spaces + \
        " add - adds new contact to your phonebook\n<<<" + 4 * spaces + \
        " delMe - delete yourself from the service & disconnect\n<<<" + 4 * spaces + \
        " exit - disconnect & closes the program\n<<<" + 4 * spaces + \
        " to send message to to contact type his name & press enter, enter the message you wan to send & press" + \
        " enter again."
    print(text)
    # O(1)


def main():  # Code structure starts from here
    os.system('cls' if os.name == 'nt' else 'clear')
    validate()
    receiveObj = receiver()
    username, password = login()
    serverConnect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverConnect.connect((getAddress(), 1234))
    # serverConnect.connect(('0.0.0.0', 1234))  # For testing, delete later
    privateKey, publicKey = getKeys()
    serverPublicKey = publicKeyShare(serverConnect, receiveObj, publicKey)
    diffieHellman(serverConnect, receiveObj, privateKey, serverPublicKey)
    sendLogin(serverConnect, serverPublicKey, username, password)
    connected = Manager().dict()  # Dictionary shared memory between threads
    phonebook = getContacts(username)  # HERE SQLITE GET ALL FRIENDS
    checkPhonebook(serverConnect, receiveObj, connected, serverPublicKey, privateKey, phonebook)
    permissionLevel = receiveObj.receiveMesEnc(privateKey.export_key().decode('utf-8'), serverConnect)  # ONLY FOR APP
    receiveProcess = Process(target=getInput, args=(
        receiveObj, privateKey.export_key().decode('utf-8'), serverConnect, connected))
    receiveProcess.start()
    cliInterface(serverConnect, serverPublicKey, connected, receiveProcess, username, password)
    receiveProcess.kill()
    serverConnect.close()
    # O(1)


if __name__ == "__main__":
    main()
