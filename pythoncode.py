#!/bin/bash
from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained("intfloat/e5-base")
model = AutoModel.from_pretrained("intfloat/e5-base")

input = tokenizer("Hello world test hsmen dndne ornrme donf foogm snmfnon fonf  ofgn ond f fngon", return_tensors="pt")
emb = model(**input).last_hidden_state.mean(dim=1)

print(emb.shape)
print(emb)
