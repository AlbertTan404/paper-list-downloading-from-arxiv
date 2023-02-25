import arxiv
import urllib.request
import os
import re
from typing import Union, List
from tqdm import tqdm


def same_title(
        tar_name: str,
        res_name: str,
        threshold=0.9
):
    tar_tokens_set = set(tar_name.split(' '))
    res_tokens_set = set(res_name.split(' '))
    return len(tar_tokens_set.intersection(res_tokens_set)) * 2 / (
            len(tar_tokens_set) + len(res_tokens_set)) > threshold


def download_papers(
        paper_titles: Union[List[str], str],
        paper_save_dir: str
):
    if isinstance(paper_titles, str):
        with open(paper_titles, 'r') as f:
            paper_titles = f.readlines()

    if not os.path.exists(paper_save_dir):
        os.makedirs(paper_save_dir)

    paper_titles = [i.strip('\n') for i in paper_titles]

    print('searching papers...')
    searched_results = []
    for title in tqdm(paper_titles):
        try:
            searched_results.append([i for i in arxiv.Search(query=title, max_results=1).results()])
        except Exception:
            continue

    searched_title_link_map = dict()
    for res in searched_results:
        if len(res) > 0:
            searched_title_link_map.update({res[0].title: res[0].links[1].href})

    searched_titles = list(searched_title_link_map.keys())

    same_titles = []
    for tar in paper_titles:
        for res in searched_titles:
            if same_title(tar, res):
                same_titles.append(res)

    print(f'{len(same_titles)} similar papers found, start downloading...')

    for title in tqdm(same_titles):
        try:
            # file name mustn't include ':' or other special characters
            filtered_title = " ".join(re.findall(r'[\w\-]+', title))
            urllib.request.urlretrieve(searched_title_link_map[title], f'{paper_save_dir}/{filtered_title}.pdf')
        except:
            print(f'Warnning: failed to download {title}.pdf')


if __name__ == '__main__':
    download_papers('./paper_list.txt', './papers')
