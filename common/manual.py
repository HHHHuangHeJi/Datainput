import nltk
import openai
from nltk import RegexpTokenizer
from stanfordcorenlp import StanfordCoreNLP
import uiautomator2 as u2

text_header = "Question: "


def GPT_3(app, activity, widgetv_n, widget_n, local):
    GCPtn = "This is a <app name> app, in its <activity name> page, the input category is <input category>."
    LCPtn_1 = "This input is about <local[n]>."
    LCPtn_2 = "This input is about <local[n]> ,we need <local[v+n]>"
    IWPtn_1 = "Please input a <widget[n]>, the <widget[n]> is"
    IWPtn_2 = "Please <widget[v + n]>"
    IWPtn_3 = "<widget[n] + [MASK] + <widget[n]>"
    IWPtn_4 = "<widget[prep] +[MASK]>"

    GCPtn = GCPtn.replace("<app name>", app).replace("<activity name>", activity).replace("<input category>", "query")
    # print(GCPtn)
    LCPtn_1 = LCPtn_1.replace("<local[n]>", local)
    # print(LCPtn_1)
    IWPtn_1 = IWPtn_1.replace("<widget[n]>", widget_n)
    # IWPtn_2 = IWPtn_2.replace("<widget[v + n]>", widgetv_n)
    # print(IWPtn_1)
    question = text_header + GCPtn + LCPtn_1 + IWPtn_1
    # question = text_header + GCPtn + LCPtn_1 + IWPtn_2
    print(question)

    openai.api_key = "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"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=question,
        temperature=0,
        max_tokens=20,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["->"]
    )

    for texts in response["choices"]:
        print(texts["text"])


def sentence_tag(s):
    file_path = ""
    nlp = StanfordCoreNLP(file_path)
    print(nlp.pos_tag(s))


if __name__ == "__main__":
    # sentence_tag("search for sources, topics, people...")
    print('Connect to device...')
    # 连接设备
    d = u2.connect("127.0.0.1:5555")
    # d = u2.connect()
    print('Device connected.')
    # d.screenshot("F:\\InputAnalysis\\contact2.jpg")
    print(d.info)
    package_name = d.info["currentPackageName"]
    # print(package_name)
    activity_name = d.app_current()["activity"].split(".")[-1]
    # print(activity_name)
    app_name = d.app_info(package_name=package_name)["label"]
    # print(app_name)
    widgetv_n = "Search for sources"
    widget_n = "place"
    local = "weather"
    GPT_3(app_name, activity_name, widgetv_n, widget_n, local)