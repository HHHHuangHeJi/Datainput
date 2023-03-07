import nltk
import uiautomator2 as u2


# 加载词汇模型
# print('Loading word2vec model, please waiting for a while....')
# # cn_model_file = 'model/news_12g_baidubaike_20g_novel_90g_embedding_64.bin'
# # cn_model = gensim.models.KeyedVectors.load_word2vec_format(cn_model_file, binary=True)
# global cn_model
# en_model_file = 'model/GoogleNews-vectors-negative300.bin'
# en_model = gensim.models.KeyedVectors.load_word2vec_format(en_model_file, binary=True)
from stanfordcorenlp import StanfordCoreNLP

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


def refine_cal_iou(location1, location2):
    x1, y1, w1, h1 = location1[0], location1[1], location1[2], location1[3]
    x2, y2, w2, h2 = location2[0], location2[1], location2[2], location2[3]
    # 计算两个矩形是否相交以及相交的比例
    if x1 <= x2 and x1 + w1 >= x2 + w2 and y1 <= y2 and y1 + h1 >= y2 + h2:
        return True
    if x2 <= x1 and x2 + w2 >= x1 + w1 and y2 <= y1 and y2 + h2 >= y1 + h1:
        return True

    col_int = min(x1 + w1, x2 + w2) - max(x1, x2)
    row_int = min(y1 + h1, y2 + h2) - max(y1, y2)
    intersection = col_int * row_int
    area1 = w1 * h1
    area2 = w2 * h2
    ratio = intersection / min(area1, area2)
    # print("Area1: {}, Area2: {}, Intersection: {}, Ratio: {}".format(area1, area2, intersection, ratio))
    if ratio >= 0.7:
        return True
    else:
        return False


def screen_shot(app, method):
    print('Connect to device...')
    # 连接设备
    d = u2.connect("127.0.0.1:5555")
    # d = u2.connect()
    print('Device connected.')
    screen_path = "E:\\PythonProject\\Datainput\\data\\{}\\{}_{}.jpg".format(app, app, method)
    d.screenshot(screen_path)


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

def sentence_tag(s):
    file_path = ""
    nlp = StanfordCoreNLP(file_path)
    print(nlp.pos_tag(s))

# def vector_similarity(str_first=None, str_second=None, language="EN"):
#     # 计算两个词语或句子的相似性，值域为-1到1
#     if language == "CN":
#         # 中文模型
#
#         def sentence_vector(s):
#             words = jieba.lcut(s)
#             v = np.zeros(64)
#             for word in words:
#                 try:
#                     c = cn_model[word]
#                 except KeyError:
#                     print("not in vocabulary")
#                     c = 0
#                 v += c
#             v /= len(words)
#             return v
#
#         v1, v2 = sentence_vector(str_first), sentence_vector(str_second)
#         return np.dot(v1, v2) / (norm(v1) * norm(v2))
#     else:
#         # 英文模型
#         print(str_first, end="---")
#         print(str_second)
#         return en_model.similarity(str_first, str_second)


if __name__ == "__main__":
    screen_shot("", "")

