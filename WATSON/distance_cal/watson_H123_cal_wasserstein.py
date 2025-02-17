import numpy as np


def process_resource_num(resource_num, resource_httpv, L):
    http1_mask = np.array([1 if item == 'http/1.1' else 0 for item in resource_httpv])
    http2_mask = np.array([1 if item == 'h2' else 0 for item in resource_httpv])
    http3_mask = np.array([1 if item == 'h3' else 0 for item in resource_httpv])

    http1_num = np.sort(resource_num[http1_mask == 1]) if np.sum(http1_mask) != 0 else np.array([0])
    http2_num = np.sort(resource_num[http2_mask == 1]) if np.sum(http2_mask) != 0 else np.array([0])
    http3_num = np.sort(resource_num[http3_mask == 1]) if np.sum(http3_mask) != 0 else np.array([0])

    http1_num = np.concatenate((np.zeros(L - len(http1_num)), http1_num))
    http2_num = np.concatenate((np.zeros(L - len(http2_num)), http2_num))
    http3_num = np.concatenate((np.zeros(L - len(http3_num)), http3_num))

    return http1_num, http2_num, http3_num


def cal_sorted_wasserstein_matrix(resource_num_1, resource_num_controls, resource_httpv_1, resource_httpv_controls, L):
    resource_num_1 = np.array(resource_num_1)

    http1_num_1, http2_num_1, http3_num_1 = process_resource_num(resource_num_1, resource_httpv_1, L)

    http1_num_controls = np.zeros((len(resource_num_controls), L))
    http2_num_controls = np.zeros((len(resource_num_controls), L))
    http3_num_controls = np.zeros((len(resource_num_controls), L))

    for i in range(len(resource_num_controls)):
        http1_num_controls[i], http2_num_controls[i], http3_num_controls[i] = process_resource_num(
            np.array(resource_num_controls[i]), resource_httpv_controls[i], L)

    http_num_1 = np.sum(http1_num_1) + np.sum(http2_num_1) + np.sum(http3_num_1)
    if http_num_1 == 0:
        raise ValueError("Total HTTP count is zero.")

    w_h1 = np.sum(np.abs(http1_num_controls - http1_num_1), axis=1) / http_num_1
    w_h2 = np.sum(np.abs(http2_num_controls - http2_num_1), axis=1) / http_num_1
    w_h3 = np.sum(np.abs(http3_num_controls - http3_num_1), axis=1) / http_num_1

    return (w_h1 + w_h2 + w_h3) / 3




