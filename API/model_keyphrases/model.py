import torch
import transformers
import torch.nn as nn
from torchcrf import CRF

from model_keyphrases.global_var import BASE_MODEL_PATH

class EntityModel(nn.Module):
    def __init__(self, num_tag):
        super(EntityModel, self).__init__()
        self.num_tag = num_tag
        self.bert = transformers.BertModel.from_pretrained(BASE_MODEL_PATH,return_dict=False)
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