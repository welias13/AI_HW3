# ===============================================================================
# Imports
# ===============================================================================

import abstract
from utils import MiniMaxWithAlphaBetaPruning, INFINITY, run_with_limited_time, ExceededTimeError
# from checkers.consts import EM, PAWN_COLOR, KING_COLOR, OPPONENT_COLOR, MAX_TURNS_NO_JUMP, RP, BP
import time
from collections import defaultdict

##
import copy
from checkers.consts import *

from checkers.moves import TOOL_CAPTURE_MOVES

# ===============================================================================
# Globals
# ===============================================================================

import vars

PAWN_WEIGHT = 1
KING_WEIGHT = 1.5


# ===============================================================================
# Player
# ===============================================================================

class Player(abstract.AbstractPlayer):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        abstract.AbstractPlayer.__init__(self, setup_time, player_color, time_per_k_turns, k)
        self.clock = time.process_time()

        # We are simply providing (remaining time / remaining turns) for each turn in round.
        # Taking a spare time of 0.05 seconds.
        self.turns_remaining_in_round = self.k
        self.time_remaining_in_round = self.time_per_k_turns
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05

    def get_move(self, game_state, possible_moves):
        self.clock = time.process_time()
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05
        if len(possible_moves) == 1:
            return possible_moves[0]

        current_depth = 1
        prev_alpha = -INFINITY

        # Choosing an arbitrary move in case Minimax does not return an answer:
        best_move = possible_moves[0]

        # Initialize Minimax algorithm, still not running anything
        minimax = MiniMaxWithAlphaBetaPruning(self.utility, self.color, self.no_more_time,
                                              self.selective_deepening_criterion)

        # Iterative deepening until the time runs out.
        while True:

            print('going to depth: {}, remaining time: {}, prev_alpha: {}, best_move: {}'.format(
                current_depth,
                self.time_for_current_move - (time.process_time() - self.clock),
                prev_alpha,
                best_move))

            try:
                (alpha, move), run_time = run_with_limited_time(
                    minimax.search, (game_state, current_depth, -INFINITY, INFINITY, True), {},
                    self.time_for_current_move - (time.process_time() - self.clock))
            except (ExceededTimeError, MemoryError):
                print('no more time, achieved depth {}'.format(current_depth))
                break

            if self.no_more_time():
                print('no more time')
                break

            prev_alpha = alpha
            best_move = move

            if alpha == INFINITY:
                print('the move: {} will guarantee victory.'.format(best_move))
                break

            if alpha == -INFINITY:
                print('all is lost')
                break

            current_depth += 1

        if self.turns_remaining_in_round == 1:
            self.turns_remaining_in_round = self.k
            self.time_remaining_in_round = self.time_per_k_turns
        else:
            self.turns_remaining_in_round -= 1
            self.time_remaining_in_round -= (time.process_time() - self.clock)
        return best_move

    def utility(self, state):
        if len(state.get_possible_moves()) == 0:
            return INFINITY if state.curr_player != self.color else -INFINITY
        if state.turns_since_last_jump >= MAX_TURNS_NO_JUMP:
            return 0

        piece_counts = defaultdict(lambda: 0)
        for loc_val in state.board.values():
            if loc_val != EM:
                piece_counts[loc_val] += 1

        opponent_color = OPPONENT_COLOR[self.color]

        my_u = ((PAWN_WEIGHT * piece_counts[PAWN_COLOR[self.color]]) +
                (KING_WEIGHT * piece_counts[KING_COLOR[self.color]]))
        op_u = ((PAWN_WEIGHT * piece_counts[PAWN_COLOR[opponent_color]]) +
                (KING_WEIGHT * piece_counts[KING_COLOR[opponent_color]]))
        if my_u == 0:
            # I have no tools left
            return -INFINITY
        elif op_u == 0:
            # The opponent has no tools left
            return INFINITY

        basic_heuristic = my_u - op_u

        if self.color == BLACK_PLAYER:
            id_dict = {BP : 1 , BK : 1 , RP : -1, RK : -1, EM : 0}
        else:
            id_dict = {BP: -1, BK: -1, RP: 1, RK: 1, EM: 0}

        safe_pawns_heuristic = 0
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if (i == 0 or j==0 or i==7 or j==7) and IS_BLACK_TILE((i, j)):
                    safe_pawns_heuristic += id_dict[state.board[(i,j)]]


        attack_heuristic = 0
        for i in range(3):
            for j in range(BOARD_COLS):
                if IS_BLACK_TILE((i, j)) and state.board[(i,j)] == BP:
                    attack_heuristic += id_dict[state.board[(i,j)]]

        for i in range(3):
            cur_i = BOARD_ROWS - i - 1
            for j in range(BOARD_COLS):
                if IS_BLACK_TILE((cur_i, j)) and state.board[(cur_i,j)] == RP:
                    attack_heuristic += id_dict[state.board[(cur_i, j)]]

        central_pawns_heuristic = 0
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if (i == 3 or i==4) and IS_BLACK_TILE((i, j)):
                    central_pawns_heuristic += id_dict[state.board[(i,j)]]

        central_kings_heuristic = 0
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if (i == 3 or i == 4) and IS_BLACK_TILE((i, j)):
                    central_kings_heuristic += id_dict[state.board[(i, j)]]

        double_diagonal_heuristic = 0
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if (i+j == 8 or i+j == 6) and IS_BLACK_TILE((i, j)):
                    double_diagonal_heuristic += id_dict[state.board[(i,j)]]

        triangle_heuristic = 0
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if (j + 2 < BOARD_COLS and i + 1 < BOARD_ROWS) and IS_BLACK_TILE((i, j)):
                    if state.board[(i, j)] in MY_COLORS[RED_PLAYER] and state.board[(i, j+2)] in MY_COLORS[RED_PLAYER] and state.board[(i+1, j+1)] in MY_COLORS[RED_PLAYER]:
                        triangle_heuristic += id_dict[state.board[(i,j)]]
                if (j + 2 < BOARD_COLS and i - 1 >= 0) and IS_BLACK_TILE((i, j)):
                    if state.board[(i, j)] in MY_COLORS[BLACK_PLAYER] and state.board[(i, j + 2)] in MY_COLORS[BLACK_PLAYER] and state.board[(i - 1, j + 1)] in MY_COLORS[BLACK_PLAYER]:
                        triangle_heuristic += id_dict[state.board[(i, j)]]

        return vars.a*basic_heuristic + vars.b*safe_pawns_heuristic + vars.c*attack_heuristic + vars.d*central_pawns_heuristic + vars.e*central_kings_heuristic + vars.f*double_diagonal_heuristic + vars.g*triangle_heuristic

    def selective_deepening_criterion(self, state):
        # Simple player does not selectively deepen into certain nodes.
        return False

    def no_more_time(self):
        return (time.process_time() - self.clock) >= self.time_for_current_move

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'simple')

# c:\python35\python.exe run_game.py 3 3 3 y simple_player random_player
