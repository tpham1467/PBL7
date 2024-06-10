from flask import Flask, request, jsonify
import requests
import sys
import pandas as pd
sys.path.insert(1, '/content/model')
sys.path.insert(2, '/content/sentence-transformers')
from model import predict as model_predict
import json
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415

    data = request.get_json()

    if 'text' not in data:
        return jsonify({"error": "Missing 'text' in request data"}), 400

    text = str(data['text'])

    print(text)

    url = 'http://key_phrase:8002/keyphrases/predict'
    
    incorrect_payload = {
    'text': text
    }
    
    response = requests.post(url, json=incorrect_payload)
    
    data1 = response.json()

    text = str(data1['tokens'])
    if text == '':
        text = str(data['text'])
    
    predict = model_predict([text])
    predicts = []
    scores = []
    for x in predict:
        predicts.append(x)
        scores.append(predict[x][0][0])

    return jsonify({
                    "keywords": str(data1['tokens']).replace(' ', ','),
                    "products": {
                        "top1": "https://www.thegioididong.com" + predicts[0],
                        "top1_score": str(scores[0]),
                        "top2": "https://www.thegioididong.com" + predicts[1],
                        "top2_score": str(scores[1]),
                         "top3": "https://www.thegioididong.com" + predicts[2],
                         "top3_score": str(scores[2])
                        }
                    }, 200)

@app.route('/', methods=['GET'])
def predict1():
    return jsonify("djjd", 200)

