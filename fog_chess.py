import math
import random
from operator import itemgetter

import chess
from stockfish import Stockfish
import collections
import copy
import time
str_index_to_pst_index = {}

pst_index = 0, 0
for i in range(128):
    if i % 2 == 0:
        str_index_to_pst_index[i] = math.floor(i / 16), int((i % 16) / 2)

def reverse_pst(pst):
    copy = pst.copy()
    copy.reverse()
    return copy


NUM_MOVES_CONSIDERING = 3
NUM_BOARDS_CONSIDERING = 2
DEPTH = 3

start_time = time.perf_counter()
move_time = time.perf_counter()
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

board_heuristics = {}
opp_board_heuristics = {}
moves_to_consider = {}
opp_moves_to_consider = {}
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
        if move:
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
        board_str = board
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
        board_str = board
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
    def opp_attacking_our_pieces(self, board, b):
        opp_moves = set()
        board.push(chess.Move.null())
        for opp_move in board.pseudo_legal_moves:
            opp_moves.add(str(opp_move)[2:4])
        board.pop()

        board_str = b
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
        start_time = time.perf_counter()
        for board in self.possible_hists[-1]:
            opp_heur_vals.append(self.opp_heuristic(board))

        opp_heur_vals.sort()
        top_vals = opp_heur_vals[-NUM_BOARDS_CONSIDERING:]

        top_boards = []
        for board in self.possible_hists[-1]:
            opp_heur = self.opp_heuristic(board)
            if opp_heur in top_vals:
                top_boards.append(board)


        move_values = {}

        for move in self.moves_to_consider(self.game.board):
            move_time = time.perf_counter()
            # print("=======")
            # print(move)
            # print("=======")
            move_values[move] = []
            for board in top_boards:
                copy = board.copy()
                copy.push(move)
                move_values[move].append(self.minimax(copy, DEPTH))
            print("++++++++++++")
            print(f"{move} took {time.perf_counter() - move_time:0.4f} seconds")
            print("++++++++++++")
        top_move = None
        best_val = -1 * float('inf')
        for move in move_values:
            val = max(move_values[move])
            if val > best_val:
                top_move = move
                best_val = val
        print(f"that all took {time.perf_counter() - start_time:0.4f} seconds")
        return top_move

    def move_heuristic(self, move, vis_board):
        move_str = str(move)
        start_square = move_str[0:2]
        end_square = move_str[2:4]

        copy = vis_board.copy()

        copy.push(move)
        copy.push(chess.Move.null())

        copy_game = FogChess(copy)
        if self.color == "white":
            copy_game.update_white_board()
            copy_board = copy_game.white_board
        else:
            copy_game.update_black_board()
            copy_board = copy_game.black_board

        visibility_change = copy_board.count("?") - self.board.count("?")

        # get pieces out of danger
        opponent_visible_pieces_squares = []
        for i in range(0, len(self.board), 2):
            if self.color == "white":
                if self.board[i].islower():
                    opponent_visible_pieces_squares.append(index_to_chess_pos[i])
            else:
                if self.board[i].isupper():
                    opponent_visible_pieces_squares.append(index_to_chess_pos[i])

        material_saved = 0
        copy = self.game.board.copy()
        copy.push(chess.Move.null())

        squares_we_know_opponent_can_attack = set()
        for move in copy.pseudo_legal_moves:
            if move_str[0:2] in opponent_visible_pieces_squares:
                squares_we_know_opponent_can_attack.add(str(move)[2:4])

        for move in copy.pseudo_legal_moves:
            move_str = str(move)
            if move_str[0:2] in opponent_visible_pieces_squares and move_str[2:4] == start_square \
                    and end_square not in squares_we_know_opponent_can_attack:
                parsed_start_square = chess.parse_square(start_square)
                piece = str(copy.piece_at(parsed_start_square))
                if piece.lower() == "p":
                    material_saved = 1
                elif piece.lower() == "b" or piece.lower() == "n":
                    material_saved = 3
                elif piece.lower() == "r":
                    material_saved = 5
                elif piece.lower() == "q":
                    material_saved = 9
                elif piece.lower() == "k":
                    material_saved = 100000000

        captured_material = 0
        parsed_end_square = chess.parse_square(end_square)
        opp_piece = str(self.game.board.piece_at(parsed_end_square))
        if opp_piece != "None":
            if opp_piece.lower() == "p":
                captured_material = 1
            elif opp_piece.lower() == "b" or opp_piece.lower() == "n":
                captured_material = 3
            elif opp_piece.lower() == "r":
                captured_material = 5
            elif opp_piece.lower() == "q":
                captured_material = 9
            elif opp_piece.lower() == "k":
                captured_material = 100000000

        return captured_material * 10 + material_saved * 8 + visibility_change * -2


    def moves_to_consider(self, board):
        vis_board = board.copy()

        new_game = FogChess(board)
        if board.turn:
            our_board = new_game.white_board
        else:
            our_board = new_game.black_board
        if our_board in moves_to_consider:
            return moves_to_consider[our_board]

        for i in range(0, len(our_board), 2):
            if our_board[i] == "?":
                vis_board.remove_piece_at(chess.parse_square(index_to_chess_pos[i]))

        move_scores = {}
        for move in board.pseudo_legal_moves:
            h = self.move_heuristic(move, vis_board)
            move_scores[move] = h
        # print("moves considered")
        moves_to_consider[our_board] = list(dict(sorted(move_scores.items(), key = itemgetter(1), reverse = True)[:NUM_MOVES_CONSIDERING]).keys())
        return moves_to_consider[our_board]

    def minimax(self, board, depth, minimize=True):
        # print("Min" if minimize else "Max")
        moves = []
        if board.turn and self.color == "white" \
                or (not board.turn and self.color == "black"):
            moves = self.moves_to_consider(board)
        else:
            moves = self.moves_to_consider(board)
        if depth > 0:
            heuristic_values = []
            for move in moves:
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
            for move in moves:
                copy = board.copy()
                copy.push(move)
                heuristic_values.append(self.heuristic(copy))
            if minimize:
                return min(heuristic_values)
            else:
                return max(heuristic_values)

    def heuristic(self, board):
        b = str(board)
        if b not in board_heuristics:
            board_heuristics[b] =  100 * self.material_advantage(b) + \
                                   2 * self.piece_square_heuristic(b) + \
                                   10 * self.center_control_hueristic(board)
        return board_heuristics[b]

    def opp_heuristic(self, board):
        b = str(board)
        if b not in opp_board_heuristics:
            opp_board_heuristics[b] =  2 * self.opp_piece_square_heuristic(b) + \
                                       5 * self.center_control_hueristic(board) + \
                                       50 * self.opp_attacking_our_pieces(board, b)
        return opp_board_heuristics[b]



def simulate_game(white_agent, black_agent, game, move_list):
    last_move = None
    for move in move_list:
        # white_agent.update_hist()
        # black_agent.update_hist()
        # if game.board.turn:
        #     game.move(move)
        #     white_agent.update_game(game)
        #     black_agent.update_game(game)
        #     white_agent.update_after_our_move(move)
        #     black_agent.update_after_their_move()
        # else:
        #     game.move(move)
        #     white_agent.update_game(game)
        #     black_agent.update_game(game)
        #     black_agent.update_after_our_move(move)
        #     white_agent.update_after_their_move()
        # white_agent.update_hist()
        # black_agent.update_hist()
        if game.board.turn:
            white_agent.update_after_their_move()
            black_agent.update_after_our_move(last_move)
            white_agent.update_hist()
            black_agent.update_hist()

            best_move = move

            last_move = best_move
            game.move(best_move)
            white_agent.update_game(game)
            black_agent.update_game(game)

        else:
            white_agent.update_after_our_move(last_move)
            black_agent.update_after_their_move()
            white_agent.update_hist()
            black_agent.update_hist()

            best_move = move

            last_move = best_move
            game.move(best_move)
            white_agent.update_game(game)
            black_agent.update_game(game)

def string_list_to_move_list(str_list):
    move_list = []
    for s in str_list:
        move_list.append(chess.Move.from_uci(s))

    return move_list

if __name__ == "__main__":
    game_start_time = time.perf_counter()

    fog_game = FogChess()
    white_agent = FogAgent(fog_game, "white")
    black_agent = FogAgent(fog_game, "black")
    game_not_over = True
    last_move = None

    str_list = ['e2e4', 'e7e5', 'd1f3', 'b8c6', 'd2d3', 'd8h4', 'g2g3', 'h4f6', 'f3f6', 'g8f6',
                'c1g5', 'c6d4', 'g5f6', 'd4c2', 'e1d2', 'c2a1', 'f6e5', 'b7b6', 'd3d4', 'c8a6', 'f1a6', ]

    move_list = [chess.Move.from_uci('e2e4'), chess.Move.from_uci('c7c5')]
    # the board objects are linked for both agents so we only need to call this on one
    simulate_game(white_agent, black_agent, fog_game, move_list)

    last_move = move_list[-1]

    while game_not_over:
        if fog_game.board.turn:
            print(fog_game.white_board)
            white_agent.update_after_their_move()
            black_agent.update_after_our_move(last_move)
            white_agent.update_hist()
            black_agent.update_hist()

            best_move = white_agent.best_move()
            print("==========================")
            print("White's move: " + str(best_move))
            print("==========================")
            last_move = best_move
            fog_game.move(best_move)
            white_agent.update_game(fog_game)
            black_agent.update_game(fog_game)

        else:
            print(fog_game.black_board)
            white_agent.update_after_our_move(last_move)
            black_agent.update_after_their_move()
            white_agent.update_hist()
            black_agent.update_hist()

            best_move = black_agent.best_move()
            print("==========================")
            print("Black's move: " + str(best_move))
            print("==========================")
            last_move = best_move
            fog_game.move(best_move)
            white_agent.update_game(fog_game)
            black_agent.update_game(fog_game)

        if fog_game.white_wins():
            print("White wins!")
            game_end_time = time.perf_counter()
            print(f"Game took {game_end_time - game_start_time:0.4f} seconds")
            break
        elif fog_game.black_wins():
            print("Black wins!")
            game_end_time = time.perf_counter()
            print(f"Game took {game_end_time - game_start_time:0.4f} seconds")
            break




# if __name__ == "__main__":
#     # fewer_pieces_fen = "1nb1kbn1/pppppppp/8/8/8/8/PPPPPPPP/1NB1KBN1 w KQkq - 0 1"
#     # fewer_pieces_board = chess.Board(fewer_pieces_fen)
#     # fog_game = FogChess(fewer_pieces_board)
#     fog_game = FogChess()
#     agent = FogAgent(fog_game, "black")
#     game_not_over = True
#     user_last_move = None
#     agent_last_move = None
#
#     while game_not_over:
#         if fog_game.board.turn:
#             print(fog_game.black_board)
#             print("\n")
#             print(fog_game.white_board)
#             agent.update_after_our_move(agent_last_move)
#             agent.update_hist()
#             move_not_made_yet = True
#         else:
#             # print(fog_game.black_board)
#             agent.update_after_their_move()
#             agent.update_hist()
#
#             best_move = agent.best_move()
#             agent_last_move = best_move
#             fog_game.move(best_move)
#             agent.update_game(fog_game)
#
#             move_not_made_yet = False
#
#         if len(agent.possible_hists) > 1:
#             possible_last_states = agent.possible_hists[-1]
#             # print("possible last states: " + str(len(possible_last_states)))
#
#         while move_not_made_yet:
#             inp = input("Input move: ")
#
#             move = chess.Move.from_uci(inp)
#
#             if fog_game.board.is_pseudo_legal(move):
#                 user_last_move = move
#                 fog_game.move(move)
#                 agent.update_game(fog_game)
#                 break
#             else:
#                 print("Illegal move, try again")
#
#         if fog_game.white_wins():
#             print("White wins!")
#             break
#         elif fog_game.black_wins():
#             print("Black wins!")
#             break