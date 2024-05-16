# Ultralytics YOLO 🚀, AGPL-3.0 license

import torch

from ultralytics.yolo.engine.predictor import BasePredictor
from ultralytics.yolo.engine.results import Results
from ultralytics.yolo.utils import DEFAULT_CFG, ROOT, ops
import cv2
import copy


class DetectionPredictor(BasePredictor):
    def postprocess_original(self, preds, img, orig_imgs):

        # here img is [batchsize, channels, height, width] format
        """Postprocesses predictions and returns a list of Results objects."""
        """
        Additionally, it returns a low level apperance features of the detected objects.
        preds has 3 elements: yolo output (1,80+4,N), 3 anchor layer grids, first layer feature map

        """

        # log self.args.conf
        preds = ops.non_max_suppression(preds,
                                        self.args.conf,
                                        self.args.iou,
                                        agnostic=self.args.agnostic_nms,
                                        max_det=self.args.max_det,
                                        classes=self.args.classes)

        results = []

        for i, pred in enumerate(preds):  # iterates through each detection
            orig_img = orig_imgs[i] if isinstance(
                orig_imgs, list) else orig_imgs
            if not isinstance(orig_imgs, torch.Tensor):
                pred[:, :4] = ops.scale_boxes(
                    img.shape[2:], pred[:, :4], orig_img.shape)

                path = self.batch[0]
                img_path = path[i] if isinstance(path, list) else path
                results.append(Results(orig_img=orig_img, path=img_path,
                                       names=self.model.names, boxes=pred, appearance_features=None))

        return results

    def postprocess_new(self, preds, img, orig_imgs, appearance_feature_layer=None):
        """Postprocesses predictions to return a list of Results objects, possibly including appearance features."""
        if appearance_feature_layer is None:
            # if 1 == 1:
            return self.postprocess_original(preds, img, orig_imgs)

        results = []

        # Handle appearance feature extraction if specified
        feature_maps = []
        preds_copy = copy.deepcopy(preds)
        if appearance_feature_layer == 'layerconcat':
            # Specify the layer indices you want to concatenate
            layers = [0, 1, 3, 5, 7]
            feature_maps = [self.extract_appearance_features(
                preds_copy, f'layer{layer}') for layer in layers]
        elif appearance_feature_layer is not None:
            feature_maps = [self.extract_appearance_features(
                preds_copy, appearance_feature_layer)]

        # Non-Max Suppression on predictions
        preds = ops.non_max_suppression(preds, self.args.conf, self.args.iou,
                                        agnostic=self.args.agnostic_nms, max_det=self.args.max_det, classes=self.args.classes)

        # Process each prediction to create results
        for i, pred in enumerate(preds):
            orig_img = orig_imgs[i] if isinstance(
                orig_imgs, list) else orig_imgs
            pred[:, :4] = ops.scale_boxes(
                img.shape[2:], pred[:, :4], orig_img.shape)  # Scale bounding boxes

            features = None
            if feature_maps:
                features = self.extract_and_concatenate_features(
                    preds_copy[i], feature_maps, img.shape)

            img_path = self.get_image_path(i)
            results.append(Results(orig_img=orig_img, path=img_path,
                                   names=self.model.names, boxes=pred, appearance_features=features))

        return results

    def extract_appearance_features(self, preds, layer_index):
        """Extract and reshape the appearance feature map from predictions."""
        feature_map = preds[-1][layer_index][0]  # (channel, height, width)
        reshaped_feature_map = feature_map.permute(1, 2, 0)
        return reshaped_feature_map

    def extract_and_concatenate_features(self, pred, feature_maps, img_shape):
        """Extract features for given bounding boxes from multiple feature maps and concatenate them."""
        concatenated_features = []
        for feature_map in feature_maps:

            feature_dim = feature_map.shape[0]
            boxes = ops.scale_boxes(
                img_shape[2:], pred[:, :4], feature_map.shape).long()
            features_normalized = []
            for box in boxes.cpu().numpy():
                x_min, y_min, x_max, y_max = box
                extracted_feature = feature_map[:, y_min:y_max, x_min:x_max]

                if 0 not in extracted_feature.shape:
                    feature_mean = torch.mean(extracted_feature, dim=(1, 2))
                    normalized_feature = feature_mean / \
                        feature_mean.norm(p=2, dim=0, keepdim=True)
                else:
                    normalized_feature = torch.ones(
                        feature_dim, dtype=torch.float32, device=feature_map.device)
                # print("normalized_feature.shape", normalized_feature.shape)
                # print("appending, normalized_feature.shape",
                #      normalized_feature.shape)
                features_normalized.append(normalized_feature)

            if features_normalized:
                print("torch.stack(features_normalized, dim=0).shape=",
                      torch.stack(features_normalized, dim=0).shape)
                concatenated_features.append(
                    torch.stack(features_normalized, dim=0))
            else:
                concatenated_features.append(torch.tensor([]))

        if concatenated_features:
            # Concatenate along feature dimension
            return torch.cat(concatenated_features, dim=1)
        return torch.tensor([])

    def get_image_path(self, index):
        """Retrieve the path for the image at the specified index."""
        path = self.batch[0]
        return path[index] if isinstance(path, list) else path

    def postprocess(self, preds, img, orig_imgs, appearance_feature_layer=None):

        # here img is [batchsize, channels, height, width] format
        """Postprocesses predictions and returns a list of Results objects."""
        """
        Additionally, it returns a low level apperance features of the detected objects.
        preds has 3 elements: yolo output (1,80+4,N), 3 anchor layer grids, first layer feature map

        """
        if appearance_feature_layer:
            feature_map = preds[-1][appearance_feature_layer][0, :, :,
                                                              :]  # (48, 368, 640) # channel, height, width for yolov8m
            reshaped_feature_map = feature_map.permute(
                1, 2, 0)  # (192, 320, 48)?, #
            feature_dim = reshaped_feature_map.shape[-1]

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

                if appearance_feature_layer is None:
                    path = self.batch[0]
                    img_path = path[i] if isinstance(path, list) else path
                    results.append(Results(orig_img=orig_img, path=img_path,
                                           names=self.model.names, boxes=pred, appearance_features=None))
                    continue

                # feature map extraction code for apperance based tracking
                # bounding boxes are in img.shape format, so we need to scale them to feature map resolution
                pred_for_feature_map[i][:, :4] = ops.scale_boxes(
                    img.shape[2:], pred_for_feature_map[i][:, :4], reshaped_feature_map.shape)

                boxes = pred_for_feature_map[i][:, :4].long()
                # convert boxes  to numpy array below
                boxes = boxes.cpu().numpy()

                features_normalized = []
                for box in boxes:
                    x_min, y_min, x_max, y_max = box
                    extracted_feature = feature_map[:,
                                                    y_min:y_max, x_min:x_max]
                    # takes care of the case out of the feature map bboxes
                    if 0 not in extracted_feature.shape:
                        feature_mean = torch.mean(
                            extracted_feature, dim=(1, 2))

                        # L2 Normalize the feature
                        normalized_feature = feature_mean / \
                            feature_mean.norm(p=2, dim=0, keepdim=True)
                    else:
                        normalized_feature = torch.ones(
                            feature_dim, dtype=torch.float32, device=feature_map.device)
                    features_normalized.append(normalized_feature)

                if len(features_normalized) == 0:
                    # or any default tensor value you want to use
                    features = torch.tensor([])
                else:
                    features = torch.stack(features_normalized, dim=0)

                # end of feature map extraction code

                path = self.batch[0]
                img_path = path[i] if isinstance(path, list) else path
                results.append(Results(orig_img=orig_img, path=img_path,
                                       names=self.model.names, boxes=pred, appearance_features=features))

        return results


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
