from blaze.expr.reductions import count

import run_game
import numpy as np
import csv
import vars

# global PAWN_WEIGHT
# PAWN_WEIGHT = 1
# global KING_WEIGHT

# vars.a = 1.5
# vars.b = 2
# vars.c = 2
# vars.d = 1
# vars.e = 2
# vars.f = 0
# vars.g = 0
# result = 'tie'
# while result=='tie':
# game = run_game.GameRunner(2, 3, 5, "y", "AI3_204360267_308311356.better_h_player", "simple_player")
# result = game.run()

# if result == "tie":
#     print("it's a tie !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

# a = 1.5
# b = 2
# c = 2
# d = 1
# e = 2



result_dict = {}
a = 1.5
b = 2
c = 2
for f in np.arange(1, 2.5, 0.5):
    for g in np.arange(1, 2.5, 0.5):
        for e in range(1, 3):
            vars.a = a
            vars.b = b
            vars.c = c
            vars.d = 3 - e
            vars.e = e
            vars.f = f
            vars.g = g
            for i in range(1, 5):
                listx = ''.join(
                    [str(a), '|', str(b), '|', str(c), '|', str(3 - e), '|', str(e), '|', str(f), '|', str(g)])
                game = run_game.GameRunner(2, 3, 5, "n", "AI3_204360267_308311356.better_h_player",
                                           "simple_player")
                result = game.run()
                if result != 'tie':
                    result = result[0]
                if listx in result_dict:
                    result_dict[listx][result] += 1
                else:
                    result_dict[listx] = {'red': 0, 'black': 0, 'tie': 0}
                    result_dict[listx][result] += 1


with open('results.csv', 'w', newline='') as out:
    csv_out = csv.writer(out)
    for params_index in result_dict.keys():
        red_res = result_dict[params_index]['red']
        black_res = result_dict[params_index]['black']
        tie_res = result_dict[params_index]['tie']
        row = [params_index, red_res, black_res, tie_res]
        # row = [params_index, 'red', red_res,'black',black_res,'tie',tie_res]
        csv_out.writerow(row)

exit(0)

result_dict = {}
for i in range(10):
    listx = ''.join([str(a), '|', str(b), '|', str(c), '|', str(d), '|', str(e)])
    game = run_game.GameRunner(2, 3, 5, "n", "AI3_204360267_308311356.better_h_player",
                               "simple_player")
    result = game.run()
    if result != 'tie':
        result = result[0]
    if listx in result_dict:
        result_dict[listx][result] += 1
    else:
        result_dict[listx] = {'red': 0, 'black': 0, 'tie': 0}
        result_dict[listx][result] += 1

print(result_dict)

exit(0)

counter = 0

result_dict = {}
for a in np.arange(1, 2.5, 0.5):
    for b in np.arange(1, 2.5, 0.5):
        for c in np.arange(1, 2.5, 0.5):
            for d in np.arange(1, 2.5, 0.5):
                for e in np.arange(1, 2.5, 0.5):
                    vars.a = a
                    vars.b = b
                    vars.c = c
                    vars.d = d
                    vars.e = e
                    for i in range(1, 5):
                        listx = ''.join([str(a), '|', str(b), '|', str(c), '|', str(d), '|', str(e)])
                        game = run_game.GameRunner(2, 3, 5, "n", "AI3_204360267_308311356.better_h_player",
                                                   "simple_player")
                        result = game.run()
                        if result != 'tie':
                            result = result[0]
                        if listx in result_dict:
                            result_dict[listx][result] += 1
                        else:
                            result_dict[listx] = {'red': 0, 'black': 0, 'tie': 0}
                            result_dict[listx][result] += 1
                            #                 break
                            #             break
                            #         break
                            #     break
                            # break

with open('results.csv', 'w', newline='') as out:
    csv_out = csv.writer(out)
    for params_index in result_dict.keys():
        red_res = result_dict[params_index]['red']
        black_res = result_dict[params_index]['black']
        tie_res = result_dict[params_index]['tie']
        row = [params_index, red_res, black_res, tie_res]
        # row = [params_index, 'red', red_res,'black',black_res,'tie',tie_res]
        csv_out.writerow(row)
