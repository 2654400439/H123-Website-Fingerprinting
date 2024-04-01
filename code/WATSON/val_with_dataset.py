import Distance_Wasserstein
import Distance_LCSS

import random
import yaml
import numpy as np
from tqdm import trange


def read_fingerprint(filename):
    with open('../../dataset/'+filename, 'r') as f:
        data = f.readlines()
    domain = [data[i].split('\t')[0] for i in range(len(data))]
    r_num = [eval(data[i].split('\t')[1]) for i in range(len(data))]
    r_version = [eval(data[i].split('\t')[2]) for i in range(len(data))]

    return domain, r_num, r_version


def main(fingerprint_val, fingerprint_database, W, T):
    domain_val, r_num_val, r_version_val = read_fingerprint(fingerprint_val)
    domain_database, r_num_database, r_version_database = [], [], []
    for fingerprint in fingerprint_database:
        out1, out2, out3 = read_fingerprint(fingerprint)
        domain_database += out1
        r_num_database += out2
        r_version_database += out3

    Wasserstein_weight = W
    LCSS_weight = 1 - W

    flag_right = 0
    for i in trange(len(domain_val)):
        distance_result = []
        for j in range(len(domain_database)):
            wasserstein = Distance_Wasserstein.cal_sorted_wasserstein(r_num_val[i], r_num_database[j], r_version_val[i], r_version_database[j])
            lcss = Distance_LCSS.cal_lcss(r_num_val[i], r_num_database[j], T)
            result = wasserstein * Wasserstein_weight + lcss * LCSS_weight
            distance_result.append(result)

        if domain_val[i] == domain_database[np.argmin(np.array(distance_result))]:
            flag_right += 1
        else:
            pass

    return flag_right / 300


if __name__ == '__main__':
    # load config
    with open('../config.yaml', 'r') as configfile:
        config = yaml.safe_load(configfile)

    W = config['H123_fingerprint']['distance_measurement_weight']
    N = config['H123_fingerprint']['candidate_num']
    T = config['H123_fingerprint']['LCSS_sim_threshold']

    file_list = ['result_' + str(i) + '.txt' for i in range(40)]
    sample_file = random.sample(file_list, N+1)
    fingerprint_database = sample_file[:N]
    fingerprint_val = sample_file[-1]
    print('Used as fingerprint database:\n', fingerprint_database)
    print('Used as new arriving fingerprint:\n', fingerprint_val)

    acc = main(fingerprint_val, fingerprint_database, W, T)
    print('WF ACC: ', acc)