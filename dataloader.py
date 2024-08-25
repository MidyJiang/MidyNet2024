from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
import torch


class custom_dataset(Dataset):
    def __init__(self, x_path, y_path, days, max_num_text, max_num_tokens, num_class=3):
        #read dataset
        self.x = torch.tensor(pd.read_csv(x_path).iloc[:, 1:].values.reshape(-1, days, max_num_text, 3, max_num_tokens),
                              dtype=torch.int64)
        self.y = torch.tensor(pd.read_csv(y_path).iloc[:, 1:].values, dtype=torch.int64).view(-1)
        self.class_weights = self.y.shape[0] / (num_class * torch.bincount(self.y.int()))
        # print(f"weight shape:{self.class_weights}")

    def __len__(self):
        return self.y.shape[0]

    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]


def create_dataloader(flags):
    train_data = custom_dataset(flags.train_x_path, flags.train_y_path, flags.days, \
                                flags.max_num_text_len, flags.max_num_tokens_len)
    dev_data = custom_dataset(flags.dev_x_path, flags.dev_y_path, flags.days, \
                              flags.max_num_text_len, flags.max_num_tokens_len)
    test_data = custom_dataset(flags.test_x_path, flags.test_y_path, flags.days, \
                               flags.max_num_text_len, flags.max_num_tokens_len)

    train_loader = DataLoader(dataset=train_data, batch_size=flags.batch_size,
                              num_workers=flags.num_workers, shuffle=True, \
                              pin_memory=True, drop_last=False)
    dev_loader = DataLoader(dataset=dev_data, batch_size=flags.batch_size,
                            num_workers=flags.num_workers, shuffle=True, \
                            pin_memory=True, drop_last=False)
    test_loader = DataLoader(dataset=test_data, batch_size=flags.batch_size,
                             num_workers=flags.num_workers, shuffle=True, \
                             pin_memory=True, drop_last=False)

    return (train_loader, dev_loader, test_loader, train_data.class_weights,
            dev_data.class_weights, test_data.class_weights)
