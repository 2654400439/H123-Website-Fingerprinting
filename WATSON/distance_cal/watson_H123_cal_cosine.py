import numpy as np


def cal_cosine_easy(resource_num_1, resource_num_controls_list, L):
    resource_num_1 = np.array(resource_num_1)
    predict_result = []

    for i in range(len(resource_num_controls_list)):
        resource_num_controls = np.array(resource_num_controls_list[i])

        resource_num_1 = np.concatenate((np.zeros(L - len(resource_num_1)), resource_num_1))
        resource_num_controls = np.concatenate((np.zeros(L - len(resource_num_controls)), resource_num_controls))

        dot_product_1 = np.dot(resource_num_1, resource_num_controls)
        similarity_1 = dot_product_1 / (np.linalg.norm(resource_num_1) * np.linalg.norm(resource_num_controls))

        predict_result.append(1 - similarity_1)

    return predict_result