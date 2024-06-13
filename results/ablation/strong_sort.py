"""
@Author: Du Yunhao
@Filename: strong_sort.py
@Contact: dyh_bupt@163.com
@Time: 2022/2/28 20:14
@Discription: Run StrongSORT
"""
from deep_sort_app import run
from opts import opt
import time
import warnings
from os.path import join
warnings.filterwarnings("ignore")

if __name__ == '__main__':
    for i, seq in enumerate(opt.sequences, start=1):
        print('processing the {}th video {}...'.format(i, seq))
        path_save = join(opt.dir_save, seq + '.txt')
        tick = time.time()
        run(
            sequence_dir=join(opt.dir_dataset, seq),
            detection_file=join(opt.dir_dets, seq + '.npy'),
            output_file=path_save,
            min_confidence=opt.min_confidence,
            nms_max_overlap=opt.nms_max_overlap,
            min_detection_height=opt.min_detection_height,
            max_cosine_distance=opt.max_cosine_distance,
            nn_budget=opt.nn_budget,
            display=False
        )
