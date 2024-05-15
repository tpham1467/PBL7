import pandas as pd
from underthesea import word_tokenize
import re
import string
import urllib

def tokenize(text):
    return word_tokenize(text, format="text")

#Lowercase
def lowercase(text):
    return text.lower()

def remove_punctuation(text):
    regex = r'(?<!\d)[.,;:](?!\d)'
    # initializing punctuations string
    punc = '''!"#$%&'()*+-/:;<=>?@[\]^_`{|}~'''
    # Removing punctuations in string
    # Using loop + punctuation string
    for ele in text:
        if ele in punc:
            text = text.replace(ele, " ")
    text = text.replace(". ", " ").replace(", "," ")
    last_char = text[-1]
    if last_char in string.punctuation:
      text = text[:-1]
    return re.sub(regex, " ", text, 0)

def remove_stopwords(text):
    stops = urllib.request.urlopen('https://raw.githubusercontent.com/stopwords/vietnamese-stopwords/master/vietnamese-stopwords-dash.txt').read()
    stopwords= [ x for x in stops.splitlines() ]
    return ' '.join([word for word in text.split() if word not in stopwords])

def preprocess_text(text):
    text.replace(u'\xa0', u' ')
    
    text = tokenize(text)
    text = lowercase(text)
    text = remove_stopwords(text)
    text = remove_punctuation(text)
    return text

# def preprocess_data (data_path):

    # Read file csv
    # data = pd.read_csv("tgdd_product_description_cleaned.csv")

    # Apply preprocess
    # data['description'] = data['description'].apply(preprocess_text)

    # Output preprocessed 
    # data.to_csv("tgdd_product_description_cleaned_preprocessed.csv", index=False, encoding="utf-8-sig")