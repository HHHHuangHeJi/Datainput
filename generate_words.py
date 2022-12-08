import json
import math
from collections import defaultdict
from math import log10, sqrt
from common import get_search_word
import gensim
import jieba
import numpy as np
from numpy.linalg import norm
from paddle_ocr import ocr
from word_extract import cal_iou

profile = {
    "name": "Huangheji",
    "sex": "Male",
    "age": 21,
    "address": "江苏省南京市江宁区将军大道29号",
    "email": "156266850@qq.com",
    "zip code": "211100",
    "password": "huang200096",
    "phone": "13607989331"
}


# CH
def vector_similarity(str_first=None, str_second=None):
    # 计算两个词语或句子的相似性，值域为-1到1
    model_label = True
    global model
    if model_label:
        # 给个标记，使得模型只加载一次，防止重复加载
        print('Loading word2vec model, please waiting for a while....')
        model_file = 'model/news_12g_baidubaike_20g_novel_90g_embedding_64.bin'
        # model_file = 'model/GoogleNews-vectors-negative300.bin'
        model = gensim.models.KeyedVectors.load_word2vec_format(model_file, binary=True)
        model_label = False

    def sentence_vector(s):
        words = jieba.lcut(s)
        v = np.zeros(64)
        for word in words:
            try:
                c = model[word]
            except KeyError:
                print("not in vocabulary")
                c = 0
            v += c
        v /= len(words)
        return v

    v1, v2 = sentence_vector(str_first), sentence_vector(str_second)
    return np.dot(v1, v2) / (norm(v1) * norm(v2))


# EN
def en_similarity(str_first=None, str_second=None):
    # 计算两个词语或句子的相似性，值域为-1到1
    model_label = True
    global model
    if model_label:
        # 给个标记，使得模型只加载一次，防止重复加载
        print('Loading word2vec model, please waiting for a while....')
        model_file = 'model/GoogleNews-vectors-negative300.bin'
        # model_file = 'model/GoogleNews-vectors-negative300.bin'
        model = gensim.models.KeyedVectors.load_word2vec_format(model_file, binary=True)
        model_label = False

    return model.similarity(str_first, str_second)


def cal_distance(p1, p2):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def generate_word(image_path, target_location, json_path):
    with open(json_path, "r") as f:
        data = json.load(f)
        data_state = data["state"]
        data_all_words = data["all_words"]

    all_text_list, all_location_list = ocr(image_path)
    centre = {}
    target_centre_point = [target_location[0] + target_location[2] / 2, target_location[1] + target_location[3] / 2]
    for text, location in zip(all_text_list, all_location_list):
        x, y, w, h = location[0], location[1], location[2], location[3]
        centre_point = [x + w / 2, y + h / 2]
        centre[text] = cal_distance(centre_point, target_centre_point)
    centre = sorted(centre.items(), key=lambda x: x[1])

    tip_word = "None"
    for text, location in zip(all_text_list, all_location_list):
        # 找到输入框内的提示文字
        # TODO 加入文字融合 将周围的文字加入 不仅仅是输入框内的提示文字
        if cal_iou(location, target_location):
            tip_word = get_search_word(text)
            break

    match_state = None
    flag = False
    if tip_word is not "None":  # 如果存在提示文字
        max_similarity = 0
        for state in data_state:
            # 遍历每个词汇与提示文字的相似度
            label = state["label"]
            if label != "None":
                flag = True
                p = en_similarity(tip_word, label)
                if p > max_similarity:
                    match_state = state
                    max_similarity = p

    if tip_word is "None" or not flag:  # 如果不存在提示文字 或者 每个状态的标签都为None
        state_list = data_state[::-1]
        for state in state_list:
            words = state["words"]
            if len(words) != 0:
                match_state = state
                break

    tfidf = defaultdict(float)
    words = match_state["words"]
    length = len(words)
    cnt = len(data_state)
    for key in words:
        # 根据TD-IDF计算文本权重
        tf = words[key] / length
        idf = log10(cnt / (data_all_words[key]) + 1)
        tfidf[key] = tf * idf
    tfidf = sorted(tfidf.items(), key=lambda x: x[1], reverse=True)

    return tfidf[0][0]
