from collections import defaultdict
import cv2
import numpy as np
from keybert import KeyBERT
import os
import time
import json
from paddle_ocr import ocr
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
output = os.path.join(ROOT, "output")


def complete_en(text):
    for item in text:
        if not item.isalpha():
            return False
    return True


def boolean_image_colorfulness(image_, threshold_):
    # 判断控件区域是否是图片
    # 这里之所以添加判断，是因为不添加这段过滤这边会出现错误
    if len(image_) <= 0 or len(image_[0]) == 0:
        return False
    # 将图片分为B,G,R三部分（注意，这里得到的R、G、B为向量而不是标量）
    (B, G, R) = cv2.split(image_.astype("float"))
    # rg = R - G
    rg = np.absolute(R - G)
    # yb = 0.5 * (R + G) - B
    yb = np.absolute(0.5 * (R + G) - B)
    # 计算rg和yb的平均值和标准差
    (rbMean, rbStd) = (np.mean(rg), np.std(rg))
    (ybMean, ybStd) = (np.mean(yb), np.std(yb))
    # 计算rgyb的标准差和平均值
    stdRoot = np.sqrt((rbStd ** 2) + (ybStd ** 2))
    meanRoot = np.sqrt((rbMean ** 2) + (ybMean ** 2))
    # 返回颜色丰富度C
    if stdRoot + (0.3 * meanRoot) > threshold_:
        return True
    else:
        return False


def not_contain_many_number(text):
    # 判断该文本是否包含数字，通过阈值进行控制量的程度
    digit_num = 0
    for every_str in text:
        if every_str.isdigit():
            digit_num += 1
    ratio = digit_num / len(text)

    if ratio <= 0.5:
        return True
    else:
        return False


def cal_iou(location1, location2):
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
    ratio = intersection / (area1 + area2 - intersection)
    if ratio >= 0.7:
        return True
    else:
        return False


def extract(image_path, app_name):
    st =time.time()
    image = cv2.imread(image_path)
    text_list, location_list = ocr(image_path)
    # 将未处理过的文本也存好
    json_file = os.path.join(output, app_name + "_raw.json")
    if not os.path.exists(json_file):
        open(json_file, "w", encoding="utf-8")
        raw_words = []
    else:
        with open(json_file, 'r', encoding="utf-8") as f:
            raw_data = json.load(f)
            raw_words = raw_data['words']

    for text in text_list:
        raw_words.append(text)
    raw_data = {"words": raw_words}
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(raw_data, f, indent=4, ensure_ascii=False)

    print("所有文本：", text_list)

    # 获取所有在同一列的文本 3个以上
    same_text_list = []
    same_location_list = []
    for text, location in zip(text_list, location_list):
        count = 1
        x, y, w, h = int(location[0]), int(location[1]), int(location[2]), int(location[3])
        temp_text_list = []
        temp_location_list = []
        temp_text_list.append(text)
        temp_location_list.append(location)
        if len(text) >= 2 and text not in same_text_list:
            for txt, loc in zip(text_list, location_list):
                tx = int(loc[0])
                if abs(x - tx) <= 5:
                    temp_text_list.append(txt)
                    temp_location_list.append(loc)
                    count += 1
        if count >= 3:
            for txt, loc in zip(temp_text_list, temp_location_list):
                if txt not in same_text_list:
                    same_text_list.append(txt)
                    same_location_list.append(loc)
    print("同一列文本：", same_text_list)

    # 获取标题类文本
    unit_area_list = []
    title_text_list = []
    title_location_list = []

    for text, location in zip(text_list, location_list):
        unit_area_list.append(location[2] * location[3] / len(text))

    if unit_area_list:
        avg = np.mean(unit_area_list)
        for index, item in enumerate(unit_area_list):
            if item >= avg:
                title_text_list.append(text_list[index])
                title_location_list.append(location_list[index])

    print("标题类文本：", title_text_list)

    # 预处理得到第一部分文本
    pre_text_list = []
    pre_location_list = []
    word_loc = {}
    for text1, loc1 in zip(same_text_list, same_location_list):
        if text1 not in word_loc:
            word_loc[text1] = loc1
    for text2, loc2 in zip(title_text_list, title_location_list):
        if text2 not in word_loc:
            word_loc[text2] = loc2
    word_loc = sorted(word_loc.items(), key=lambda x: x[1][1])

    for item in word_loc:
        pre_text_list.append(item[0])
        pre_location_list.append(item[1])

    print("预处理之后的文本:", pre_text_list)

    # 过滤数字占比大的文本 以及 一些固定不需要的文字
    no_num_text_list = []
    no_num_location_list = []
    for text, location in zip(pre_text_list, pre_location_list):
        if not_contain_many_number(text):
            no_num_location_list.append(location)
            no_num_text_list.append(text)

    print("过滤数字类之后：", no_num_text_list)

    # 过滤图片中的文本
    final_text_list = no_num_text_list
    final_location_list = no_num_location_list
    # for text, location in zip(no_num_text_list, no_num_location_list):
    #     x, y, w, h = int(location[0]), int(location[1]), int(location[2]), int(location[3])
    #     target_image = image[y: y + h, x: x + w]
    #     part_of_image = image[y:y + h, int(x + w * 0.8):x + w]
    #     if not boolean_image_colorfulness(target_image, 0.3) and not boolean_image_colorfulness(part_of_image, 0.3):
    #         final_location_list.append(location)
    #         final_text_list.append(text)

    print("所有文字为：", final_text_list)

    # 提取关键字
    if len(final_text_list) != 0:
        key_words = []
        k_model = KeyBERT()
        for text in final_text_list:
            words = [(text, 1)]
            if ' ' in text:
                words = k_model.extract_keywords(text)
            if len(words) != 0:
                key_words.append(words)

        # print("所得到的关键字为：", key_words)
        json_file = os.path.join(output, app_name + ".json")
        if not os.path.exists(json_file):
            open(json_file, "w", encoding="utf-8")
            data_state = []
            data_all_words = {}
        else:
            with open(json_file, 'r', encoding="utf-8") as f:
                data = json.load(f)
                data_state = data['state']
                data_all_words = data['all_words']

        picture_information = {"id": image_path.split('\\')[-1], "label": "None"}
        words = defaultdict(int)
        length = 0
        for item in key_words:
            for word in item:
                if not_contain_many_number(str(word[0])) and len(str(word[0])) > 3:
                    length += 1
                    words[word[0]] += 1
                    if words[word[0]] == 1:
                        if word[0] not in data_all_words:
                            data_all_words[word[0]] = 1
                        else:
                            data_all_words[word[0]] += 1
        picture_information["words"] = words
        for word in words:
            if complete_en(word):
                picture_information["label"] = word
                break
        data_state.append(picture_information)
        data_all_words = dict(sorted(data_all_words.items(), key=lambda x: x[1], reverse=True))
        print(picture_information)
        data = {"state": data_state, "all_words": data_all_words}
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("Time: ", end=" ")
        print(time.time() - st)


if __name__ == '__main__':
    path_of_dir = \
        'E:\\PythonProject\\Datainput\\data\\metoffice'
    image_list = [os.path.join(path_of_dir, name) for name in os.listdir(path_of_dir)]
    # image_list = ["E:\\PythonProject\\Datainput\\data\\screen_2022-08-12_001714.png"]
    app_name = "metoffice"
    for image in image_list:
        extract(image, app_name)

