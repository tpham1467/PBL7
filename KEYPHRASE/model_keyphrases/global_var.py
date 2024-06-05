import os
import transformers

global MAX_LEN 
MAX_LEN = 256

global EMBEDDING_MODEL_NAME
EMBEDDING_MODEL_NAME="bert-base-multilingual-cased"

# Define the local path for saving the tokenizer
local_tokenizer_path = "./model_keyphrases/pretrained_model/" + EMBEDDING_MODEL_NAME + "-tokenizer"

def load_tokenizer():
    # Check if the tokenizer is saved locally
    if os.path.exists(local_tokenizer_path):
        # Load the tokenizer from the local path
        TOKENIZER = transformers.BertTokenizer.from_pretrained(local_tokenizer_path)
    else:
        # Load the tokenizer from the Hugging Face Hub
        TOKENIZER = transformers.BertTokenizer.from_pretrained(EMBEDDING_MODEL_NAME)
        # Save the tokenizer locally
        TOKENIZER.save_pretrained(local_tokenizer_path)
    return TOKENIZER

global TOKENIZER
TOKENIZER = load_tokenizer()