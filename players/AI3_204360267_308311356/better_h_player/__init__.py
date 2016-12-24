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

        opponent_state = copy.deepcopy(state)
        opponent_state.curr_player = opponent_color

        # considering threats for both players
        current_player_possible_moves = state.get_possible_moves()
        opponent_player_possible_moves = opponent_state.get_possible_moves()
        current_player_threats = state.calc_capture_moves()
        opponent_player_threats = opponent_state.calc_capture_moves()
        # current_jumps_count = 0
        # opponent_jumps_count = 0
        # for game_move in current_player_possible_moves:
        #     if game_move.jumped_locs:
        #         current_jumps_count += len(game_move.jumped_locs)
        # for game_move in opponent_player_possible_moves:
        #     if game_move.jumped_locs:
        #         opponent_jumps_count += len(game_move.jumped_locs)
        # threat_heuristic = current_jumps_count - opponent_jumps_count
        threat_heuristic = len(current_player_threats) - len(opponent_player_threats)

        # considering available single moves for both players
        # current_player_single_moves = state.calc_single_moves()
        # opponent_player_single_moves = opponent_state.calc_single_moves()
        # single_moves_heuristic = len(current_player_single_moves) - len(opponent_player_single_moves)

        # considering distance of soon to be kings pawns for both players
        current_player_princes_avg = 0.0
        current_player_princes_count = 0
        opponent_player_princes_avg = 0.0
        opponent_player_princes_count = 0
        for (i, j), loc_val in state.board.items():
            if loc_val == RP and BOARD_ROWS - i < 5:
                if PAWN_COLOR[self.color] == RP:
                    current_player_princes_avg = (current_player_princes_avg * current_player_princes_count + i - 3) / (
                        current_player_princes_count + 1)
                    current_player_princes_count += 1

                else:
                    opponent_player_princes_avg = (
                                                      opponent_player_princes_avg * opponent_player_princes_count + i - 3) / (
                                                      opponent_player_princes_count + 1)
                    opponent_player_princes_count += 1
            if loc_val == BP and BOARD_ROWS - i > 4:
                if PAWN_COLOR[self.color] == BP:
                    current_player_princes_avg = (current_player_princes_avg * current_player_princes_count + 4 - i) / (
                        current_player_princes_count + 1)
                    current_player_princes_count += 1
                else:
                    opponent_player_princes_avg = (
                                                      opponent_player_princes_avg * opponent_player_princes_count + 4 - i) / (
                                                      opponent_player_princes_count + 1)
                    opponent_player_princes_count += 1

        dominance_heuristic = current_player_princes_avg - opponent_player_princes_avg

        return basic_heuristic

    def selective_deepening_criterion(self, state):
        # Simple player does not selectively deepen into certain nodes.
        return False

    def no_more_time(self):
        return (time.process_time() - self.clock) >= self.time_for_current_move

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'simple')

# c:\python35\python.exe run_game.py 3 3 3 y simple_player random_player
