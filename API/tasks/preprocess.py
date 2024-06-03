import pandas as pd
# from underthesea import word_tokenize

import re
import string
import os

def tokenize(text):
    # return word_tokenize(text, format="text")
    return ""

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
    stops = open("./vietnamese-stopwords-dash.txt", "r", encoding="utf8").read()
    stopwords= [ x for x in stops.splitlines() ]
    return ' '.join([word for word in text.split() if word not in stopwords])

def preprocess_text(text):
    text = text.replace(u'\xa0', u' ')
    
    text = tokenize(text)
    text = lowercase(text)
    text = remove_stopwords(text)
    text = remove_punctuation(text)
    print(text)
    return text

def preprocess_data (data_path, preprocess_path):
    #if file exists then read file
    if os.path.exists(data_path):
        # Read file csv
        df = pd.read_csv(data_path, encoding="utf-8-sig")
        # Apply preprocess
        df['description'] = df['description'].apply(preprocess_text)
        print(df.head(5))
        
        #if preprocess file not exists then create new file
        if not os.path.exists(preprocess_path):
            # Output preprocessed 
            df.to_csv(preprocess_path, index=False, encoding="utf-8-sig")
            return "Data is preprocessed and has written to csv file"
        else:
            os.remove(preprocess_path)
            print ("Found a csv file, deleting it...")
            df.to_csv(preprocess_path, index=False, encoding="utf-8-sig")
            return "Data is preprocessed and has written to csv file"
        