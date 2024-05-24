import os
import torch
import transformers
import torch.nn as nn
from torchcrf import CRF

# from model_keyphrases.global_var import BASE_MODEL_PATH
from model_keyphrases.global_var import EMBEDDING_MODEL_NAME

from huggingface_hub import PyTorchModelHubMixin

bert_model = None
# Define the local path and the Hugging Face model identifier
local_model_path = "./model_keyphrases/pretrained_model/bert-base-uncased"
# Check if the model is saved locally
if os.path.exists(local_model_path):
    # Load the model from the local path
    bert_model = transformers.BertModel.from_pretrained(local_model_path)
else:
    # Load the model from the Hugging Face Hub
    bert_model = transformers.BertModel.from_pretrained(EMBEDDING_MODEL_NAME,return_dict=False)
    # Save the model locally
    bert_model.save_pretrained(local_model_path)

class EntityModel(nn.Module, PyTorchModelHubMixin):
    def __init__(self, num_tag):
        super(EntityModel, self).__init__()
        self.num_tag = num_tag
        self.bert = bert_model
        self.bilstm= nn.LSTM(768, 1024 // 2, num_layers=1, bidirectional=True, batch_first=True)

        self.dropout_tag = nn.Dropout(0.3)

        self.hidden2tag_tag = nn.Linear(1024, self.num_tag)

        self.crf_tag = CRF(self.num_tag, batch_first=True)


    # return the loss only, not encode the tag
    def forward(self, ids, mask, token_type_ids, target_tag):
        x, _ = self.bert(ids, attention_mask=mask, token_type_ids=token_type_ids)
        h, _ = self.bilstm(x)

        o_tag = self.dropout_tag(h)
        tag = self.hidden2tag_tag(o_tag)
        mask = torch.where(mask==1, True, False)

        loss_tag = - self.crf_tag(tag, target_tag, mask=mask, reduction='token_mean')
        loss=loss_tag

        return loss


    # encode the tag, dont return loss
    def encode(self, ids, mask, token_type_ids, target_tag):
        # Bert - BiLSTM
        x, _ = self.bert(ids, attention_mask=mask, token_type_ids=token_type_ids)
        h, _ = self.bilstm(x)

        # drop out
        o_tag = self.dropout_tag(h)
        # o_pos = self.dropout_pos(h)

        # Hidden2Tag (Linear)
        tag = self.hidden2tag_tag(o_tag)
        mask = torch.where(mask==1, True, False)
        tag = self.crf_tag.decode(tag, mask=mask)

        return tag