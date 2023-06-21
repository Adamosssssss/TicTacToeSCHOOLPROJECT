import tkinter as tk
import socket
import threading
from time import sleep
from RSA import RSA


class TicTacToeServer:
    def __init__(self):
        self.server = None
        self.host_IP = '127.0.0.1'
        self.port = 5000
        self.client_name = " "
        self.clients = []
        self.clients_names = []

        self.window = tk.Tk()
        self.window.title("Tic-Tac-Toe Server")

        # Top frame consisting of two buttons widgets (i.e. btnStart, btnStop)
        self.topFrame = tk.Frame(self.window)
        self.btnStart = tk.Button(self.topFrame, text="Start", command=self.start_server)
        self.btnStart.pack(side=tk.LEFT)
        self.topFrame.pack(side=tk.TOP, pady=(5, 0))

        # Middle frame consisting of two labels for displaying the host and port info
        self.middleFrame = tk.Frame(self.window)
        self.lblHost = tk.Label(self.middleFrame, text="Address: X.X.X.X")
        self.lblHost.pack(side=tk.LEFT)
        self.lblPort = tk.Label(self.middleFrame, text="Port:XXXX")
        self.lblPort.pack(side=tk.LEFT)
        self.middleFrame.pack(side=tk.TOP, pady=(5, 0))

        # The client frame shows the client area
        self.clientFrame = tk.Frame(self.window)
        self.lblLine = tk.Label(self.clientFrame, text="**********Client List**********").pack()
        self.scrollBar = tk.Scrollbar(self.clientFrame)
        self.scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tkDisplay = tk.Text(self.clientFrame, height=10, width=30)
        self.tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
        self.scrollBar.config(command=self.tkDisplay.yview)
        self.tkDisplay.config(yscrollcommand=self.scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
        self.clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))

    def start_server(self):
        self.btnStart.config(state=tk.DISABLED)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # print(socket.AF_INET)
        # print(socket.SOCK_STREAM)

        self.server.bind((self.host_IP, self.port))
        self.server.listen(2)  # server is listening for client connection

        threading.Thread(target=self.accept_clients, args=(self.server, " ")).start()

        self.lblHost["text"] = "Address: " + self.host_IP
        self.lblPort["text"] = "Port: " + str(self.port)

    def accept_clients(self, the_server, y):
        while True:
            if len(self.clients) < 2:
                client, addr = the_server.accept()
                self.clients.append(client)

                # use a thread so as not to clog the gui thread
                threading.Thread(target=self.send_receive_client_message, args=(client, addr)).start()

    def send_receive_client_message(self, client_connection, client_ip_addr):
        client_msg = " "

        # send welcome message to client
        self.client_name = client_connection.recv(4096).decode()
        # print(self.client_name)

        if len(self.clients) < 2:
            client_connection.send("welcome1".encode())
        else:
            client_connection.send("welcome2".encode())

        self.clients_names.append(self.client_name)
        self.update_client_names_display(self.clients_names)  # update client names display

        if len(self.clients) > 1:
            sleep(1)
            symbols = ["O", "X"]

            # send opponent name and symbol
            self.clients[0].send(("opponent_name$" + self.clients_names[1] + "symbol" + symbols[0]).encode())
            self.clients[1].send(("opponent_name$" + self.clients_names[0] + "symbol" + symbols[1]).encode())

        while True:
            # get the player choice from received data
            data = client_connection.recv(4096).decode()
            print(data)
            if not data:
                break

            # player x,y coordinate data. forward to the other player
            if data.startswith("$xy$"):
                # is the message from client1 or client2?
                if client_connection == self.clients[0]:
                    # send the data from this player (client) to the other player (client)
                    self.clients[1].send(data.encode())
                else:
                    # send the data from this player (client) to the other player (client)
                    self.clients[0].send(data.encode())

        # find the client index then remove from both lists(client name list and connection list)
        idx = self.get_client_index(self.clients, client_connection)
        del self.clients_names[idx]
        del self.clients[idx]
        client_connection.close()

        self.update_client_names_display(self.clients_names)  # update client names display


    # @staticmethod
    def get_client_index(client_list, curr_client):
        idx = 0
        for conn in client_list:
            if conn == curr_client:
                break
            idx = idx + 1

        return idx

    def update_client_names_display(self, name_list):
        self.tkDisplay.config(state=tk.NORMAL)
        self.tkDisplay.delete('1.0', tk.END)

        for c in name_list:
            self.tkDisplay.insert(tk.END, c + "\n")
        self.tkDisplay.config(state=tk.DISABLED)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    server = TicTacToeServer()
    server.run()
    