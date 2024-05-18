from multiprocessing import Pool
from litesort_app import run
from opts import opt
import time
import warnings
from os.path import join
from tqdm import tqdm  # Import tqdm for the progress bar
warnings.filterwarnings("ignore")


def process_sequence(seq):
    # Use carriage return to rewrite the line
    print(f'\rProcessing video {seq}...', end='')
    path_save = join(opt.dir_save, seq + '.txt')
    run(
        sequence_dir=join(opt.dir_dataset, seq),
        output_file=path_save,
        min_confidence=opt.min_confidence,
        nms_max_overlap=opt.nms_max_overlap,
        min_detection_height=opt.min_detection_height,
        nn_budget=opt.nn_budget,
        display=False,
        verbose=False,
        device=opt.device
    )
    # The print statement here is modified to use a carriage return at the start.


if __name__ == '__main__':
    # Wrap the sequences with tqdm for a progress bar
    sequences = tqdm(opt.sequences)
    for sequence in sequences:
        process_sequence(sequence)
        # Update the description for tqdm progress bar
        sequences.set_description(f'Processing video {sequence}')

# Optional: Uncomment and modify the below block to use multiprocessing with progress updates.
# if __name__ == '__main__':
#     with Pool(processes=4) as pool:  # Adjust the number of processes based on your system's capability
#         list(tqdm(pool.imap(process_sequence, opt.sequences), total=len(opt.sequences)))
