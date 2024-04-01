
def calculate_threshold(x, y, sim_threshold):
    return float(max(x, y) * sim_threshold)


def cal_lcss(seq1, seq2, sim_threshold):
    len_seq1, len_seq2 = len(seq1), len(seq2)

    dp = [[0] * (len_seq2 + 1) for _ in range(len_seq1 + 1)]

    for i in range(1, len_seq1 + 1):
        for j in range(1, len_seq2 + 1):
            threshold = calculate_threshold(seq1[i - 1], seq2[j - 1], sim_threshold)
            if abs(seq1[i - 1] - seq2[j - 1]) <= threshold:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    i, j = len_seq1, len_seq2
    lcs = []
    while i > 0 and j > 0:
        threshold = calculate_threshold(seq1[i - 1], seq2[j - 1], sim_threshold)
        if abs(seq1[i - 1] - seq2[j - 1]) <= threshold:
            lcs.insert(0, seq1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    bias = 1 - abs((sum(seq1) - sum(seq2))) / sum(seq1) if abs((sum(seq1) - sum(seq2))) / sum(seq1) < 1 else 0
    len_sim = min(len(seq1), len(seq2)) / max(len(seq1), len(seq2))
    lcs_sum = sum(lcs) if sum(lcs) < sum(seq1) else sum(seq1)
    return 1 - (lcs_sum / sum(seq1) * bias + len(lcs) / len(seq1) * len_sim) / 2