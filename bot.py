#!/usr/bin/env python3

import socket
import time
import pickle

## Bot Information
botnick    = "palasso_dev"
botpass    = ""
uname      = "gotmail"
realname   = "gotmail"

## Server Information
port       = 6667
server     = "chat.freenode.net"
channel    = "##testing"

## Bot Settings
bufsize    = 2048
master     = "palasso"
password   = "lolcats"
operand    = "!"

## Stored Files
loggedturfs= "log.txt"
turfstats  = "stats.pickle"

## Commands
commands = {"send": "sendcmd", "turfed": "turfed", "shutdown": "shutdown"}

def sendcmd():
    nick = getnick(line['sender'])
    if not param:
        receiver = nick
    else:
        receiver = param
    if receiver in names:
        reply = f"delivers {receiver} a steaming pile of 💩."
        if receiver in stats:
            stats[receiver] += 1
        else:
            stats[receiver] = 1
        logturf(nick, receiver)
    else:
        reply = f"can't find user {receiver} :/"
    sendme(line['channel'], reply)

def turfed():
    nick = getnick(line['sender'])
    if not param:
        receiver = nick
    else:
        receiver = param
    if receiver in stats:
        num = stats[receiver]
        if num == 1:
            reply = f"{receiver} received a steaming pile of 💩."
        else:
            reply = f"{receiver} received {num} steaming piles of 💩."
    else:
        reply = f"{receiver} received no steaming piles of 💩."
    sendmsg(line['channel'], reply)

def shutdown():
    nick = getnick(line['sender'])
    if line['channel'] != botnick:
        if password == param:
            reply = f"{nick}: You just gave your password to everyone you dumbass!"
        else:
            reply = f"{nick}: At least you weren't stupid enough to type your real password..."
        sendmsg(line['channel'], reply)
    elif password == param:
        sendmsg(nick, "Shutting Down!")
        send(f"PART {channel}\n")
        send("QUIT \n")
        exit(0)
    else:
        sendmsg(nick, "Wrong password! Try again...")

## Utilities
def send(msg):
    ircsock.send(msg.encode('utf8'))

def ping():
    send("PONG :pingis\n")

def sendmsg(chan, msg):
    send(f"PRIVMSG {chan} :{msg}\n")

def sendme(chan, msg):
    send(f"PRIVMSG {chan} :\x01ACTION {msg}\x01\r\n") ## working do NOT touch.

def logturf(sender, receiver):
    with open(loggedturfs, 'a') as handle:
        handle.write(f"{sender} sent a package to {receiver}.\n")
    with open(turfstats, 'wb') as handle:
        pickle.dump(stats, handle, protocol=pickle.HIGHEST_PROTOCOL)

def getnick(s):
    result = ''
    for c in s:
        if c == '!':
            break
        result += c
    return result[1:]

## Where the action happens
stats={}
try:
    with open(turfstats, 'rb') as handle:
        stats = pickle.load(handle)
except OSError:
    with open(turfstats, 'wb') as handle:
        pickle.dump(stats, handle, protocol=pickle.HIGHEST_PROTOCOL)
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, port))
send(f"USER {uname} 2 3 {realname}\n")
send(f"NICK {botnick}\n")
send(f"PRIVMSG NickServ :identify {botpass} \n")
time.sleep(10)
send(f"JOIN {channel}\n")
sendmsg(master, "Hello Master, I'm ready to serve.")

read_buffer = ''
names = []

## Main Loop
while True:
    read_buffer += ircsock.recv(bufsize).decode()
    lines = read_buffer.split('\r\n')
    read_buffer = lines.pop();

    for line in lines:
        print(line)
        line = line.rstrip().split(' ', 3)
        if line[0] == 'PING':
            ping()
        elif len(line) > 3:
            line = {'sender': line[0], 'type': line[1], 'channel': line[2], 'message': line[3][1:]}
            if line['type'] == '353':
                names += line['message'][len(channel)+len(botnick)+3:].split()
                print(names)
            elif line['type'] == 'PART' or line['type'] == 'QUIT':
                names.remove(getnick(line['sender']))
                print(names)
            else:
                if line['message'].count(' ') > 0:
                    cmd, param = line['message'].split(' ', 1)
                else:
                    cmd = line['message']
                    param = False
                cmd = cmd[len(operand):]
                if cmd in commands:
                    locals()[commands[cmd]]()
        elif len(line) > 2:
            line = {'sender': line[0], 'type': line[1], 'message': line[2][1:]}
            if line['type'] == 'JOIN':
                names.append(getnick(line['sender']))
                print(names)
            elif line['type'] == 'NICK':
                names.remove(getnick(line['sender']))
                names.append(line['message'])
                print(names)
            elif line['type'] == 'PART' or line['type'] == 'QUIT':
                names.remove(getnick(line['sender']))
                print(names)
