import socket
import threading
import os
from subprocess import Popen, PIPE
import signal

queue = []
seen_messages = set()
lock = threading.Lock()


class ClientThread(threading.Thread):
    def __init__(self, clientAddress, clientsocket):
        super().__init__()
        self.csocket = clientsocket
        print("New connection added: ", clientAddress)

    def run(self):
        # self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
        global lock
        global queue
        global seen_messages
        try:
            while True:
                data = self.csocket.recv(2048)
                if not data:
                    print("not data")
                    continue

                msg = data.decode().strip()
                # print(f"Received message: {msg}")

                lock.acquire()
                # print(f"Connection: {self.csocket.getsockname()} locked")
                if msg == '1':
                    print(f"Received message: {msg}")
                    to_send = None if not queue else queue.pop()
                    if to_send is None:
                        # If there is no message to send, just send '1' back
                        to_send = '1'
                    print(f"Sending message: {to_send}")
                    self.csocket.send(to_send.encode())

                else:
                    if not msg in seen_messages:
                        seen_messages.add(msg)
                        queue.append(msg)
                        # print(f"Added message to queue: {msg}")

                lock.release()
                # print(f"Connection: {self.csocket.getsockname()} released")

        except Exception as e:
            lock.release()
            print(f"Error: {str(e)}")
            print(f"Client at {self.csocket.getsockname()} disconnected...")
        finally:
            self.csocket.close()
            print(f"Connection to {self.csocket.getsockname()} closed")


LOCALHOST = "localhost"
PORT = 8889
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    server.bind((LOCALHOST, PORT))
except OSError:
    process = Popen(
        ["lsof", "-i", ":{0}".format(PORT)], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    for process in str(stdout.decode("utf-8")).split("\n")[1:]:
        data = [x for x in process.split(" ") if x != '']
        if (len(data) <= 1):
            continue
        os.kill(int(data[1]), signal.SIGKILL)

print("Server started")
print("Waiting for client request..")

while True:
    server.listen(5)
    clientsock, clientAddress = server.accept()
    newthread: ClientThread = ClientThread(clientAddress, clientsock)
    newthread.start()
