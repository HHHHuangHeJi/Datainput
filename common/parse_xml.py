# This Script is to get the edit-text control in the GUI with xml
import json
import time
import xml.etree.ElementTree as ET
import os.path
import string
import cv2

# xml_file = "E:\\PythonProject\\evaluate\\test_xml"
xml_file = "E:\PythonProject\evaluate\\test_xml"


def to_int(s):
    temp = ""
    bound = []
    for index, t in enumerate(s):
        if t == ' ':
            bound.append(eval(temp))
            temp = ""
        else:
            temp += t
    if temp != "":
        bound.append(eval(temp))
    return bound


def dfs(root, app_name):
    queue = [root]
    while len(queue) > 0:
        cur = queue.pop()
        cur_node = cur.attrib
        if "class" in cur.attrib:
            cur_bound = to_int(cur_node['bounds'].replace('[', '').replace(']', ' ').replace(',', ' '))
            cur_class = cur_node['class'].split('.')[-1].lower()
            if "edittext" in cur_class or "hint-text" in cur_class or "autocompletetextview" in cur_class:
                print("Class:", end=" ")
                print(cur_class)
                # break
        if "resource-id" in cur.attrib:
            cur_bound = to_int(cur_node['bounds'].replace('[', '').replace(']', ' ').replace(',', ' '))
            cur_resource_id = cur_node['resource-id'].split('.')[-1].lower()
            if "edittext" in cur_resource_id or "hint-text" in cur_resource_id or "autocompletetextview" in cur_resource_id:
                print("Id:", end=" ")
                print(cur_resource_id)
                # break

        for leaf in cur.findall('node'):
            queue.append(leaf)


def parse_xml_file(xml_path):
    for file in os.listdir(xml_path):
        box = []
        cur_xml = os.path.join(xml_path, file)
        # print(cur_xml)
        tree = ET.parse(cur_xml)
        t_root = tree.getroot()
        dfs(t_root, cur_xml)


if __name__ == "__main__":
    parse_xml_file(xml_file)
    # to_int("10 20 30 40")


