import math
import chess

# this all creates a dictionary mapping the index of a character in the string representation of the board to the
# name of the square e.g index 0 is associated with a8, index 2 b8, ...
index_to_chess_pos = {}
modulus_to_file = {0: "a",
                   2: "b",
                   4: "c",
                   6: "d",
                   8: "e",
                   10: "f",
                   12: "g",
                   14: "h"}
for i in range(128):
    if i % 2 == 0:
        file = modulus_to_file.get(i % 16)
        rank = math.ceil((128 - i) / 16)
        index_to_chess_pos[i] = str(file) + str(rank)


class FogChess:
    def __init__(self):
        self.board = chess.Board()
        self.update_white_board()
        self.update_black_board()

    def update_white_board(self):
        flipped_turn = False
        # self.board.turn is true when it's white's turn and false otherwise
        if not self.board.turn:
            # use null move to make it whites turn so we can see the pseudo_legal moves
            self.board.push(chess.Move.null())
            flipped_turn = True

        visible_squares = set()
        # use pseudo_legal_moves to see where we would be able to move aka what we should see
        for move in self.board.pseudo_legal_moves:
            end_square = str(move)[2:4]
            visible_squares.add(end_square)

        white_board = ""
        for i in range(len(str(self.board))):
            character = str(self.board)[i]
            square = index_to_chess_pos.get(i)
            if character == "\n" or character == " ":
                white_board += character
            # uppercase characters are the white pieces
            elif square in visible_squares or character.isupper():
                white_board += character
            else:
                white_board += "?"

        if flipped_turn:
            # undo the null move
            self.board.pop()

        self.white_board = white_board

    def update_black_board(self):
        flipped_turn = False
        if self.board.turn:
            self.board.push(chess.Move.null())
            flipped_turn = True

        visible_squares = set()
        for move in self.board.pseudo_legal_moves:
            end_square = str(move)[2:4]
            visible_squares.add(end_square)

        black_board = ""
        for i in range(len(str(self.board))):
            character = str(self.board)[i]
            square = index_to_chess_pos.get(i)
            if character == "\n" or character == " ":
                black_board += character
            # lowercase characters are the black pieces
            elif square in visible_squares or character.islower():
                black_board += character
            else:
                black_board += "?"

        if flipped_turn:
            self.board.pop()

        self.black_board = black_board

    def move(self, move):
        self.board.push(move)
        self.update_white_board()
        self.update_black_board()

    def white_wins(self):
        return 'k' not in str(self.board)

    def black_wins(self):
        return 'K' not in str(self.board)


class FogAgent:
    def __init__(self, game, color):
        self.game = game
        self.color = color
        self.update_game(game)
        self.hist = []
        self.possible_hists = [[chess.Board()]]

    def update_game(self, game):
        self.game = game
        if self.color == "white":
            self.board = self.game.white_board
        else:
            self.board = self.game.black_board

    def update_hist(self):
        self.hist.append(self.board)

    def update_after_their_move(self):
        if len(self.hist) > 0:
            possibilities = []
            recents = self.possible_hists[-1]
            for state in recents:
                for move in state.pseudo_legal_moves:
                    new_pos = state.copy()
                    new_pos.push(move)
                    if self.state_is_possible(new_pos):
                        possibilities.append(new_pos)
            self.possible_hists.append(possibilities)

    def update_after_our_move(self, move):
        if len(self.hist) > 0:
            possibilities = []
            recents = self.possible_hists[-1]
            for state in recents:
                new_pos = state.copy()
                new_pos.push(move)
                if self.state_is_possible(new_pos):
                    possibilities.append(new_pos)
            self.possible_hists.append(possibilities)


    def state_is_possible(self, state):
        # state_str is the string representation of the given potential board we're testing
        # self.board is the board visible to the agent

        state_str = str(state)
        for i in range(len(self.board)):
            actual_square = self.board[i]
            potential_square = state_str[i]
            previous_square = self.hist[-1][i]
            # if we can see the square, it should match the true board
            if actual_square != "?":
                if actual_square != potential_square:
                    return False
            if self.color == "white":
                # if a square isn't visible, one of our own pieces can't be there
                if actual_square == "?" and potential_square.isupper():
                    return False
                # if a pawn can't move forward something must be blocking it
                if actual_square == "P" and self.board[i - 16] == "?":
                    if state_str[i - 16] == ".":
                        return False
                # check for en passant
                if actual_square == "P":
                    if self.hist[-1][i - 15] == "?" and self.board[i - 15] == ".":
                        if state_str[i + 1] != "p":
                            return False
                    elif self.hist[-1][i - 17] == "?" and self.board[i - 17] == ".":
                        if state_str[i - 1] != "p":
                            return False

            else:
                if actual_square == "?" and potential_square.islower():
                    return False
                if actual_square == "p" and self.board[i + 16] == "?":
                    if state_str[i + 16] == ".":
                        return False
                # check for en passant
                if actual_square == "p":
                    if self.hist[-1][i + 15] == "?" and self.board[i + 15] == ".":
                        if state_str[i - 1] != "P":
                            return False
                    elif self.hist[-1][i + 17] == "?" and self.board[i + 17] == ".":
                        if state_str[i + 1] != "P":
                            return False
        return True


if __name__ == "__main__":
    fog_game = FogChess()
    agent = FogAgent(fog_game, "black")
    game_not_over = True
    our_last_move = None
    while game_not_over:
        if fog_game.board.turn:
            print(fog_game.white_board)
            agent.update_after_our_move(our_last_move)
            agent.update_hist()
        else:
            print(fog_game.black_board)
            agent.update_after_their_move()
            agent.update_hist()

        if len(agent.possible_hists) > 1:
            possible_last_states = agent.possible_hists[-1]
            print("possible last states: " + str(len(possible_last_states)))

        move_not_made_yet = True
        while move_not_made_yet:
            inp = input("Input move: ")

            move = chess.Move.from_uci(inp)

            if fog_game.board.is_pseudo_legal(move):
                if not fog_game.board.turn:
                    our_last_move = move
                fog_game.move(move)
                agent.update_game(fog_game)
                break
            else:
                print("Illegal move, try again")

        if fog_game.white_wins():
            print("White wins!")
            break
        elif fog_game.black_wins():
            print("Black wins!")
            break



