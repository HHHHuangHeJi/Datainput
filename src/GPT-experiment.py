import openai
import uiautomator2 as u2

text_header = "Question: "


def generate_question(app, activity, widgetv_n, widget_n, local):
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
    IWPtn_2 = IWPtn_2.replace("<widget[v + n]>", widgetv_n)
    # print(IWPtn_1)
    question = text_header + GCPtn + LCPtn_1 + IWPtn_1
    # question = text_header + GCPtn + LCPtn_1 + IWPtn_2
    print(question)
    return question


def judge_question(word_list, tip_word):
    question = "Question: Given words: "
    for word in word_list:
        question += word
        question += ","
    question += \
        "which one is the most relative to {}. Please answer the question from the given words.".format(tip_word)
    print(question)
    return question


def GPT_3(question):
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
    word = response["choices"][0]["text"]
    print(word)
    return word




if __name__ == "__main__":
    # # sentence_tag("search for sources, topics, people...")
    # print('Connect to device...')
    # # 连接设备
    # d = u2.connect("127.0.0.1:5555")
    # # d = u2.connect()
    # print('Device connected.')
    # # d.screenshot("F:\\InputAnalysis\\contact2.jpg")
    # print(d.info)
    # package_name = d.info["currentPackageName"]
    # # print(package_name)
    # activity_name = d.app_current()["activity"].split(".")[-1]
    # # activity_name = "contact"
    # print(activity_name)
    # app_name = d.app_info(package_name=package_name)["label"]
    # # app_name = "contact"
    # print(app_name)
    # widgetv_n = "Search places"
    # widget_n = "places"
    # local = "weather"
    # question1 = generate_question(app_name, activity_name, widgetv_n, widget_n, local)
    words = ["maps", "weather", "folder"]
    tip_word = "places"
    question2 = judge_question(word_list=words, tip_word=tip_word)
    print(GPT_3(question2).split(':')[-1].replace(' ', '').lower())

