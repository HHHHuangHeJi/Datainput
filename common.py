import nltk

# nltk.download()


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

