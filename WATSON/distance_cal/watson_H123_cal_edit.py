def cal_num_edit_distance(array1, array2_list):
    predict_result = []
    for k in range(len(array2_list)):
        array2 = array2_list[k]
        len1, len2 = len(array1), len(array2)
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        for i in range(len1 + 1):
            for j in range(len2 + 1):
                if i == 0:
                    dp[i][j] = j
                elif j == 0:
                    dp[i][j] = i
                else:
                    cost = abs(array1[i - 1] - array2[j - 1])
                    dp[i][j] = min(dp[i - 1][j] + 1,     # delete
                                   dp[i][j - 1] + 1,     # insert
                                   dp[i - 1][j - 1] + cost)  # replace

        predict_result.append(dp[len1][len2])

    return predict_result