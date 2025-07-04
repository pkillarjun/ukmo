import os
import sys
import math
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path
from colorama import Fore
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

sys.path.append(str(Path(__file__).parent.parent))
from common.utility import *
from model.support import *


# https://docs.pytorch.org/docs/stable/generated/torch.nn.TransformerEncoderLayer.html
class WeatherEncoder(nn.Module):

    def __init__(self, ukmo_var_size, d_model, nhead, num_layers, dim_feedforward, dropout):
        super().__init__()
        self.d_model = d_model
        self.input_proj = nn.Linear(ukmo_var_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model)
        self.dropout = nn.Dropout(dropout)

        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model,
                                                   nhead=nhead,
                                                   dim_feedforward=dim_feedforward,
                                                   dropout=dropout,
                                                   batch_first=True)

        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)

    def forward(self, t_input):
        t_input = self.input_proj(t_input) * math.sqrt(self.d_model)
        t_input = self.pos_encoding(t_input)
        t_input = self.dropout(t_input)
        return self.transformer(t_input)


# https://docs.pytorch.org/docs/stable/generated/torch.nn.TransformerDecoderLayer.html
# Implements smooth rounding from https://arxiv.org/abs/2504.19026
class TemperatureDecoder(nn.Module):

    def __init__(self, run_enc_size, fcst_enc_size, fcst_steps, d_model, nhead, num_layers, dim_feedforward, dropout):
        super().__init__()
        self.d_model = d_model
        self.fcst_steps = fcst_steps
        self.input_proj = nn.Linear((run_enc_size + fcst_enc_size), d_model)
        self.pos_encoding = PositionalEncoding(d_model)
        self.dropout = nn.Dropout(dropout)

        decoder_layer = nn.TransformerDecoderLayer(d_model=d_model,
                                                   nhead=nhead,
                                                   dim_feedforward=dim_feedforward,
                                                   dropout=dropout,
                                                   batch_first=True)

        self.transformer = nn.TransformerDecoder(decoder_layer, num_layers)
        self.output_proj = nn.Linear(d_model, 1)

    def sigmoid(self, z):
        return 1 / (1 + torch.exp(-z))

    def smooth_round_sigma(self, x, k):
        result = torch.zeros_like(x)

        # Get range of integers to consider (5 neighbors for efficiency)
        x_floor = torch.floor(x)

        for offset in range(-2, 3):  # n in [floor(x)-2, floor(x)+2]
            n = x_floor + offset

            # Sigmoid window: σ(k(x-(n-0.5))) - σ(k(x-(n+0.5)))
            sig_left = self.sigmoid(k * (x - (n - 0.5)))
            sig_right = self.sigmoid(k * (x - (n + 0.5)))
            window = sig_left - sig_right

            result += n * window

        return result

    def forward(self, enc_output, t_run_hour, t_time, epoch=None, max_epochs=None):
        # Broadcast model run encoding to all fcst timesteps
        run_enc_expand = t_run_hour.unsqueeze(1).repeat(1, self.fcst_steps, 1)

        # Combine model run encoding + target fcst times as decoder input for cross-attention
        decoder_input = torch.cat([run_enc_expand, t_time], dim=2)
        decoder_input = self.input_proj(decoder_input) * math.sqrt(self.d_model)
        decoder_input = self.pos_encoding(decoder_input)
        decoder_input = self.dropout(decoder_input)

        # Ensures autoregressive training: each timestep can only attend to previous timesteps
        tgt_mask = nn.Transformer.generate_square_subsequent_mask(decoder_input.size(1)).to(decoder_input.device)

        # Cross-attention: time queries attend to weather history with causal masking
        output = self.transformer(decoder_input, enc_output, tgt_mask=tgt_mask)

        # Project to temperature values and remove singleton dimension
        temps = self.output_proj(output).squeeze(-1)

        if self.training:
            # Reach k=20 by 1/2 of training (before typical early stopping)
            target_epoch = max_epochs // 2
            progress = min(epoch / target_epoch, 1.0)
            k = 5 + progress * 15  # k: 5→20
        else:
            # Fixed k=15 for validation/testing (middle ground sharpness)
            k = 15

        return self.smooth_round_sigma(temps, k)


class WeatherModel(nn.Module):

    def __init__(self, ukmo_var_size, run_enc_size, fcst_enc_size, fcst_steps, d_model, nhead, enc_layers, dec_layers,
                 dim_feedforward, dropout):
        super().__init__()
        self.encoder = WeatherEncoder(ukmo_var_size, d_model, nhead, enc_layers, dim_feedforward, dropout)
        self.decoder = TemperatureDecoder(run_enc_size, fcst_enc_size, fcst_steps, d_model, nhead, dec_layers, dim_feedforward,
                                          dropout)

    def forward(self, t_run_hour, t_input, t_time, epoch=None, max_epochs=None):
        enc_output = self.encoder(t_input)
        return self.decoder(enc_output, t_run_hour, t_time, epoch, max_epochs)


def train_model(model, train_dataset, validation_dataset, params):
    criterion = nn.MSELoss()
    scaler = torch.amp.GradScaler('cuda')
    optimizer = optim.AdamW(model.parameters(), lr=params['learning_rate'], weight_decay=params['l2_reg_weight'])
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=15, min_lr=1e-6)

    epochs = params['epochs']
    model.to(DEVICE)

    es_loss = float('inf')
    es_counter = 0
    es_patience = 30
    es_model_state = None

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        num_batches = 0

        for t_run_hour, t_input, t_time, t_temp in train_dataset:
            t_run_hour = t_run_hour.to(DEVICE, non_blocking=True)
            t_input = t_input.to(DEVICE, non_blocking=True)
            t_time = t_time.to(DEVICE, non_blocking=True)
            t_temp = t_temp.to(DEVICE, non_blocking=True)

            optimizer.zero_grad()

            # Mixed precision forward pass and loss calculation
            with torch.amp.autocast('cuda'):
                preds = model(t_run_hour, t_input, t_time, epoch=epoch, max_epochs=epochs)
                loss = criterion(preds, t_temp)

            # Backward pass: scale loss → compute gradients → unscale for clipping
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)

            # Prevent gradient explosion by clipping gradient norm to 1.0
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            # Apply optimizer step and update mixed precision scaler
            scaler.step(optimizer)
            scaler.update()

            epoch_loss += loss.item()
            num_batches += 1

        avg_loss = validate_model(model, validation_dataset, criterion)
        scheduler.step(avg_loss)

        if avg_loss < es_loss:
            es_loss = avg_loss
            es_counter = 0
            es_model_state = model.state_dict()
            print_log(f"New best model at epoch {epoch+1} with val loss: {es_loss:.4f}", Fore.GREEN)
        else:
            es_counter += 1

        if es_counter >= es_patience:
            print_log(f"Early stopping triggered at epoch {epoch+1}. Best val loss: {es_loss:.4f}", Fore.YELLOW)
            model.load_state_dict(es_model_state)
            break

        if (epoch + 1) % 5 == 0:
            train_loss = epoch_loss / num_batches
            current_lr = scheduler.get_last_lr()[0]
            print_log(
                f"Epoch [{epoch+1}/{epochs}], Loss: {train_loss:.4f}, Val Loss: {avg_loss:.4f}, "
                f"LR: {current_lr:.6f}, Patience: {es_counter}/{es_patience}", Fore.BLUE)

    if es_model_state is not None and es_counter < es_patience:
        print_log(f"Loading best model with val loss: {es_loss:.4f}", Fore.GREEN)
        model.load_state_dict(es_model_state)

    final_eval(model, train_dataset, validation_dataset)


def train_transformer(training_data):
    train_data, eval_data = train_test_split(training_data, test_size=0.1, random_state=69)

    _train_data = prep_datasets(train_data)
    train_dataset = create_dataset(_train_data)
    print_log(f"Generated {len(_train_data)} training samples", Fore.BLUE)

    _eval_data = prep_datasets(eval_data)
    eval_dataset = create_dataset(_eval_data)
    print_log(f"Generated {len(_eval_data)} evaluation samples", Fore.BLUE)

    print_log(f"Split data: {len(train_data)} train, {len(eval_data)} eval samples", Fore.CYAN)

    run_enc_size = len(train_data[0]['run_hour'])
    ukmo_var_size = len(train_data[0]['input'][0])
    fcst_steps = len(train_data[0]['output'])
    fcst_enc_size = len(train_data[0]['output'][0]['time'])

    model = WeatherModel(ukmo_var_size=ukmo_var_size,
                         run_enc_size=run_enc_size,
                         fcst_enc_size=fcst_enc_size,
                         fcst_steps=fcst_steps,
                         d_model=256,
                         nhead=8,
                         enc_layers=6,
                         dec_layers=4,
                         dim_feedforward=1024,
                         dropout=0.1)

    params = {'learning_rate': 0.0001, 'epochs': 500, 'l2_reg_weight': 0.001}

    print_log(f"Training Transformer model with params: {params}", Fore.YELLOW)
    train_model(model, train_dataset, eval_dataset, params)


def test_transformer(testing_data):
    test_data = prep_datasets(testing_data)
    test_dataset = create_dataset(test_data)
    print_log(f"Generated {len(test_data)} testing samples", Fore.BLUE)

    run_enc_size = len(testing_data[0]['run_hour'])
    ukmo_var_size = len(testing_data[0]['input'][0])
    fcst_steps = len(testing_data[0]['output'])
    fcst_enc_size = len(testing_data[0]['output'][0]['time'])

    model = WeatherModel(ukmo_var_size=ukmo_var_size,
                         run_enc_size=run_enc_size,
                         fcst_enc_size=fcst_enc_size,
                         fcst_steps=fcst_steps,
                         d_model=256,
                         nhead=8,
                         enc_layers=6,
                         dec_layers=4,
                         dim_feedforward=1024,
                         dropout=0.1)

    model.load_state_dict(torch.load(MODEL_FILE))
    model.to(DEVICE)
    model.eval()

    print_log("Model Predictions vs Actual Values:", Fore.YELLOW)
    print_log("=" * 80, Fore.MAGENTA)

    sample_idx = 0
    with torch.no_grad():
        for t_run_hour, t_input, t_time, t_temp in test_dataset:
            t_run_hour = t_run_hour.to(DEVICE, non_blocking=True)
            t_input = t_input.to(DEVICE, non_blocking=True)
            t_time = t_time.to(DEVICE, non_blocking=True)

            with torch.amp.autocast('cuda'):
                preds = model(t_run_hour, t_input, t_time)

            for i in range(preds.size(0)):
                predicted_temps = preds[i].cpu().numpy()
                actual_temps = t_temp[i].numpy()

                print_log(f"\nSample {sample_idx + 1}:", Fore.CYAN)
                print_log(f"{'Hour':<9} {'Predicted':<12} {'Actual':<12} {'Diff'}", Fore.MAGENTA)
                print_log("-" * 42, Fore.MAGENTA)

                for j, (pred, actual) in enumerate(zip(predicted_temps, actual_temps)):
                    diff = abs(pred - actual)
                    print_log(f"{j:>4}   {pred:>8.2f}     {actual:>8.2f}     {diff:>7.2f}", Fore.GREEN)

                mae_sample = mean_absolute_error(actual_temps, predicted_temps)
                r2_sample = r2_score(actual_temps, predicted_temps)
                print_log(f"Sample MAE: {mae_sample:.4f}, R²: {r2_sample:.4f}", Fore.BLUE)

                sample_idx += 1

    test_preds, test_targets = eval_model(model, test_dataset)
    test_mae = mean_absolute_error(test_targets, test_preds)
    test_r2 = r2_score(test_targets, test_preds)

    print_log(f"\nOverall Test Performance:", Fore.YELLOW)
    print_log(f"  MAE: {test_mae:.4f}", Fore.CYAN)
    print_log(f"  R²: {test_r2:.4f}", Fore.CYAN)
