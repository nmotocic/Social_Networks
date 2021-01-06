import numpy as np
import sys


def get_adv_val(user_item, user_avg, item_avg, param):
    I, J, K = param
    I -= 1
    J -= 1
    sims = {}
    for col_num, col in enumerate(user_avg):
        if not col == user_avg[J]:
            numer = 0
            denom_1, denom_2 = 0, 0
            for i in range(len(col)):
                numer += user_avg[J][i] * col[i]
                denom_1 += user_avg[J][i] * user_avg[J][i]
                denom_2 += col[i] * col[i]                
            sim = numer / (np.sqrt(denom_1) * np.sqrt(denom_2))
            if sim >= 0 and not user_item[I][col_num] == 'X':
                sims[col_num] = sim
    rating = 0
    sum_of_sims = 0
    for n in sims:
        rating += float(int(user_item[I][n]) * sims[n])
        sum_of_sims += sims[n]
    if sum_of_sims > 0:
        rating /= sum_of_sims
    return rating


def get_recommendations(matrix):
    line_index = 0
    user_item = []
    item_avg = []
    user_avg = []

    predictions = {}
    for line in matrix:
        if line_index == 0:
            M = int(line.split(" ")[0])
            N = int(line.split(" ")[1])
        elif line_index < M + 1:
            user_item.append(line.rstrip().split(" "))
            row = line.rstrip().split(" ")
            row = [0 if x == 'X' else int(x) for x in row]
            avg = 0
            if not np.count_nonzero(row) == 0:
                avg = sum(row) / np.count_nonzero(row)
            for i in range(len(row)):
                if not row[i] == 0:
                    row[i] = float(row[i] - avg)
            item_avg.append(row)
        elif line_index == M + 1:
            item_user = np.transpose(user_item)
            for row in np.transpose(user_item):
                row = [0 if x == 'X' else int(x) for x in row]
                avg = 0
                if not np.count_nonzero(row) == 0:
                    avg = sum(row) / np.count_nonzero(row)
                for i in range(len(row)):
                    if not row[i] == 0:
                        row[i] = float(row[i] - avg)
                user_avg.append(row)
            Q = int(line)
            counter = 0
        elif M + 1 < line_index < M + Q + 2:
            prediction = get_adv_val(user_item, user_avg, item_avg, list(map(int, line.rstrip().split(" "))))
            movie = int(line.rstrip().split(" ")[1])
            predictions[int(line.rstrip().split(" ")[1])] = prediction - 1
            counter += 1
        line_index += 1
    return dict(sorted(predictions.items(), key=lambda item: item[1], reverse=True))


