import json
import time
import xml.etree.ElementTree as ET
import os.path
import cv2


def dfs(tree_root, _box):
    queue = [tree_root]
    hash_map = {}
    # "FrameLayout": 1,
    clickable_ui = {"DrawerLayout": 1, "SlidingMenu": 1,  "ListView": 1, "LinearLayout": 1, "FrameLayout": 1,
                    "ViewGroup": 1, "RecyclerView": 1}
    framework_ui = \
        {"DrawerLayout": 1, "SlidingMenu": 1, "ListView": 1, "ViewGroup": 1, "ScrollView": 1, "FrameLayout": 1,
         "LinearLayout": 1, "RecyclerView": 1}
    while len(queue) > 0:
        cur = queue.pop()
        if "class" in cur.attrib:
            father = cur.attrib['class'].split('.')[-1]
        else:
            father = "root"
        for leaf in cur.findall('node'):
            bound = leaf.attrib['bounds']
            bound = bound.replace('[', '').replace(']', ' ').replace(',', ' ')
            name = leaf.attrib['class'].split('.')[-1]
            num_sum = 0
            region = []
            index = 0
            while index < len(bound):
                if bound[index].isdigit():
                    while bound[index].isdigit():
                        num_sum = num_sum * 10 + int(bound[index])
                        index += 1
                    region.append(num_sum)
                    num_sum = 0
                else:
                    index += 1
            if leaf.find('node') is not None:
                queue.append(leaf)
            if name in framework_ui.keys() or leaf.attrib["enabled"] == "false":
                continue
            clickable = False
            if father in clickable_ui.keys():
                clickable = True
            if name == "TextView" and leaf.attrib["clickable"] != "true":
                continue
            if leaf.attrib["clickable"] == "true" or clickable:
            # print(name, end='#')
            # print(hash_map[name], end="# ")
            # print(bound)
                _box.append(region)


if __name__ == '__main__':
    xmls_file = "E:\\PythonProject\\evalute\\test_xml"
    pictures_file = "E:\\PythonProject\\evalute\\test_screen"
    write_file = "E:\\PythonProject\\evalute\\output_8"
    if not os.path.exists(write_file):
        os.mkdir(write_file)
    for file in os.listdir(xmls_file):
        _id = file.split('.')[0]
        xml_file = os.path.join(xmls_file, file)
        img_path = pictures_file + os.sep + _id + ".png"
        result_path = write_file + os.sep + _id + ".png"
        tree = ET.parse(xml_file)
        root = tree.getroot()
        box = []
        dfs(root, box)
        img = cv2.imread(img_path)
        for item in box:
            x1 = item[0]
            y1 = item[1]
            x2 = item[2]
            y2 = item[3]
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        cv2.imwrite(result_path, img)

    # file = r"E:\PythonProject\evalute\test_xml\screen_2022-08-03_141739.xml"
    #
    # tree = ET.parse(file)
    #
    # root = tree.getroot()
    #
    # box = []
    # dfs(root, box)
    # img = cv2.imread("E:\PythonProject\evalute\\test_screen\screen_2022-08-03_141629.png")
    # img = cv2.imread("E:\PythonProject\evalute\\test_screen\screen_2022-08-03_141629.png"
    # img = cv2.imread("E:\PythonProject\evalute\\test_screen\screen_2022-08-03_141739.png")
    # img = cv2.imread("E:\PythonProject\evalute\\test_screen\screen_2022-08-05_055333.png")
    # for item in box:
    #     x1 = item[0]
    #     y1 = item[1]
    #     x2 = item[2]
    #     y2 = item[3]
    #     cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
    #
    # temp = str(time.time())
    # p = "E:\PythonProject\evalute\\" + temp + ".png"
    # cv2.imwrite(p, img)

