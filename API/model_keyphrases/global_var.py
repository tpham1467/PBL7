import transformers

global MAX_LEN 
MAX_LEN = 256
# global BASE_MODEL_PATH
# BASE_MODEL_PATH = "./model_keyphrases/pretrained_model/bert-base-uncased"
# global MODEL_PATH
# MODEL_PATH = "model_keyphrases/models/trained_model"

global EMBEDDING_MODEL_NAME
EMBEDDING_MODEL_NAME="bert-base-uncased"

global TOKENIZER
TOKENIZER = transformers.BertTokenizer.from_pretrained(
    EMBEDDING_MODEL_NAME,
    do_lower_case=True
)