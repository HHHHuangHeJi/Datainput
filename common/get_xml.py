import uiautomator2 as u2
from datetime import datetime


if __name__ == "__main__":
    print('Connect to device...')
    # 连接设备
    d = u2.connect("127.0.0.1:5555")
    # d = u2.connect()
    print('Device connected.')
    # d.screenshot("F:\\InputAnalysis\\contact2.jpg")
    print(d.info)
    package_name = d.info["currentPackageName"]
    print(package_name)
    activity_name = d.app_current()["activity"]
    print(activity_name.split(".")[-1])
    app_name = d.app_info(package_name=package_name)["label"]
    print(app_name)
    # # 获取当前页面的层次结构
    # page_source = d.dump_hierarchy(compressed=True, pretty=True)
    # tag = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    # screenshot_name = "screen_%s.xml" % tag
    # save_path = r"C:/Users/Administrator/QTypist/ui-tree/"
    # xml_file = open(save_path + screenshot_name, 'w', encoding='utf-8')
    # xml_file.write(page_source)
    # xml_file.close()