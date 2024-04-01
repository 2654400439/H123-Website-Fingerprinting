import H123_fingerprint_construction

from tqdm import trange


def main():
    with open('./url_list_top300_h3.txt', 'r') as f:
        data = f.readlines()
    url_list = data[0].split('\t')

    for i in trange(len(url_list)):
        with open('../../result/dataset_tmp/dataset.txt', 'a') as f:
            url = 'http://' + url_list[i]
            try:
                r_num, r_version = H123_fingerprint_construction.fingerprint_extract(url)
                f.write(url_list[i] + '\t' + str(r_num) + '\t' + str(r_version) + '\n')
            except Exception:
                f.write(url_list[i] + '\t' + 'error' + '\n')


if __name__ == '__main__':
    main()
