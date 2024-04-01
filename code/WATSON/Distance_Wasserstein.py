import numpy as np


def cal_sorted_wasserstein(resource_num_1, resource_num_2, resource_httpv_1, resource_httpv_2):
    resource_num_1 = np.array(resource_num_1)
    resource_num_2 = np.array(resource_num_2)

    http1_mask_1 = np.array([1 if item == 'http/1.1' else 0 for item in resource_httpv_1])
    http2_mask_1 = np.array([1 if item == 'h2' else 0 for item in resource_httpv_1])
    http3_mask_1 = np.array([1 if item == 'h3' else 0 for item in resource_httpv_1])

    http1_num_1 = np.sort(resource_num_1[http1_mask_1 == 1] if np.sum(http1_mask_1) != 0 else np.array([0]))
    http2_num_1 = np.sort(resource_num_1[http2_mask_1 == 1] if np.sum(http2_mask_1) != 0 else np.array([0]))
    http3_num_1 = np.sort(resource_num_1[http3_mask_1 == 1] if np.sum(http3_mask_1) != 0 else np.array([0]))

    http1_mask_2 = np.array([1 if item == 'http/1.1' else 0 for item in resource_httpv_2])
    http2_mask_2 = np.array([1 if item == 'h2' else 0 for item in resource_httpv_2])
    http3_mask_2 = np.array([1 if item == 'h3' else 0 for item in resource_httpv_2])

    http1_num_2 = np.sort(resource_num_2[http1_mask_2 == 1] if np.sum(http1_mask_2) != 0 else np.array([0]))
    http2_num_2 = np.sort(resource_num_2[http2_mask_2 == 1] if np.sum(http2_mask_2) != 0 else np.array([0]))
    http3_num_2 = np.sort(resource_num_2[http3_mask_2 == 1] if np.sum(http3_mask_2) != 0 else np.array([0]))

    http1_num_1 = np.concatenate((np.zeros(len(http1_num_2)-len(http1_num_1)), http1_num_1)) if len(
        http1_num_1) < len(http1_num_2) else http1_num_1
    http1_num_2 = np.concatenate((np.zeros(len(http1_num_1) - len(http1_num_2)), http1_num_2)) if len(
        http1_num_1) > len(http1_num_2) else http1_num_2

    http2_num_1 = np.concatenate((np.zeros(len(http2_num_2) - len(http2_num_1)), http2_num_1)) if len(
        http2_num_1) < len(http2_num_2) else http2_num_1
    http2_num_2 = np.concatenate((np.zeros(len(http2_num_1) - len(http2_num_2)), http2_num_2)) if len(
        http2_num_1) > len(http2_num_2) else http2_num_2

    http3_num_1 = np.concatenate((np.zeros(len(http3_num_2) - len(http3_num_1)), http3_num_1)) if len(
        http3_num_1) < len(http3_num_2) else http3_num_1
    http3_num_2 = np.concatenate((np.zeros(len(http3_num_1) - len(http3_num_2)), http3_num_2)) if len(
        http3_num_1) > len(http3_num_2) else http3_num_2

    http_num_1 = np.sum(http1_num_1) + np.sum(http2_num_1) + np.sum(http3_num_1)
    w_h1 = np.sum(np.abs(http1_num_1 - http1_num_2)) / http_num_1
    w_h2 = np.sum(np.abs(http2_num_1 - http2_num_2)) / http_num_1
    w_h3 = np.sum(np.abs(http3_num_1 - http3_num_2)) / http_num_1

    return (w_h1 + w_h2 + w_h3) / 3