import os
import torch

for gpu_id in range(4):  # Assuming 4 GPUs
    device = torch.device(f'cuda:{gpu_id}')
    try:
        # Check if GPU is available and print its name
        if torch.cuda.is_available():
            torch.cuda.set_device(device)
            print(f"GPU {gpu_id} is available and set to: {torch.cuda.get_device_name(gpu_id)}")
        else:
            print(f"GPU {gpu_id} is not available.")
    except Exception as e:
        print(f"Error accessing GPU {gpu_id}: {e}")
