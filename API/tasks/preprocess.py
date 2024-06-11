import os
import re
import string

import pandas as pd
from database.mysql_connector import update_preprocess_tasks
from underthesea import word_tokenize

TOKENIZE_RECORD_COUNT = 0
LOWERCASE_RECORD_COUNT = 0
STOPWORD_RECORD_COUNT = 0
PUNCTUATION_RECORD_COUNT = 0


def tokenize(text):
    return word_tokenize(text, format="text")


# Lowercase
def lowercase(text):
    return text.lower()


def remove_punctuation(text):
    regex = r"(?<!\d)[.,;:](?!\d)"
    # initializing punctuations string
    punc = """!"#$%&'()*+-/:;<=>?@[\]^_`{|}~"""
    # Removing punctuations in string
    # Using loop + punctuation string
    for ele in text:
        if ele in punc:
            text = text.replace(ele, " ")
    text = text.replace(". ", " ").replace(", ", " ")
    last_char = text[-1]
    if last_char in string.punctuation:
        text = text[:-1]
    return re.sub(regex, " ", text, 0)


def remove_stopwords(text):
    stops = open("./vietnamese-stopwords-dash.txt", "r", encoding="utf8").read()
    stopwords = [x for x in stops.splitlines()]
    return " ".join([word for word in text.split() if word not in stopwords])


def preprocess_text(text):
    global TOKENIZE_RECORD_COUNT
    global LOWERCASE_RECORD_COUNT
    global STOPWORD_RECORD_COUNT
    global PUNCTUATION_RECORD_COUNT
    text = text.replace("\xa0", " ")
    text = tokenize(text)
    print(text)
    TOKENIZE_RECORD_COUNT += 1
    update_preprocess_tasks("tokenize", TOKENIZE_RECORD_COUNT)
    text = lowercase(text)
    LOWERCASE_RECORD_COUNT += 1
    update_preprocess_tasks("lowercase", LOWERCASE_RECORD_COUNT)
    text = remove_stopwords(text)
    STOPWORD_RECORD_COUNT += 1
    update_preprocess_tasks("remove_stopwords", STOPWORD_RECORD_COUNT)
    text = remove_punctuation(text)
    PUNCTUATION_RECORD_COUNT += 1
    update_preprocess_tasks("remove_punctuation", PUNCTUATION_RECORD_COUNT)

    return text


def preprocess_data(data_path, preprocess_path):
    reset_all_record_count()
    # if file exists then read file
    if os.path.exists(data_path):
        # Read file csv
        df = pd.read_csv(data_path, encoding="utf-8-sig")
        # Apply preprocess
        print(f"preprocess_data: {len(df)}")
        df["description"] = df["description"].apply(preprocess_text)
        # print(df.head(5))

        # if preprocess file not exists then create new file
        if not os.path.exists(preprocess_path):
            # Output preprocessed
            df.to_csv(preprocess_path, index=False, encoding="utf-8-sig")
            return "Data is preprocessed and has written to csv file"
        else:
            os.remove(preprocess_path)
            print("Found a csv file, deleting it...")
            df.to_csv(preprocess_path, index=False, encoding="utf-8-sig")
            return "Data is preprocessed and has written to csv file"


def reset_all_record_count():
    global TOKENIZE_RECORD_COUNT
    global LOWERCASE_RECORD_COUNT
    global STOPWORD_RECORD_COUNT
    global PUNCTUATION_RECORD_COUNT

    TOKENIZE_RECORD_COUNT = 0
    LOWERCASE_RECORD_COUNT = 0
    STOPWORD_RECORD_COUNT = 0
    PUNCTUATION_RECORD_COUNT = 0
