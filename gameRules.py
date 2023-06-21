
class gameRules:
    def check_row(list_labels):
        list_symbols = []
        list_labels_temp = []
        winner = False
        win_symbol = ""
        for i in range(len(list_labels)):
            list_symbols.append(list_labels[i]["symbol"])
            list_labels_temp.append(list_labels[i])
            if (i + 1) % 3 == 0:
                if (list_symbols[0] == list_symbols[1] == list_symbols[2]):
                    if list_symbols[0] != "":
                        winner = True
                        win_symbol = list_symbols[0]

                        list_labels_temp[0]["label"].config(foreground="green", highlightbackground="green",
                                                            highlightcolor="green", highlightthickness=2)
                        list_labels_temp[1]["label"].config(foreground="green", highlightbackground="green",
                                                            highlightcolor="green", highlightthickness=2)
                        list_labels_temp[2]["label"].config(foreground="green", highlightbackground="green",
                                                            highlightcolor="green", highlightthickness=2)

                list_symbols = []
                list_labels_temp = []

        return [winner, win_symbol]


    # [(0,0) -> (1,0) -> (2,0)], [(0,1) -> (1,1) -> (2,1)], [(0,2), (1,2), (2,2)]
    def check_col(list_labels, num_cols):
        winner = False
        win_symbol = ""
        for i in range(num_cols):
            if list_labels[i]["symbol"] == list_labels[i + num_cols]["symbol"] == list_labels[i + num_cols + num_cols][
                "symbol"]:
                if list_labels[i]["symbol"] != "":
                    winner = True
                    win_symbol = list_labels[i]["symbol"]

                    list_labels[i]["label"].config(foreground="green", highlightbackground="green",
                                                highlightcolor="green", highlightthickness=2)
                    list_labels[i + num_cols]["label"].config(foreground="green", highlightbackground="green",
                                                            highlightcolor="green", highlightthickness=2)
                    list_labels[i + num_cols + num_cols]["label"].config(foreground="green", highlightbackground="green",
                                                                        highlightcolor="green", highlightthickness=2)

        return [winner, win_symbol]


    def check_diagonal(list_labels, num_cols):
        winner = False
        win_symbol = ""
        i = 0
        j = 2

        # top-left to bottom-right diagonal (0, 0) -> (1,1) -> (2, 2)
        a = list_labels[i]["symbol"]
        b = list_labels[i + (num_cols + 1)]["symbol"]
        c = list_labels[(num_cols + num_cols) + (i + 1)]["symbol"]
        if list_labels[i]["symbol"] == list_labels[i + (num_cols + 1)]["symbol"] == \
                list_labels[(num_cols + num_cols) + (i + 2)]["symbol"]:
            if list_labels[i]["symbol"] != "":
                winner = True
                win_symbol = list_labels[i]["symbol"]

                list_labels[i]["label"].config(foreground="green", highlightbackground="green",
                                            highlightcolor="green", highlightthickness=2)

                list_labels[i + (num_cols + 1)]["label"].config(foreground="green", highlightbackground="green",
                                                                highlightcolor="green", highlightthickness=2)
                list_labels[(num_cols + num_cols) + (i + 2)]["label"].config(foreground="green",
                                                                            highlightbackground="green",
                                                                            highlightcolor="green", highlightthickness=2)

        # top-right to bottom-left diagonal (0, 0) -> (1,1) -> (2, 2)
        elif list_labels[j]["symbol"] == list_labels[j + (num_cols - 1)]["symbol"] == list_labels[j + (num_cols + 1)][
            "symbol"]:
            if list_labels[j]["symbol"] != "":
                winner = True
                win_symbol = list_labels[j]["symbol"]

                list_labels[j]["label"].config(foreground="green", highlightbackground="green",
                                            highlightcolor="green", highlightthickness=2)
                list_labels[j + (num_cols - 1)]["label"].config(foreground="green", highlightbackground="green",
                                                                highlightcolor="green", highlightthickness=2)
                list_labels[j + (num_cols + 1)]["label"].config(foreground="green", highlightbackground="green",
                                                                highlightcolor="green", highlightthickness=2)
        else:
            winner = False

        return [winner, win_symbol]
    

    # it's a draw if grid is filled
    def check_draw(list_labels):
        for i in range(len(list_labels)):
            if list_labels[i]["ticked"] is False:
                return [False, ""]
        return [True, ""]
