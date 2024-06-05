import os
import transformers

global MAX_LEN 
MAX_LEN = 256
# global BASE_MODEL_PATH
# BASE_MODEL_PATH = "./model_keyphrases/pretrained_model/bert-base-uncased"
# global MODEL_PATH
# MODEL_PATH = "model_keyphrases/models/trained_model"

global EMBEDDING_MODEL_NAME
EMBEDDING_MODEL_NAME="bert-base-multilingual-cased"

# Define the local path for saving the tokenizer
local_tokenizer_path = "./model_keyphrases/pretrained_model/" + EMBEDDING_MODEL_NAME + "-tokenizer"

global TOKENIZER
# TOKENIZER = transformers.BertTokenizer.from_pretrained(
#     EMBEDDING_MODEL_NAME,
#     do_lower_case=True
# )

# Check if the tokenizer is saved locally
if os.path.exists(local_tokenizer_path):
    # Load the tokenizer from the local path
    TOKENIZER = transformers.BertTokenizer.from_pretrained(local_tokenizer_path)
else:
    # Load the tokenizer from the Hugging Face Hub
    TOKENIZER = transformers.BertTokenizer.from_pretrained(EMBEDDING_MODEL_NAME)
    # Save the tokenizer locally
    TOKENIZER.save_pretrained(local_tokenizer_path)