import json
import random
import string
from collections import defaultdict
from pathlib import Path
import os
from urllib.parse import quote
from urllib.request import urlopen
from paddle_ocr import ocr
from src.manual import *
from src.common import *
from SPARQLWrapper import JSON, SPARQLWrapper
from numpy import log10


FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
output = os.path.join(ROOT, "output")


def generate_random_history(app_name):
    json_path = os.path.join(output, app_name + "_raw.json")
    print(json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        raw_words = data["words"]
    n = len(raw_words)
    x = random.randrange(0, n)
    return raw_words[x]


def generate_random():
    words = []
    with open("max.fuzzing.strings", "r", encoding='utf-8') as f:
        for line in f:
            word = line.strip()
            if len(word) > 0 and word[0] != '#' and word[0] != '<':
                words.append(word)
    n = len(words)
    x = random.randrange(0, n)
    return words[x]


def generate_word(image_path, target_location, json_path):
    with open(json_path, "r") as f:
        data = json.load(f)
        data_state = data["state"]
        data_all_words = data["all_words"]

    all_text_list, all_location_list = ocr(image_path)

    tip_word = get_tip_word(all_text_list, all_location_list, target_location)
    # tip_word = "places"

    # match_state = data_state[0]
    # flag = False
    hashtable = {}
    label_list = []
    for index, state in enumerate(data_state):
        print(state)
        label = state["label"].lower()
        hashtable[label] = index
        label_list.append(label)
    question = judge_question(label_list, tip_word=tip_word)
    word = GPT_3(question).split(':')[-1].replace(' ', '').lower()
    print(word)
    _id = hashtable[word]
    match_state = data_state[_id]
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
    # screen_shot()
    print(generate_random_history("metoffice"))
    # print(generate_random())
    # print(generate_word("", "", "E:\\PythonProject\\Datainput\\output\\metoffice.json"))
    # screen_shot("metoffice", "GPT-3")
