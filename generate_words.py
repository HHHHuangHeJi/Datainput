import json
import math
from urllib.parse import quote
from urllib.request import urlopen
import gensim
import jieba
from SPARQLWrapper import SPARQLWrapper, JSON
from numpy.linalg import norm
from word_extract import *
import nltk
import random
import string

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

print('Loading word2vec model, please waiting for a while....')
# cn_model_file = 'model/news_12g_baidubaike_20g_novel_90g_embedding_64.bin'
# cn_model = gensim.models.KeyedVectors.load_word2vec_format(cn_model_file, binary=True)
global cn_model
en_model_file = 'model/GoogleNews-vectors-negative300.bin'
en_model = gensim.models.KeyedVectors.load_word2vec_format(en_model_file, binary=True)


def get_tip_word(text_list, location_list, target):
    x, y, w, h = int(target[0]), int(target[1]), int(target[2]), int(target[3])
    top_left = (max(x - w, 0), max(y - h, 0))
    right_bottom = (min(1080, x + w), min(1920, y + h))
    refine_text = []
    refine_location = []
    for text, location in zip(text_list, location_list):
        x1, y1, x2, y2 = int(location[0]), int(location[1]), int(location[0]) + int(location[2]), int(location[1]) + int(location[3])
        if x1 < top_left[0] or x2 > right_bottom[0] or y1 < top_left[1] or y2 > right_bottom[1]:
            continue
        refine_text.append(text)
        refine_location.append(location)
    inner = (x, y, w, h)
    upper = (x, max(0, y - h), w, h)
    left = (max(0, x - w), y, w, h)
    lower = (x, min(y + h, 1920), w, h)
    tip_location = [inner, upper, left, lower]
    print(tip_location)
    for tip in tip_location:
        for text, location in zip(refine_text, refine_location):
            if refine_cal_iou(tip, location):
                return text

    return "None"


def get_search_word(text_):
    # 获取“搜索提示关键字”
    result = "None"

    # 调用词法分析
    words = nltk.tokenize.word_tokenize(text_)
    pos_tag = nltk.tag.pos_tag(words)

    # "NN" 名词
    for pos in pos_tag:
        if pos[1] == "NN":
            result = pos[0]

    return result


def vector_similarity(str_first=None, str_second=None, language="EN"):
    # 计算两个词语或句子的相似性，值域为-1到1
    if language == "CN":
        # 中文模型

        def sentence_vector(s):
            words = jieba.lcut(s)
            v = np.zeros(64)
            for word in words:
                try:
                    c = cn_model[word]
                except KeyError:
                    print("not in vocabulary")
                    c = 0
                v += c
            v /= len(words)
            return v

        v1, v2 = sentence_vector(str_first), sentence_vector(str_second)
        return np.dot(v1, v2) / (norm(v1) * norm(v2))
    else:
        # 英文模型
        return en_model.similarity(str_first, str_second)


def generate_word(image_path, target_location, json_path):
    with open(json_path, "r") as f:
        data = json.load(f)
        data_state = data["state"]
        data_all_words = data["all_words"]

    all_text_list, all_location_list = ocr(image_path)

    tip_word = get_tip_word(all_text_list, all_location_list, target_location)

    match_state = None
    flag = False
    if tip_word != "None":  # 如果存在提示文字
        max_similarity = 0
        for state in data_state:
            # 遍历每个词汇与提示文字的相似度
            label = state["label"]
            if label != "None":
                flag = True
                p = vector_similarity(tip_word, label)
                if p > max_similarity:
                    match_state = state
                    max_similarity = p

    if tip_word == "None" or not flag:  # 如果不存在提示文字 或者 每个状态的标签都为None
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


def generate_random_text():
    n = random.randint(2, 4)
    input_str = ""
    while n:
        s = random.choice(string.ascii_lowercase)
        input_str += s
        n -= 1
    return input_str


def generate_random_history(app_name):
    json_path = os.path.join(output, app_name + "_raw.json")
    with open(json_path, "r") as f:
        data = json.load(f)
        raw_words = data["words"]
    n = len(raw_words)
    x = random.randrange(0, n)
    return raw_words[x]


def generate_db(method, query):
    if method == 1:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        # query = "Country"
        sparql.setQuery("""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT *
            WHERE { <http://dbpedia.org/resource/%s> dbo:wikiPageWikiLink ?label}
        """ % (query))
        print('\
        \
        *** JSON Example')
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        # print(results)
        # for result in results["results"]["bindings"]:
        #     print(result["label"]["value"].split('/')[-1])
        return results["results"]["bindings"][2]["label"]["value"].split('/')[-1]
    elif method == 2:
        query = ""
        input_entity = quote(query)
        api_key = "&apikey=55ac303c95dff5652de92e996d1997b9"
        input_url = 'http://shuyantech.com/api/cnprobase/entity?q='
        url = input_url + input_entity + api_key
        response = urlopen(url)
        result = eval(response.read().decode('utf-8'))
        assert result["status"] == "ok", "中文数据库内获取数据失败......"
        return result["ret"][2][0]


if __name__ == "__main__":
    word = generate_db(2, "植物")
    print(word)
