import os
import sys
import math
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
from sklearn.metrics import mean_absolute_error, r2_score

sys.path.append(str(Path(__file__).parent.parent))
from common.config import *
from common.utility import *

DEVICE = torch.device('cuda:0')

MODEL_FILE = f"{DOWNLOAD_DIR}/transformer.pth"


# Based on "Attention is All You Need" - Vaswani et al. (2017) for "batch_first=True"
class PositionalEncoding(nn.Module):

    def __init__(self, d_model, max_len=512):
        super().__init__()
        pe = torch.zeros(max_len, d_model)

        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)

        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)

        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        seq_len = x.size(1)
        return x + self.pe[:, :seq_len, :].to(x.device)


def eval_model(model, dataloader):
    model.eval()
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for t_run_hour, t_input, t_time, t_temp in dataloader:
            t_run_hour = t_run_hour.to(DEVICE, non_blocking=True)
            t_input = t_input.to(DEVICE, non_blocking=True)
            t_time = t_time.to(DEVICE, non_blocking=True)

            with torch.amp.autocast('cuda'):
                preds = model(t_run_hour, t_input, t_time)

            all_preds.extend(preds.cpu().numpy().flatten())
            all_targets.extend(t_temp.numpy().flatten())

    return np.array(all_preds), np.array(all_targets)


def validate_model(model, dataloader, criterion):
    model.eval()
    total_loss = 0
    num_batches = 0

    with torch.no_grad():
        for t_run_hour, t_input, t_time, t_temp in dataloader:
            t_run_hour = t_run_hour.to(DEVICE, non_blocking=True)
            t_input = t_input.to(DEVICE, non_blocking=True)
            t_time = t_time.to(DEVICE, non_blocking=True)
            t_temp = t_temp.to(DEVICE, non_blocking=True)

            with torch.amp.autocast('cuda'):
                preds = model(t_run_hour, t_input, t_time)
                loss = criterion(preds, t_temp)

            total_loss += loss.item()
            num_batches += 1

    avg_loss = total_loss / num_batches
    return avg_loss


def final_eval(model, train_dataset, validation_dataset):
    train_preds, train_targets = eval_model(model, train_dataset)
    test_preds, test_targets = eval_model(model, validation_dataset)

    train_mae = mean_absolute_error(train_targets, train_preds)
    train_r2 = r2_score(train_targets, train_preds)
    test_mae = mean_absolute_error(test_targets, test_preds)
    test_r2 = r2_score(test_targets, test_preds)

    print_log(f"Training Performance:", Fore.YELLOW)
    print_log(f"  MAE: {train_mae:.4f}", Fore.CYAN)
    print_log(f"  R²: {train_r2:.4f}", Fore.CYAN)

    print_log(f"Testing Performance:", Fore.YELLOW)
    print_log(f"  MAE: {test_mae:.4f}", Fore.CYAN)
    print_log(f"  R²: {test_r2:.4f}", Fore.CYAN)

    torch.save(model.state_dict(), MODEL_FILE)


def prep_datasets(prep_data):
    prep_samples = []

    for entry in prep_data:
        t_run_hour = torch.tensor(entry['run_hour'], dtype=torch.float32)
        t_input = torch.tensor(entry['input'], dtype=torch.float32)

        temp_time = []
        temp_temp = []

        for item in entry['output']:
            temp_time.append(item['time'])
            temp_temp.append(item['temp'])

        t_time = torch.tensor(temp_time, dtype=torch.float32)
        t_temp = torch.tensor(temp_temp, dtype=torch.float32)

        prep_samples.append((t_run_hour, t_input, t_time, t_temp))

    return prep_samples


def create_dataset(data_samples):
    t_run_hours = torch.stack([sample[0] for sample in data_samples])
    t_inputs = torch.stack([sample[1] for sample in data_samples])
    t_times = torch.stack([sample[2] for sample in data_samples])
    t_temps = torch.stack([sample[3] for sample in data_samples])

    dataset = torch.utils.data.TensorDataset(t_run_hours, t_inputs, t_times, t_temps)
    return torch.utils.data.DataLoader(dataset,
                                       batch_size=128,
                                       shuffle=True,
                                       pin_memory=True,
                                       num_workers=os.cpu_count(),
                                       persistent_workers=True,
                                       prefetch_factor=4)
