# AMD GPU ROCm Setup Guide for Fedora

A complete guide for setting up AMD ROCm with PyTorch on Fedora Linux, including GPU compatibility workarounds.

## Installation

### Install ROCm Packages

Install all ROCm packages and development libraries:

```bash
# Install all ROCm packages
sudo dnf install -y rocm*

# Install specific development packages
sudo dnf install -y \
    rocblas \
    rocblas-devel \
    rocsparse \
    rocsparse-devel \
    rocfft \
    rocfft-devel \
    rocrand \
    rocrand-devel \
    rccl \
    rccl-devel \
    miopen \
    miopen-devel \
    hipcub-devel \
    rocthrust-devel
```

### Install PyTorch

Install [PyTorch](https://pytorch.org/get-started/locally/) with ROCm support:

```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.3
```

### User Group Configuration

Add your user to the required groups for GPU access:

```bash
sudo usermod -a -G video,render $USER
groups $USER
```

**Note:** Reboot after adding user to groups for changes to take effect.

## Environment Configuration

### GPU Compatibility Setup

Set environment variables to ensure proper GPU recognition:

```bash
# Make ROCm think both GPUs are gfx1030
export HSA_OVERRIDE_GFX_VERSION=10.3.0

# Only use GPU 0 (RX 6800M)
export HIP_VISIBLE_DEVICES=0
export ROCR_VISIBLE_DEVICES=0
```

### Verify GPU Detection

Check that your GPU is properly detected:

```bash
# Full GPU information
rocminfo | grep -E "(Agent|Name|gfx)"

# Just GFX version
rocminfo | grep gfx
```

## Testing

### Basic GPU Detection Test

Verify PyTorch can detect and use your AMD GPU:

```python
import torch
print('Device count:', torch.cuda.device_count())
print('Device name:', torch.cuda.get_device_name(0))
print('Memory:', torch.cuda.get_device_properties(0).total_memory / 1024**3, 'GB')
```

### Performance Benchmark Test

Run a matrix multiplication benchmark to test GPU performance:

```python
import torch
import time

device = torch.device('cuda:0')
a = torch.randn(5000, 5000, device=device)
b = torch.randn(5000, 5000, device=device)

start = time.time()
for i in range(100):
    c = torch.mm(a, b)
torch.cuda.synchronize()
end = time.time()

print(f'Time taken: {end - start:.2f} seconds')
```

## Troubleshooting

- If GPU is not detected, ensure you've rebooted after adding user to groups
- Verify environment variables are set in your shell profile
- Check that the symlinks were created correctly in the PyTorch library directory
- Make sure you're using the correct Python version (3.13 in this case)

## Notes

- This setup is specifically configured for RX 6800M GPU
- The GFX version override (10.3.0) may need adjustment for different GPU models
- Environment variables should be added to your shell profile for persistence
