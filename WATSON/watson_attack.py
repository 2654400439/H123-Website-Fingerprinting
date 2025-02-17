import csv
import random
import numpy as np
from distance_cal import watson_H123_cal_wasserstein, watson_H123_cal_LCSS, watson_H123_cal_cosine, watson_H123_cal_edit
import math
from multiprocessing import Pool
import os
from itertools import chain
import yaml
import argparse
import time


def process_file(filename, L):
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        data = [row for row in reader]

    wfp_tmp, httpv_tmp, wfp_key_tmp = [], [], []
    for row in data:
        wfp_tmp.append(eval(row[1])[:L])
        httpv_tmp.append(eval(row[2])[:L])
        wfp_key_tmp.append(row[0])

    return wfp_tmp, httpv_tmp, wfp_key_tmp


def generate_train_test(filelist, L):
    wfp, httpv, wfp_key = [], [], []

    for filename in filelist:
        file_path = "../dataset/H123/" + filename
        wfp_tmp, httpv_tmp, wfp_key_tmp = process_file(file_path, L)
        wfp.append(wfp_tmp)
        httpv.append(httpv_tmp)
        wfp_key.append(wfp_key_tmp)

    return wfp, httpv, wfp_key


def process_chunk(chunk_indices, wfp, httpv, wfp_key, wfp_ref, httpv_ref, wfp_key_ref, config):
    flag_right = 0
    flag_list = []

    weight_sorted_wasserstein = config[1]
    weight_lcss = 1 - weight_sorted_wasserstein

    for flag in chunk_indices:
        wfp_controls = []
        httpv_controls = []
        flag_controls = []

        target_num = wfp[flag]
        up_filter = sum(target_num) + math.ceil(sum(target_num) * 0.2)
        down_filter = sum(target_num) - math.ceil(sum(target_num) * 0.2)
        for i in range(len(wfp_ref)):
            if down_filter <= sum(wfp_ref[i]) <= up_filter:
                wfp_controls.append(wfp_ref[i])
                httpv_controls.append(httpv_ref[i])
                flag_controls.append(wfp_key_ref[i])
        match config[3]:
            case "watson":
                predict_result = weight_lcss * watson_H123_cal_LCSS.batch_greedy_lcs(target_num, wfp_controls, config[2]) + weight_sorted_wasserstein * watson_H123_cal_wasserstein.cal_sorted_wasserstein_matrix(target_num, wfp_controls, httpv[flag], httpv_controls, config[0])
            case "lcss":
                predict_result = watson_H123_cal_LCSS.batch_greedy_lcs(target_num, wfp_controls, config[2])
            case "wasserstein":
                predict_result = watson_H123_cal_wasserstein.cal_sorted_wasserstein_matrix(target_num, wfp_controls, httpv[flag], httpv_controls, config[0])
            case "cosine":
                predict_result = watson_H123_cal_cosine.cal_cosine_easy(target_num, wfp_controls, config[0])
            case "edit":
                predict_result = watson_H123_cal_edit.cal_num_edit_distance(target_num, wfp_controls)
            case _:
                predict_result = []
        if wfp_key[flag] == flag_controls[np.argmin(np.array(predict_result))]:
            flag_right += 1
            flag_list.append(1)
        else:
            flag_list.append(0)
    return flag_right, flag_list


def main(file, train_file, config: list):
    # Get the number of CPU cores in the system. You can adjust this if needed.
    num_processes = os.cpu_count()

    # Generate training(reference) and testing data
    wfp, httpv, wfp_key = generate_train_test([file] + train_file, config[0])

    # Treat the first file as the test set, and others as reference sets
    wfp_test = wfp[0]
    wfp_ref = list(chain(*wfp[1:]))  # Flatten the reference data for efficient processing
    httpv_test = httpv[0]
    httpv_ref = list(chain(*httpv[1:]))
    wfp_key_test = wfp_key[0]
    wfp_key_ref = list(chain(*wfp_key[1:]))

    num_tests = len(wfp_test)  # Total number of test samples
    chunk_size = (num_tests + num_processes - 1) // num_processes  # Divide test samples into chunks

    # Create chunks for parallel processing using a generator expression to avoid storing large lists
    chunks = (range(i * chunk_size, min((i + 1) * chunk_size, num_tests)) for i in range(num_processes))

    # Start a multiprocessing pool to process the chunks in parallel
    with Pool(processes=num_processes) as pool:
        results = pool.starmap(process_chunk,
                              [(chunk, wfp_test, httpv_test, wfp_key_test, wfp_ref, httpv_ref, wfp_key_ref, config)
                               for chunk in chunks])

    # Aggregate the results and calculate the accuracy (correct flags)
    total_flag_right = sum(result[0] for result in results)
    accuracy = total_flag_right / num_tests
    return accuracy


if __name__ == '__main__':
    # load config
    with open('../config.yaml', 'r') as configfile:
        config = yaml.safe_load(configfile)
    L = config['H123_fingerprint']['max_len']
    W = config['H123_fingerprint']['distance_measurement_weight']
    T = config['H123_fingerprint']['LCSS_sim_threshold']

    parser = argparse.ArgumentParser(description='This script processes parameters with N and distance.')
    parser.add_argument('--N', type=int, choices=range(1, 40), default=1,
                        help='An integer N, which must be between 1 and 39 inclusive.')
    parser.add_argument('--distance', type=str, choices=['watson', 'lcss', 'wasserstein', 'cosine', 'edit'],
                        default='watson', help='Distance measure, which can be one of: lcss, wasserstein, cosine.')
    args = parser.parse_args()

    N = args.N
    distance = args.distance

    file_list = ['result_' + str(i) + '.csv' for i in range(1, 41)]
    sample_file = random.sample(file_list, N+1)

    fingerprint_database = sample_file[:N]
    fingerprint_val = sample_file[-1]
    print('Used as fingerprint database:\n', fingerprint_database)
    print('Used as new arriving fingerprint:\n', fingerprint_val)

    start = time.time()
    acc = main(fingerprint_val, fingerprint_database, [L, W, T, distance])
    print('WF ACC: ', acc)
    end = time.time()
    print('Total time: ', end - start)