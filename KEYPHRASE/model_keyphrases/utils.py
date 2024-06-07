import os

import joblib
import numpy as np
import torch
from model_keyphrases.dataset import EntityDataset
from model_keyphrases.global_var import TOKENIZER
from model_keyphrases.model import EntityModel

global device
device = torch.device("cpu")


def predict_sentence(model, sentence, enc_tag):
    sentence = sentence.split()
    test_dataset = EntityDataset(
        texts=[sentence],
        # pos=[[0] * len(sentence)],
        tags=[[0] * len(sentence)],
        enc_tag=enc_tag,
    )

    with torch.no_grad():
        data = test_dataset[0]
        for k, v in data.items():
            data[k] = v.to(device).unsqueeze(0)

        tag = model.encode(**data)
        tag = enc_tag.inverse_transform(tag[0])
        # pos = enc_pos.inverse_transform(pos[0])

    return tag


def reverse_tokenize(ids, tags):
    tokens = []
    tags_list = []
    for token_id, tag in zip(ids, tags):
        token = TOKENIZER.decode(token_id)
        token = token.replace(" ", "")
        token_array = np.array(list(token))
        token_string = "".join(token_array)
        if token_string.startswith("##"):
            token_string = token_string.replace("##", "")
            if tokens:
                tokens[-1] += token_string
                # Nếu từ bắt đầu bằng '##', ta vẫn giữ nguyên tag của từ trước đó
                tags_list[-1] = tag
        else:
            tokens.append(token_string)
            tags_list.append(tag)
    return list(zip(tokens, tags_list))


# meta_data: enc_pos/enc_tag - POS/TAG label encoder
global meta_data
meta_data = joblib.load("model_keyphrases/meta.bin")
# enc_pos = meta_data["enc_pos"]
global enc_tag
enc_tag = meta_data["enc_tag"]

# num_pos = len(list(enc_pos.classes_))
global num_tag
num_tag = len(list(enc_tag.classes_))

# Define the local path and the Hugging Face model identifier
local_model_path = "./model_keyphrases/pretrained_model/bert-bilstm-crf-mobile-phone"
huggingface_model_identifier = "Soraki5th/bert-bilstm-crf-mobile-phone"


def _load_model(verbose=False):
    # model = EntityModel(num_tag=num_tag)
    # model.load_state_dict(torch.load(MODEL_PATH+f"_{9}.bin", map_location=device))
    # model = EntityModel.from_pretrained("Soraki5th/bert-bilstm-crf-mobile-phone")
    print("Loading model...")

    # Check if the model is saved locally
    if os.path.exists(local_model_path):
        # Load the model from the local path
        if verbose:
            print("Loading model from local path...")
        model = EntityModel.from_pretrained(local_model_path)
    else:
        if verbose:
            print("Loading model from hugging face...")
        # Load the model from the Hugging Face Hub
        model = EntityModel.from_pretrained(huggingface_model_identifier)
        if verbose:
            print("Saving model...")
        # Save the model locally
        model.save_pretrained(local_model_path)
    # Move the model to the specified device
    model.to(device)
    print("model loaded successfully!")
    return model


def _save_model(verbose=False):
    if verbose:
        print("Loading model from hugging face...")
    # Load the model from the Hugging Face Hub
    model = EntityModel.from_pretrained(huggingface_model_identifier)
    if verbose:
        print("Saving model...")
    # Save the model locally
    model.save_pretrained(local_model_path)
    # Move the model to the specified device
    model.to(device)

    return model


def _predict(model, sentence):
    # join the arr -> string sentence (nargs='+', dont have to use "" when enter the string)
    tokenized_sentence = TOKENIZER.encode(sentence)

    tags = predict_sentence(model, sentence, enc_tag)

    print(sentence)
    print("Word\t\tLabel")
    # Sử dụng reverse_tokenize để lấy reversed_tokens
    reversed_tokens = reverse_tokenize(tokenized_sentence, tags)

    tokens = []
    tags = []
    # Lặp qua reversed_tokens và hiển thị các token và tag thỏa điều kiện
    for token, tag in reversed_tokens:
        if tag in [
            "S",
            "B-P",
            "I-P",
        ]:  # Lọc để chỉ hiển thị các nhãn 'S', 'B-P', và 'I-P'
            print(f"{token}\t\t{tag}")
            tokens.append(token)
            tags.append(tag)

    return " ".join(tokens), " ".join(tags)
