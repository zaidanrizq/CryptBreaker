import hashlib
import json
import os

import bcrypt
import pika
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from art import text2art

#Sesuaikan
#----------------------------------
serverIP = "192.168.1.8"
resultQueueName = "Result Queue"
jobQueueName = "Job Queue"
processedJobQueueName = "Processed Job Notificatoin Queue"
#----------------------------------

#Const
#----------------------------------
processed_jobs = set()
#----------------------------------

def showMainMenu():

    allowedInput = [0,1]

    print("============================================================================")
    print(text2art("CryptBreaker"))
    print(text2art("(Client)"))
    print("============================================================================")
    print("MENU UTAMA")
    print("1. Mulai cracking password.")
    print("0. Keluar dari program.")

    while True:
        try:
            menuPilihan = int(input("PILIH MENU: "))
            if menuPilihan in allowedInput:
                break
            else:
                print("Menu yang tersedia hanya 0, 1, 2, dan 3. Pilih kembali!")
        except:
            print("Menu yang tersedia hanya 0, 1, 2, dan 3. Pilih kembali!")
            
    return menuPilihan

def startCracking():

    allowedInput = [0,1]  
    
    print("============================================================================")
    print(text2art("CryptBreaker"))
    print(text2art("(Client)"))
    print("============================================================================")
    print('Menunggu pesan. Untuk berhenti dari proses cracking, tekan CTRL+C')
    print("PROGRAM RUNNING...\n")
    try:
        channel.queue_declare(queue = resultQueueName)
        channel.queue_declare(queue = processedJobQueueName)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue = jobQueueName, auto_ack = False, on_message_callback = onMessageReceived)
        channel.basic_consume(queue = processedJobQueueName, auto_ack = True, on_message_callback = onNotificationReceived)
        consuming = True
        channel.start_consuming()
        
    except KeyboardInterrupt:
        if consuming:
            channel.stop_consuming()

        print("\nProses berhenti.")
        print("0. Kembali ke menu utama.")
        print("1. Keluar dari program.")

        while True:
            try:
                menuPilihan = int(input("PILIH MENU: "))
                if menuPilihan not in allowedInput:
                    print("Menu yang tersedia hanya 0 dan 1. Pilih kembali!")
                else:
                    return menuPilihan
            except:
                print("Menu yang tersedia hanya 0 dan 1. Pilih kembali!")

def sendMessage(channel, queue_name, message):
    channel.basic_publish(exchange = '', routing_key = queue_name,
                          body = json.dumps(message))
    print(f"Sent {message} to {queue_name}")

def onMessageReceived(ch, method, properties, body):

    global processed_jobs
    
    batchMessage = json.loads(body)
    hashType = guessHashType(batchMessage[0]['password_terenkripsi'])

    for message in batchMessage:
        if json.dumps(message['nama_job']) in processed_jobs:
            break

        encryptedPassword = message['password_terenkripsi']
        inputSequence = message['input_sekuen']
        result = checkInputSequence(hashType,inputSequence, encryptedPassword)
        
        if result:
            print(f"{message['nama_job']}: Password cracked")
            resultMessage = {
                'nama_job' : message['nama_job'],
                'hash_type' : hashType,
                'input_sekuen' : inputSequence
            }
            sendMessage(ch, resultQueueName, resultMessage)
            sendMessage(ch, processedJobQueueName, message['nama_job'])
            print("")
            break
        
    channel.basic_ack(delivery_tag=method.delivery_tag)

def onNotificationReceived(ch, method, properties, body):
    global processed_jobs
    processed_job = body.decode('utf-8')
    processed_jobs.add(processed_job)

def checkInputSequence(hash_type, input_sequence, encrypted_password):
    if hash_type == "MD5":
        return hashlib.md5(input_sequence.encode()).hexdigest() == encrypted_password
    elif hash_type == "SHA1":
        return hashlib.sha1(input_sequence.encode()).hexdigest() == encrypted_password
    elif hash_type == "SHA256":
        return hashlib.sha256(input_sequence.encode()).hexdigest() == encrypted_password
    elif hash_type == "bcrypt":
        encoded_input_sequence = input_sequence.encode()
        encoded_encrypted_password = encrypted_password.encode()
        return bcrypt.checkpw(encoded_input_sequence, encoded_encrypted_password)
    elif hash_type == "Argon2":
        ph = PasswordHasher()
        try:
            ph.verify(encrypted_password, input_sequence)
            return True
        except VerifyMismatchError:
            return False
    else:
        return None

def guessHashType(hash_string):
    length = len(hash_string)
    hash_string_lower = hash_string.lower()

    if length == 32:  # MD5 hash length
        return 'MD5'
    elif length == 40:  # SHA1 hash length
        return 'SHA1'
    elif length == 64:  # SHA256 hash length
        return 'SHA256'
    elif hash_string.startswith(("$2a$", "$2b$", "$2y$")):
        return 'bcrypt'
    elif hash_string.startswith(("$argon2i$", "$argon2d$", "$argon2id$")):
        return 'Argon2'
    else:
        return 'Unknown'
    

if __name__ == "__main__":
    
    connectionParameters = pika.ConnectionParameters(serverIP, heartbeat=0)
    connection = pika.BlockingConnection(connectionParameters)
    channel = connection.channel()

    try:
        while True:
            menuPilihan = showMainMenu()
            match menuPilihan:
                case 0:
                    break
                case 1:
                    os.system('cls')
                    menuPilihan = startCracking()
                    if menuPilihan == 1:
                        break
                    else:
                        os.system('cls')
    finally:
        if channel.is_open or connection.is_open:
            try:
                channel.close()
                connection.close()
                print("Closing Channel.")
                print("Closing Connection.")
            except:
                print("Closing Channel.")
                print("Closing Connection.")
