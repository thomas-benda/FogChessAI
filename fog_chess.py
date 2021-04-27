import math
import random

import chess
from stockfish import Stockfish
import collections
import copy

str_index_to_pst_index = {}

pst_index = 0, 0
for i in range(128):
    if i % 2 == 0:
        str_index_to_pst_index[i] = math.floor(i / 16), int((i % 16) / 2)

def reverse_pst(pst):
    copy = pst.copy()
    copy.reverse()
    return copy


pawnEvalWhite =[[0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
    [5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0],
    [1.0,  1.0,  2.0,  3.0,  3.0,  2.0,  1.0,  1.0],
    [0.5,  0.5,  1.0,  2.5,  2.5,  1.0,  0.5,  0.5],
    [0.0,  0.0,  0.0,  2.0,  2.0,  0.0,  0.0,  0.0],
    [0.5, -0.5, -1.0,  0.0,  0.0, -1.0, -0.5,  0.5],
    [0.5,  1.0, 1.0,  -2.0, -2.0,  1.0,  1.0,  0.5],
    [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0]
]

pawnEvalBlack = reverse_pst(pawnEvalWhite)

knightEval = [
    [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
    [-4.0, -2.0,  0.0,  0.0,  0.0,  0.0, -2.0, -4.0],
    [-3.0,  0.0,  1.0,  1.5,  1.5,  1.0,  0.0, -3.0],
    [-3.0,  0.5,  1.5,  2.0,  2.0,  1.5,  0.5, -3.0],
    [-3.0,  0.0,  1.5,  2.0,  2.0,  1.5,  0.0, -3.0],
    [-3.0,  0.5,  1.0,  1.5,  1.5,  1.0,  0.5, -3.0],
    [-4.0, -2.0,  0.0,  0.5,  0.5,  0.0, -2.0, -4.0],
    [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
]

bishopEvalWhite = [
    [ -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
    [ -1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
    [ -1.0,  0.0,  0.5,  1.0,  1.0,  0.5,  0.0, -1.0],
    [ -1.0,  0.5,  0.5,  1.0,  1.0,  0.5,  0.5, -1.0],
    [ -1.0,  0.0,  1.0,  1.0,  1.0,  1.0,  0.0, -1.0],
    [ -1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0, -1.0],
    [ -1.0,  0.5,  0.0,  0.0,  0.0,  0.0,  0.5, -1.0],
    [ -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
]

bishopEvalBlack = reverse_pst(bishopEvalWhite)

rookEvalWhite = [
    [  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
    [  0.5,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  0.5],
    [ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
    [ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
    [ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
    [ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
    [ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
    [  0.0,   0.0, 0.0,  0.5,  0.5,  0.0,  0.0,  0.0]
]

rookEvalBlack = reverse_pst(rookEvalWhite)

evalQueen = [
    [ -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
    [ -1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
    [ -1.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0],
    [ -0.5,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5],
    [  0.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5],
    [ -1.0,  0.5,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0],
    [ -1.0,  0.0,  0.5,  0.0,  0.0,  0.0,  0.0, -1.0],
    [ -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]
]

kingEvalWhite = [

    [ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [ -2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
    [ -1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
    [  2.0,  2.0,  0.0,  0.0,  0.0,  0.0,  2.0,  2.0 ],
    [  2.0,  3.0,  1.0,  0.0,  0.0,  1.0,  3.0,  2.0 ]
]

kingEvalBlack = reverse_pst(kingEvalWhite)
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

# keeps track of the actual game
class FogChess:
    def __init__(self, board=None):
        # what the board actually is
        if board:
            self.board = board
        else:
            self.board = chess.Board()
        # what white sees
        self.update_white_board()
        # what black sees
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
        self.hist = []
        self.possible_hists = [[game.board.copy()]]
        self.update_game(game)

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

    # def stockfish_heuristic(self, board):
    #     move_stack = board.move_stack
    #     list_of_moves = []
    #     for move in move_stack:
    #         list_of_moves.append(str(move))
    #
    #     stockfish = Stockfish()
    #     stockfish.set_position(list_of_moves)
    #
    #     eval = stockfish.get_evaluation()
    #
    #     if self.color == "white":
    #         if eval.get("type") == "cp":
    #             return eval.get("value")
    #         else:
    #             return 50
    #
    #     else:
    #         if eval.get("type") == "cp":
    #             return -1 * eval.get("value")
    #         else:
    #             return 50

    def piece_square_heuristic(self, board):
        board_str = str(board)
        board_score = 0
        if self.color == "white":
            for i in range(0, len(board_str), 2):
                square = board_str[i]
                if square.isupper():
                    pst_row = str_index_to_pst_index[i][0]
                    pst_col = str_index_to_pst_index[i][1]
                    if square == "P":
                        board_score += pawnEvalWhite[pst_row][pst_col]
                    elif square == "N":
                        board_score += knightEval[pst_row][pst_col]
                    elif square == "B":
                        board_score += bishopEvalWhite[pst_row][pst_col]
                    elif square == "R":
                        board_score += rookEvalWhite[pst_row][pst_col]
                    elif square == "Q":
                        board_score += evalQueen[pst_row][pst_col]
                    elif square == "K":
                        board_score += kingEvalWhite[pst_row][pst_col]
        elif self.color == "black":
            for i in range(0, len(board_str), 2):
                square = board_str[i]
                if square.islower():
                    pst_row = str_index_to_pst_index[i][0]
                    pst_col = str_index_to_pst_index[i][1]
                    if square == "p":
                        board_score += pawnEvalBlack[pst_row][pst_col]
                    elif square == "n":
                        board_score += knightEval[pst_row][pst_col]
                    elif square == "b":
                        board_score += bishopEvalBlack[pst_row][pst_col]
                    elif square == "r":
                        board_score += rookEvalBlack[pst_row][pst_col]
                    elif square == "q":
                        board_score += evalQueen[pst_row][pst_col]
                    elif square == "k":
                        board_score += kingEvalBlack[pst_row][pst_col]

        return board_score

    def opp_piece_square_heuristic(self, board):
        board_str = str(board)
        board_score = 0
        if self.color == "black":
            for i in range(0, len(board_str), 2):
                square = board_str[i]
                if square.isupper():
                    pst_row = str_index_to_pst_index[i][0]
                    pst_col = str_index_to_pst_index[i][1]
                    if square == "P":
                        board_score += pawnEvalWhite[pst_row][pst_col]
                    elif square == "N":
                        board_score += knightEval[pst_row][pst_col]
                    elif square == "B":
                        board_score += bishopEvalWhite[pst_row][pst_col]
                    elif square == "R":
                        board_score += rookEvalWhite[pst_row][pst_col]
                    elif square == "Q":
                        board_score += evalQueen[pst_row][pst_col]
                    elif square == "K":
                        board_score += kingEvalWhite[pst_row][pst_col]
        elif self.color == "white":
            for i in range(0, len(board_str), 2):
                square = board_str[i]
                if square.islower():
                    pst_row = str_index_to_pst_index[i][0]
                    pst_col = str_index_to_pst_index[i][1]
                    if square == "p":
                        board_score += pawnEvalBlack[pst_row][pst_col]
                    elif square == "n":
                        board_score += knightEval[pst_row][pst_col]
                    elif square == "b":
                        board_score += bishopEvalBlack[pst_row][pst_col]
                    elif square == "r":
                        board_score += rookEvalBlack[pst_row][pst_col]
                    elif square == "q":
                        board_score += evalQueen[pst_row][pst_col]
                    elif square == "k":
                        board_score += kingEvalBlack[pst_row][pst_col]

        return board_score

    def center_control_hueristic(self, board):
        center_ctrl_count = 0
        center_spaces = ['d4', 'd5', 'e4', 'e5']
        pieces_in_center = set()
        # make move list from our perspective, not the opponents
        board.push(chess.Move.null())

        for move in board.pseudo_legal_moves:
            if str(move)[0:2] in center_spaces:
                pieces_in_center.add(str(move)[0:2])
            if str(move)[2:4] in center_spaces:
                center_ctrl_count += 1

        board.pop()

        return center_ctrl_count + 5 * len(pieces_in_center)

    def material_advantage(self, board):
        board_str = str(board)
        advantage = 0
        for i in range(0, len(board_str), 2):
            square = board_str[i]
            if square == "P":
                advantage += 1
            elif square == "N" or square == "B":
                advantage += 3
            elif square == "R":
                advantage += 5
            elif square == "Q":
                advantage += 9
            elif square == "K":
                advantage += 100
            elif square == "p":
                advantage -= 1
            elif square == "n" or square == "b":
                advantage -= 3
            elif square == "r":
                advantage -= 5
            elif square == "q":
                advantage -= 9
            elif square == "k":
                advantage -= 100

        # originally calculated for white, flip if black
        if self.color == "black":
            advantage *= -1

        return advantage

    # returns a negative value because being under attack is bad
    def pieces_under_attack(self, board):
        opp_moves = set()
        for opp_move in board.pseudo_legal_moves:
            opp_moves.add(str(opp_move)[2:4])

        board_str = str(board)
        under_attack = 0
        for i in range(0, len(board_str), 2):
            if index_to_chess_pos[i] in opp_moves:
                square = board_str[i]
                if self.color == "white":
                    if square == "P":
                        under_attack -= 1 ** 2
                    elif square == "N" or square == "B":
                        under_attack -= 3 ** 2
                    elif square == "R":
                        under_attack -= 5 ** 2
                    elif square == "Q":
                        under_attack -= 9 ** 2
                    elif square == "K":
                        under_attack -= 100 ** 2
                else:
                    if square == "p":
                        under_attack -= 1 ** 2
                    elif square == "n" or square == "b":
                        under_attack -= 3 ** 2
                    elif square == "r":
                        under_attack -= 5 ** 2
                    elif square == "q":
                        under_attack -= 9 ** 2
                    elif square == "k":
                        under_attack -= 100 ** 2

        return under_attack

    # returns a negative value because being under attack is bad
    def opp_attacking_our_pieces(self, board):
        opp_moves = set()
        board.push(chess.Move.null())
        for opp_move in board.pseudo_legal_moves:
            opp_moves.add(str(opp_move)[2:4])
        board.pop()

        board_str = str(board)
        under_attack = 0
        for i in range(0, len(board_str), 2):
            if index_to_chess_pos[i] in opp_moves:
                square = board_str[i]
                if self.color == "white":
                    if square == "P":
                        under_attack += 1 ** 2
                    elif square == "N" or square == "B":
                        under_attack += 3 ** 2
                    elif square == "R":
                        under_attack += 5 ** 2
                    elif square == "Q":
                        under_attack += 9 ** 2
                    elif square == "K":
                        under_attack += 100 ** 2
                else:
                    if square == "p":
                        under_attack += 1 ** 2
                    elif square == "n" or square == "b":
                        under_attack += 3 ** 2
                    elif square == "r":
                        under_attack += 5 ** 2
                    elif square == "q":
                        under_attack += 9 ** 2
                    elif square == "k":
                        under_attack += 100 ** 2
        return under_attack

    def board_visibility_heuristic(self, board):
        vis_set = set()
        board.push(chess.Move.null())
        for move in board.pseudo_legal_moves:
            vis_set.add(str(move)[0:2])
            vis_set.add(str(move)[2:4])
        board.pop()
        return len(vis_set)

    def combined_heuristic(self, board):
        h = 20 * self.pieces_under_attack(board) + \
            5 * self.board_visibility_heuristic(board)

        return h

    def best_move(self):
        opp_heur_vals = []
        for board in self.possible_hists[-1]:
            opp_heur_vals.append(self.opp_heuristic(board))

        opp_heur_vals.sort()
        top_vals = opp_heur_vals[-10:]

        top_boards = []
        for board in self.possible_hists[-1]:
            opp_heur = self.opp_heuristic(board)
            if opp_heur in top_vals:
                top_boards.append(board)


        move_values = {}

        for move in self.game.board.pseudo_legal_moves:
            print(move)
            move_values[move] = []
            # # some heuristics don't care about the opponents pieces whatsoever
            # copy = self.game.board.copy()
            # copy.push(move)
            # heur = len(self.possible_hists[-1]) * \
            #        (20 * self.material_advantage(copy) +
            #         2 * self.piece_square_heuristic(copy) +
            #         5 * self.center_control_hueristic(copy))
            # move_values[move] = heur
            for board in top_boards:
                copy = board.copy()
                copy.push(move)
                # heur = self.combined_heuristic(copy)
                # move_values[move] += heur
                move_values[move].append(self.minimax(copy, 1))

        top_move = None
        best_val = -1 * float('inf')
        for move in move_values:
            val = max(move_values[move])
            if val > best_val:
                top_move = move
                best_val = val

        return top_move

        # best_score = max(move_values.values())
        # good_moves = []
        # for key in move_values:
        #     if move_values[key] == best_score:
        #         good_moves.append(key)
        #
        # random.shuffle(good_moves)
        #
        # return good_moves[0]

    def minimax(self, board, depth, minimize=True):
        if depth > 0:
            heuristic_values = []
            for move in board.pseudo_legal_moves:
                copy = board.copy()
                copy.push(move)
                if minimize:
                    heuristic_values.append(self.minimax(copy, depth - 1, not minimize))
                else:
                    heuristic_values.append(self.minimax(copy, depth - 1, not minimize))
            if minimize:
                return min(heuristic_values)
            else:
                return max(heuristic_values)

        else:
            heuristic_values = []
            for move in board.pseudo_legal_moves:
                copy = board.copy()
                copy.push(move)
                heuristic_values.append(self.heuristic(copy))
            if minimize:
                return min(heuristic_values)
            else:
                return max(heuristic_values)

    def heuristic(self, board):
        return 100 * self.material_advantage(board) + \
                2 * self.piece_square_heuristic(board) + \
                10 * self.center_control_hueristic(board)

    def opp_heuristic(self, board):
        return 2 * self.opp_piece_square_heuristic(board) + \
               5 * self.center_control_hueristic(board) + \
               50 * self.opp_attacking_our_pieces(board)



if __name__ == "__main__":
    fewer_pieces_fen = "1nb1kbn1/pppppppp/8/8/8/8/PPPPPPPP/1NB1KBN1 w KQkq - 0 1"
    fewer_pieces_board = chess.Board(fewer_pieces_fen)
    fog_game = FogChess(fewer_pieces_board)
    # fog_game = FogChess()
    agent = FogAgent(fog_game, "black")
    game_not_over = True
    user_last_move = None
    agent_last_move = None
    while game_not_over:
        if fog_game.board.turn:
            print(fog_game.black_board)
            print("\n")
            print(fog_game.white_board)
            agent.update_after_our_move(agent_last_move)
            agent.update_hist()
            move_not_made_yet = True
        else:
            # print(fog_game.black_board)
            agent.update_after_their_move()
            agent.update_hist()

            best_move = agent.best_move()
            agent_last_move = best_move
            fog_game.move(best_move)
            agent.update_game(fog_game)

            move_not_made_yet = False

        if len(agent.possible_hists) > 1:
            possible_last_states = agent.possible_hists[-1]
            # print("possible last states: " + str(len(possible_last_states)))

        while move_not_made_yet:
            inp = input("Input move: ")

            move = chess.Move.from_uci(inp)

            if fog_game.board.is_pseudo_legal(move):
                user_last_move = move
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
