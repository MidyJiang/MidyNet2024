import time
import warnings
from datetime import datetime, timedelta
import os
import torch
import torch.nn.functional as F
import torch
import torch.nn as nn
from torchviz import make_dot
from transformers import AutoModelForSequenceClassification

import config
from module import MidyNet

flags=config.args

model_path= f'QFE.pt'
model = MidyNet(flags)
state_dict = torch.load(model_path)
model.load_state_dict(state_dict)
model.to(flags.device)
model.eval()
x=torch.zeros(flags.batch_size, flags.days, flags.max_num_text_len, 3, flags.max_num_tokens_len,dtype=torch.long).to(flags.device)
y=model(x)


graph = make_dot(y, params=dict(model.named_parameters()))
graph.render("midynet_structure", format="png")

