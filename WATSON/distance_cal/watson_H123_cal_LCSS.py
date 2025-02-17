import numpy as np
import numba


def calculate_threshold(x, y, T):
    return max(x, y) * T


@numba.njit
def compute_dp_matrix_numba(seq1, seq2, T):
    len_seq1 = len(seq1)
    len_seq2 = len(seq2)
    dp = np.zeros((len_seq1 + 1, len_seq2 + 1), dtype=np.int32)
    for i in range(len_seq1):
        for j in range(len_seq2):
            threshold = max(seq1[i], seq2[j]) * T
            if abs(seq1[i] - seq2[j]) <= threshold:
                dp[i + 1, j + 1] = dp[i, j] + 1
            else:
                dp[i + 1, j + 1] = max(dp[i, j + 1], dp[i + 1, j])
    return dp


@numba.njit
def traceback_lcs(seq1, seq2, dp, T):
    lcs_sum = 0
    lcs_length = 0
    i, j = len(seq1), len(seq2)
    while i > 0 and j > 0:
        x = seq1[i - 1]
        y = seq2[j - 1]
        threshold = max(x, y) * T
        if abs(x - y) <= threshold and dp[i, j] == dp[i - 1, j - 1] + 1:
            lcs_sum += x
            lcs_length += 1
            i -= 1
            j -= 1
        else:
            if dp[i - 1, j] > dp[i, j - 1]:
                i -= 1
            else:
                j -= 1
    return lcs_sum, lcs_length


def batch_greedy_lcs(seq1, seq2_list, T):
    seq1_np = np.array(seq1, dtype=np.float64)
    total_sum_seq1 = np.sum(seq1_np)
    len_seq1 = len(seq1_np)
    sum_seq2_list = [np.sum(seq2) for seq2 in seq2_list]
    similarities = []

    for k, seq2 in enumerate(seq2_list):
        seq2_np = np.array(seq2, dtype=np.float64)
        dp = compute_dp_matrix_numba(seq1_np, seq2_np, T)
        lcs_sum, lcs_length = traceback_lcs(seq1_np, seq2_np, dp, T)

        total_sum_seq2 = sum_seq2_list[k]
        len_seq2 = len(seq2_np)
        bias = max(0.0, 1.0 - abs(total_sum_seq1 - total_sum_seq2) / total_sum_seq1)
        len_sim = min(len_seq1, len_seq2) / max(len_seq1, len_seq2)
        similarity = 1.0 - ((lcs_sum / total_sum_seq1 * bias + lcs_length / len_seq1 * len_sim)) / 2.0
        similarities.append(similarity)

    return np.array(similarities)