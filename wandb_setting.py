import os
import getpass
import wandb
import config

wandb_dir = f'/tmp/wandb_{getpass.getuser()}'
os.makedirs(wandb_dir, exist_ok=True)
MidyKey=r"************************************" #drawn from environ secret

settings = {
    'WANDB_ENTITY': 'midyjiang',  # WANDB account name
    'WANDB_DIR': wandb_dir,
    'WANDB_PROJECT': 'HAN_torch_FinBERT',  
    'WANDB_API_KEY': MidyKey,  
}

def wandb_config():
    for k, v in settings.items():
        os.environ[k] = v

def ini():
    wandb.login(key=MidyKey)

    flags = config.args

    wandb.init(project='FT_HAN',
               notes="2010.01.01-2024.07.18",
               tags=["3-class","follow-up yield","FT_Dataset",
                   "FT_HAN", "trial",  "full_time","6:3:1",
                     f"device:{flags.device}",
                     f"learning_rate:{flags.learning_rate}",
                     f"weight_decay:{flags.weight_decay}",
                     f"batch_size:{flags.batch_size}",
                     f"dr:{flags.dr}",
                     f"hidden_size:{flags.hidden_size}",
                     f"train_epochs:{flags.train_epochs}",
                     f"check_interval:{flags.check_interval}",
                     f"days:{flags.days}",
                     f"max_num_text_len:{flags.max_num_text_len}",
                     f"max_num_tokens_len:{flags.max_num_tokens_len}",  
                     ],
               # name='midy_name')
               )
