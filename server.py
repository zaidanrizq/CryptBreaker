import json
import os
import sys

import pika
from art import text2art

#Sesuaikan
#---------------------------------------------------------------
serverIP = "192.168.1.8"
jobQueueName = "Job Queue"
resultQueueName = "Result Queue"
jobName = "Job "
password_dictionary = '10-million-password-list-top-100000.txt'
batch_size = 5
#---------------------------------------------------------------

#Const
#---------------------------------------------------------------
jobOrder = 1
crackedPassword = []
#---------------------------------------------------------------


def showMainMenu():
    
    allowedInput = [0,1,2]
    
    print("============================================================================")
    print(text2art("CryptBreaker"))
    print(text2art("(Server)"))
    print("============================================================================")
    print("MENU UTAMA")
    print("1. Tambah hashed password yang ingin di crack.")
    print("2. Tampilkan hashed password yang berhasil di crack.")
    print("0. Keluar dari program.")

    while True:
        try:
            menuPilihan = int(input("PILIH MENU: "))
            if menuPilihan in allowedInput:
                break
            else:
                print("Menu yang tersedia hanya 0, 1, 2. Pilih kembali!")
        except:
            print("Menu yang tersedia hanya 0, 1, dan 2. Pilih kembali!")
            
    return menuPilihan

def tambahJob():
    
    global jobOrder

    allowedInput = [0,1]
    batchMessage = []
    
    print("============================================================================")
    print(text2art("CryptBreaker"))
    print(text2art("(Server)"))
    print("============================================================================")
    print("MENU TAMBAH HASHED PASSWORD")
    print("0. Kembali ke menu utama.")
    
    while True:
        try:
            manyJob = int(input("Masukkan berapa banyak hashed password yang ingin di crack: "))
            break
        except:
            print("Masukkan harus berupa angka!")

    if manyJob == 0:
        return None
    else:
        if jobOrder == 1:
            channel.queue_declare(queue = jobQueueName)
        
        with open(password_dictionary, 'r') as file:
            passwords = file.read().splitlines()
        
        for i in range(manyJob):
            namaJob = jobName + str(jobOrder)
            print(f"\n{jobName} {jobOrder}")
            encryptedPassword = input(f"Masukkan hashed password ke {jobOrder}: ")

            for j, password in enumerate(passwords):
                job_message = {
                        'nama_job' : f'{jobName}{jobOrder}',
                        'password_terenkripsi' : encryptedPassword,
                        'input_sekuen' : password
                    }
                batchMessage.append(job_message)

                if (j+1) % batch_size == 0 or (j+1) == len(passwords):
                    sendBatchMessage(channel, jobQueueName, batchMessage)
                    batchMessage = []
            
            jobOrder += 1

        print("\nPenambahan berhasil.")
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

def sendBatchMessage(channel, queue_name, message):
    
    batch_message = json.dumps(message)
    channel.basic_publish(exchange = '', routing_key = queue_name, body = batch_message)

def showCrackedPassword():

    global crackedPassword
    
    allowedInput = [0,1]

    maxShowMessage = 100
    
    print("============================================================================")
    print(text2art("CryptBreaker"))
    print(text2art("(Server)"))
    print("============================================================================")
    print("MENU TAMPILKAN CRACKED PASSWORD\n")

    try:
        channel.queue_declare(queue=resultQueueName, passive=True)
        
        for i in range(maxShowMessage):
            method_frame, header_frame, body = channel.basic_get(queue=resultQueueName, auto_ack=False)
            if method_frame:
                crackedPassword.append(body.decode())
                channel.basic_ack(method_frame.delivery_tag)
            else:
                break

        for j in crackedPassword:
            print(j)
            
    except pika.exceptions.ChannelClosedByBroker:
        print("BELUM ADA PASSWORD YANG BERHASIL DI CRACK!!!")
        print("JALANKAN ULANG PROGRAM!!!")
        sys.exit(1)

    print("\n0. Kembali ke menu utama.")
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
                    menuPilihan = tambahJob()
                    if menuPilihan == 1:
                        break
                    else:
                        os.system('cls')
                case 2:
                    os.system('cls')
                    menuPilihan = showCrackedPassword()
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
