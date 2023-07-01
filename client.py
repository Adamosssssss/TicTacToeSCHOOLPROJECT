import tkinter as tk
import socket
from tkinter import PhotoImage
from tkinter import messagebox
from time import sleep
import threading
from gameRules import gameRules
import RSA
import json


class TicTacToeClient():
    def __init__(self):
        # MAIN GAME WINDOW
        self.window_main = tk.Tk()
        self.window_main.title("Tic-Tac-Toe Client")
        self.top_welcome_frame= tk.Frame(self.window_main)
        self.lbl_name = tk.Label(self.top_welcome_frame, text = "Name:")
        self.lbl_name.pack(side=tk.LEFT)
        self.ent_name = tk.Entry(self.top_welcome_frame)
        self.ent_name.pack(side=tk.LEFT)
        self.btn_connect = tk.Button(self.top_welcome_frame, text="Connect", command=lambda : self.connect())
        self.btn_connect.pack(side=tk.LEFT)
        self.top_welcome_frame.pack(side=tk.TOP)
        self.top_frame = tk.Frame(self.window_main)

        #RSA 
        self.primes = RSA.get_primes(15, 300)
        self.public_key, self.private_key = RSA.keys(self.primes[0], self.primes[1])
        self.server_public_key = None
        print(self.public_key)

        # network client
        self.client = None
        self.host_IP = 'localhost'
        self.port = 5000
        self.list_labels = []
        self.num_cols = 3
        self.your_turn = False
        self.you_started = False

        self.your_details = {
            "name": "Charles",
            "symbol": "X",
            "color" : "",
            "score" : 0
        }

        self.opponent_details = {
            "name": " ",
            "symbol": "O",
            "color": "",
            "score": 0
        }

        for x in range(3):
            for y in range(3):
                self.lbl = tk.Label(self.top_frame, text=" ", font="Helvetica 45 bold", height=2, width=5, highlightbackground="grey",
                            highlightcolor="grey", highlightthickness=1)
                self.lbl.bind("<Button-1>", lambda e, xy=[x, y]: self.get_cordinate(xy))
                self.lbl.grid(row=x, column=y)

                self.dict_labels = {"xy": [x, y], "symbol": "", "label": self.lbl, "ticked": False}
                self.list_labels.append(self.dict_labels)

        self.lbl_status = tk.Label(self.top_frame, text="Status: Not connected to server", font="Helvetica 14 bold")
        self.lbl_status.grid(row=3, columnspan=3)

        self.top_frame.pack_forget()


    def gameStart(self):
        
        sleep(3)

        for i in range(len(self.list_labels)):
            self.list_labels[i]["symbol"] = ""
            self.list_labels[i]["ticked"] = False
            self.list_labels[i]["label"]["text"] = ""
            self.list_labels[i]["label"].config(foreground="black", highlightbackground="grey",
                                        highlightcolor="grey", highlightthickness=1)

        self.lbl_status.config(foreground="black")
        self.lbl_status["text"] = "STATUS: Game's starting."
        sleep(1)
        self.lbl_status["text"] = "STATUS: Game's starting.."
        sleep(1)
        self.lbl_status["text"] = "STATUS: Game's starting..."
        sleep(1)

        if self.you_started:
            self.you_started = False
            self.your_turn = False
            self.lbl_status["text"] = "STATUS: " + self.opponent_details["name"] + "'s turn!"
        else:
            self.you_started = True
            self.your_turn = True
            self.lbl_status["text"] = "STATUS: Your turn!"
        


    def get_cordinate(self, xy):
        # convert 2D to 1D cordinate i.e. index = x * num_cols + y
        self.label_index = xy[0] * self.num_cols + xy[1]
        label = self.list_labels[self.label_index]
        print(xy)

        if self.your_turn:
            if label["ticked"] is False:
                label["label"].config(foreground=self.your_details["color"])
                label["label"]["text"] = self.your_details["symbol"]
                label["ticked"] = True
                label["symbol"] = self.your_details["symbol"]
                # send xy cordinate to server
                print(str(xy[0]), str(xy[1]))
                message = "$xy$" + str(xy[0]) + "$" + str(xy[1])
                print(message)

                #Encrypted
                #enc_message = RSA.encrypt(self.server_public_key, message)
                #print(enc_message)
                #self.client.send(json.dumps(enc_message).encode('utf-8'))

                #NonEncrypted
                self.client.send(message.encode())
                
                self.your_turn = False

                # Does this play leads to a win or a draw
                result = self.game_logic()
                if result[0] is True and result[1] != "":  # a win
                    self.your_details["score"] = self.your_details["score"] + 1
                    self.lbl_status["text"] = "Game over, You won! You(" + str(self.your_details["score"]) + ") - " \
                        "" + self.opponent_details["name"] + "(" + str(self.opponent_details["score"])+")"
                    self.lbl_status.config(foreground="green")
                    threading._start_new_thread(self.gameStart, ())

                elif result[0] is True and result[1] == "":  # a draw
                    self.lbl_status["text"] = "Game over, Draw! You(" + str(self.your_details["score"]) + ") - " \
                        "" + self.opponent_details["name"] + "(" + str(self.opponent_details["score"]) + ")"
                    self.lbl_status.config(foreground="blue")
                    threading._start_new_thread(self.gameStart, ())

                else:
                    self.lbl_status["text"] = "STATUS: " + self.opponent_details["name"] + "'s turn!"
        else:
            self.lbl_status["text"] = "STATUS: Wait for your turn!"
            self.lbl_status.config(foreground="red")

            # send xy coordinate to server to server

    def game_logic(self):
        result = gameRules.check_row(self.list_labels)
        if result[0]:
            return result

        result = gameRules.check_col(self.list_labels, self.num_cols)
        if result[0]:
            return result

        result = gameRules.check_diagonal(self.list_labels, self.num_cols)
        if result[0]:
            return result

        result = gameRules.check_draw(self.list_labels)
        return result


    def connect(self):
        if len(self.ent_name.get()) < 1:
            tk.messagebox.showerror(title="ERROR!!!", message="You MUST enter your first name <e.g. Shimon>")
        else:
            self.your_details["name"] = self.ent_name.get()
            self.connect_to_server(self.ent_name.get())


    def connect_to_server(self, name):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.host_IP, self.port))

            server_publick_key_str = self.client.recv(1024).decode()
            self.server_public_key = eval(server_publick_key_str)
            print(self.server_public_key)

            #Encrypted
            print(name)
            enc_name = RSA.encrypt(self.server_public_key, self.ent_name.get())
            print(enc_name)
            self.client.send(json.dumps(enc_name).encode('utf-8')) 

            # Send name to server after connecting
            # start a thread to keep receiving message from server

            threading._start_new_thread(self.receive_message_from_server, (self.client, "m"))
            self.top_welcome_frame.pack_forget()
            self.top_frame.pack(side=tk.TOP)
            self.window_main.title("Tic-Tac-Toe Client - " + name)
        except Exception as e:
                print('this exception',e)
                tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + self.host_IP + " on port: " + str(
                    self.port) + " Server may be Unavailable. Try again later")
    
    def receive_message_from_server(self, sck, m):
        while True:
            from_server = sck.recv(1024).decode()
            self.client.send(str(self.public_key).encode())

            if not from_server: break

            if from_server.startswith("welcome"):
                if from_server == "welcome1":
                    self.your_details["color"] = "purple"
                    self.opponent_details["color"] = "orange"
                    self.lbl_status["text"] = "Server: Welcome " + self.your_details["name"] + "! Waiting for player 2"
                elif from_server == "welcome2":
                    self.lbl_status["text"] = "Server: Welcome " + self.your_details["name"] + "! Game will start soon"
                    self.your_details["color"] = "orange"
                    self.opponent_details["color"] = "purple"

            elif from_server.startswith("opponent_name$"):
                temp = from_server.replace("opponent_name$", "")
                temp = temp.replace("symbol", "")
                name_index = temp.find("$")
                symbol_index = temp.rfind("$")
                self.opponent_details["name"] = temp[0:name_index]
                self.your_details["symbol"] = temp[symbol_index:len(temp)]

                # set opponent symbol
                if self.your_details["symbol"] == "O":
                    self.opponent_details["symbol"] = "X"
                else:
                    self.opponent_details["symbol"] = "O"

                self.lbl_status["text"] = "STATUS: " + self.opponent_details["name"] + " is connected!"
                sleep(3)
                # is it your turn to play? hey! 'O' comes before 'X'
                if self.your_details["symbol"] == "O":
                    self.lbl_status["text"] = "STATUS: Your turn!"
                    self.your_turn = True
                    self.you_started = True
                else:
                    self.lbl_status["text"] = "STATUS: " + self.opponent_details["name"] + "'s turn!"
                    self.you_started = False
                    self.your_turn = False

            elif from_server.startswith("$xy$"):
                temp = from_server.replace("$xy$", "")
                _x = temp[0:temp.find("$")]
                _y = temp[temp.find("$") + 1:len(temp)]

                # update board
                label_index = int(_x) * self.num_cols + int(_y)
                label = self.list_labels[label_index]
                label["symbol"] = self.opponent_details["symbol"]
                label["label"]["text"] = self.opponent_details["symbol"]
                label["label"].config(foreground=self.opponent_details["color"])
                label["ticked"] = True

                # Does this cordinate leads to a win or a draw
                result = self.game_logic()
                if result[0] is True and result[1] != "":  # opponent win
                    self.opponent_details["score"] = self.opponent_details["score"] + 1
                    if result[1] == self.opponent_details["symbol"]:  #
                        self.lbl_status["text"] = "Game over, You Lost! You(" + str(self.your_details["score"]) + ") - " \
                            "" + self.opponent_details["name"] + "(" + str(self.opponent_details["score"]) + ")"
                        self.lbl_status.config(foreground="red")
                        threading._start_new_thread(self.gameStart, ())
                elif result[0] is True and result[1] == "":  # a draw
                    self.lbl_status["text"] = "Game over, Draw! You(" + str(self.your_details["score"]) + ") - " \
                        "" + self.opponent_details["name"] + "(" + str(self.opponent_details["score"]) + ")"
                    self.lbl_status.config(foreground="blue")
                    threading._start_new_thread(self.gameStart, ())
                else:
                    self.your_turn = True
                    self.lbl_status["text"] = "STATUS: Your turn!"
                    self.lbl_status.config(foreground="black")
        sck.close()

    def run(self):
        self.window_main.mainloop()


if __name__ == "__main__":
    client = TicTacToeClient()
    client.run()
    

# connect and send name to server
# when two player connects, server sends opponent name, symbol
# p1: $name$charles$symbol$O
# client with symbol of O starts
# when client receive opponent position, then it's their turn to play
# check if I win or draw each time I choose play or receive cordinate
