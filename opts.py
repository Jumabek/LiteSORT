"""
@Author: Du Yunhao
@Filename: opts.py
@Contact: dyh_bupt@163.com
@Time: 2022/2/28 19:41
@Discription: opts
"""
import json
import argparse
from os.path import join

data = {
    'MOT17': {
        'train': [
            'MOT17-02-FRCNN',
            'MOT17-04-FRCNN',
            'MOT17-05-FRCNN',
            'MOT17-09-FRCNN',
            'MOT17-10-FRCNN',
            'MOT17-11-FRCNN',
            'MOT17-13-FRCNN'
        ],
        'test': [
            'MOT17-01-FRCNN',
            'MOT17-03-FRCNN',
            'MOT17-06-FRCNN',
            'MOT17-07-FRCNN',
            'MOT17-08-FRCNN',
            'MOT17-12-FRCNN',
            'MOT17-14-FRCNN'
        ]
    },
    'MOT20': {
        'test': [
            'MOT20-04',
            'MOT20-06',
            'MOT20-07',
            'MOT20-08'
        ],
        'train': [
            'MOT20-01',
            'MOT20-02',
            'MOT20-03',
            'MOT20-05'
        ]
    },
    'KITTI': {
        'train': [
            "0000", "0002", "0004", "0006", "0008", "0010", "0012", "0014", "0016", "0018", "0020",
            "0001", "0003", "0005", "0007", "0009", "0011", "0013", "0015", "0017", "0019"
        ]

    }
}


class opts:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            'dataset',
            type=str,
            default='MOT17',
            help='MOT17 or MOT20',
        )
        self.parser.add_argument(
            'mode',
            type=str,
            help='val or test',
        )
        self.parser.add_argument(
            '--input_resolution',
            type=int,
            required=True,
            help='Resolution for input images (e.g., 1080 for 1920x1080)',
        )
        self.parser.add_argument(
            '--min_confidence',
            type=float,
            required=True,
            help='Minimum confidence threshold for detections',
        )

        self.parser.add_argument(
            '--precomputed_features',
            action='store_true',
            help='Uses pre-computed detections and apperance features',
            default=False
        )
        self.parser.add_argument(
            '--iou_only',
            action='store_true',
            help='Only use IOU matching',
            default=False
        )
        self.parser.add_argument(
            '--yolosort',
            action='store_true',
            help='Use integrated yolo apperance features from detector itself'
        )
        self.parser.add_argument(
            '--BoT',
            action='store_true',
            help='Replacing the original feature extractor with BoT'
        )
        self.parser.add_argument(
            '--ECC',
            action='store_true',
            help='CMC model'
        )
        self.parser.add_argument(
            '--NSA',
            action='store_true',
            help='NSA Kalman filter'
        )
        self.parser.add_argument(
            '--EMA',
            action='store_true',
            help='EMA feature updating mechanism'
        )
        self.parser.add_argument(
            '--MC',
            action='store_true',
            help='Matching with both appearance and motion cost'
        )
        self.parser.add_argument(
            '--woC',
            action='store_true',
            help='Replace the matching cascade with vanilla matching'
        )
        self.parser.add_argument(
            '--AFLink',
            action='store_true',
            help='Appearance-Free Link'
        )
        self.parser.add_argument(
            '--GSI',
            action='store_true',
            help='Gaussian-smoothed Interpolation'
        )
        self.parser.add_argument(
            '--root_dataset',
            default='datasets/'
        )
        self.parser.add_argument(
            '--path_AFLink',
            default='/data/dyh/results/StrongSORT_Git/AFLink_epoch20.pth'
        )
        self.parser.add_argument(
            '--dir_save',
            required=True,
            default='results/StrongSORT_Git/tmp'
        )
        self.parser.add_argument(
            '--EMA_alpha',
            default=0.9
        )
        self.parser.add_argument(
            '--MC_lambda',
            default=0.98
        )

    def parse(self, args=''):
        if args == '':
            opt = self.parser.parse_args()
        else:
            opt = self.parser.parse_args(args)
        # opt.min_confidence = 0.25
        # opt.min_confidence = 0.6  # original
        opt.nms_max_overlap = 1.0
        opt.min_detection_height = 0
        if opt.BoT:
            opt.max_cosine_distance = 0.4
            opt.dir_dets = 'results/StrongSORT_Git/{}_{}_YOLOX+BoT'.format(
                opt.dataset, opt.mode)
        else:
            opt.max_cosine_distance = 0.3
            opt.dir_dets = 'results/StrongSORT_Git/{}_{}_YOLOX+simpleCNN'.format(
                opt.dataset, opt.mode)
        if opt.MC:
            opt.max_cosine_distance += 0.05
        if opt.EMA:
            opt.nn_budget = 1
        else:
            opt.nn_budget = 100
        if opt.ECC:
            path_ECC = f'results/StrongSORT_Git/{opt.dataset}_ECC_{ opt.mode}.json'
            opt.ecc = json.load(open(path_ECC))
        opt.sequences = data[opt.dataset][opt.mode]
        opt.dir_dataset = join(
            opt.root_dataset,
            opt.dataset,
            opt.mode
        )
        return opt


opt = opts().parse()
