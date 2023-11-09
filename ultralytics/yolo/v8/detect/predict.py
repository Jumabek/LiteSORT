# Ultralytics YOLO 🚀, AGPL-3.0 license

import torch

from ultralytics.yolo.engine.predictor import BasePredictor
from ultralytics.yolo.engine.results import Results
from ultralytics.yolo.utils import DEFAULT_CFG, ROOT, ops
import cv2
import copy


class DetectionPredictor(BasePredictor):

    def postprocess(self, preds, img, orig_imgs, yolosort=False):

        # here img is [batchsize, channels, height, width] format
        """Postprocesses predictions and returns a list of Results objects."""
        """
        Additionally, it returns a low level apperance features of the detected objects.
        preds has 3 elements: yolo output (1,80+4,N), 3 anchor layer grids, first layer feature map
        
        """
        feature_map = preds[-1][0, :, :,
                                :]  # (16, 192, 320) # channel, height, width
        reshaped_feature_map = feature_map.permute(1, 2, 0)  # (192, 320, 16)

        # log self.args.conf
        preds = ops.non_max_suppression(preds,
                                        self.args.conf,
                                        self.args.iou,
                                        agnostic=self.args.agnostic_nms,
                                        max_det=self.args.max_det,
                                        classes=self.args.classes)

        # these will be scaled inside the loop
        pred_for_feature_map = copy.deepcopy(preds)

        results = []

        for i, pred in enumerate(preds):  # iterates through each detection
            orig_img = orig_imgs[i] if isinstance(
                orig_imgs, list) else orig_imgs
            if not isinstance(orig_imgs, torch.Tensor):
                pred[:, :4] = ops.scale_boxes(
                    img.shape[2:], pred[:, :4], orig_img.shape)

                # feature map extraction code for apperance based tracking
                # bounding boxes are in img.shape format, so we need to scale them to feature map resolution
                pred_for_feature_map[i][:, :4] = ops.scale_boxes(
                    img.shape[2:], pred_for_feature_map[i][:, :4], reshaped_feature_map.shape)

                boxes = pred_for_feature_map[i][:, :4].long()
                # convert boxes  to numpy array below
                boxes = boxes.cpu().numpy()

                if yolosort:
                    features_normalized = []
                    for box in boxes:
                        x_min, y_min, x_max, y_max = box
                        extracted_feature = feature_map[:,
                                                        y_min:y_max, x_min:x_max]
                        feature_mean = torch.mean(
                            extracted_feature, dim=(1, 2))

                        # L2 Normalize the feature
                        normalized_feature = feature_mean / \
                            feature_mean.norm(p=2, dim=0, keepdim=True)
                        features_normalized.append(normalized_feature)

                    if len(features_normalized) == 0:
                        # or any default tensor value you want to use
                        features = torch.tensor([])
                    else:
                        features = torch.stack(features_normalized, dim=0)
                else:
                    features = None

                # end of feature map extraction code

                path = self.batch[0]
                img_path = path[i] if isinstance(path, list) else path
                results.append(Results(orig_img=orig_img, path=img_path,
                                       names=self.model.names, boxes=pred, appearance_features=features))

        return results

        # for i, pred in enumerate(preds):  # iterateus through each detection
        #     orig_img = orig_imgs[i] if isinstance(
        #         orig_imgs, list) else orig_imgs
        #     if not isinstance(orig_imgs, torch.Tensor):
        #         pred[:, :4] = ops.scale_boxes(
        #             img.shape[2:], pred[:, :4], orig_img.shape)

        #         # bounding boxes are in img.shape format, so we need to scale them to feature map resolution
        #         pred_for_feature_map[i][:, :4] = ops.scale_boxes(
        #             img.shape[2:], pred_for_feature_map[i][:, :4], feature_map.shape)
        #         feature = ops.get_feature_map(
        #             feature_map, pred_for_feature_map[i][:, :4])

        #     path = self.batch[0]
        #     img_path = path[i] if isinstance(path, list) else path
        #     results.append(Results(orig_img=orig_img, path=img_path,
        #                    names=self.model.names, boxes=pred, feature_map_boxes=pred_for_feature_map))
        # return results


def predict(cfg=DEFAULT_CFG, use_python=False):
    """Runs YOLO model inference on input image(s)."""
    model = cfg.model or 'yolov8n.pt'
    source = cfg.source if cfg.source is not None else ROOT / 'assets' if (ROOT / 'assets').exists() \
        else 'https://ultralytics.com/images/bus.jpg'

    args = dict(model=model, source=source)
    if use_python:
        from ultralytics import YOLO
        YOLO(model)(**args)
    else:
        predictor = DetectionPredictor(overrides=args)
        predictor.predict_cli()


if __name__ == '__main__':
    predict()
