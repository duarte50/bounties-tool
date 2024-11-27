import cv2
import numpy as np
import pyautogui

class FindBounties:
    def __init__(self):
        self.template_cache = {}

    def find_item(self, item_name, region):
        try:
            screenshot = pyautogui.screenshot(region=region)
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

            # Load the template image
            image_path = f"assets/bounties/{item_name}.png"
            if image_path not in self.template_cache:
                template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                self.template_cache[image_path] = template
                if template is None:
                    print(f"Template image not found: {image_path}")
                    return 0
            else:
                template = self.template_cache[image_path]

            match_count = 0  # To count number of matches

            # Template matching
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.9  # Threshold for template matching

            # Get the positions and scores where the match is above the threshold
            match_locations = np.where(result >= threshold)
            scores = result[match_locations]

            # Convert match locations to bounding boxes
            boxes = []
            for (y, x), score in zip(zip(*match_locations), scores):
                box = [x, y, x + template.shape[1], y + template.shape[0], score]
                boxes.append(box)

            boxes = np.array(boxes)
            if len(boxes) > 0:
                # Apply Non-Maximum Suppression (NMS) to remove redundant boxes
                indices = self.nms(boxes, 0.5)
                match_count += len(indices)

            return match_count  # Return the total count of matches

        except Exception as e:
            return 0

    def nms(self, boxes, threshold):
        if len(boxes) == 0:
            return []

        # Sort the boxes by their score in descending order
        boxes = boxes[boxes[:, 4].argsort()[::-1]]
        selected_boxes = []

        while len(boxes) > 0:
            # Select the box with the highest score
            box = boxes[0]
            selected_boxes.append(box)

            # Calculate IoU (Intersection over Union) between the selected box and the rest
            remaining_boxes = []
            for b in boxes[1:]:
                iou = self.iou(box, b)
                if iou < threshold:  # If IoU is below threshold, keep the box
                    remaining_boxes.append(b)

            boxes = np.array(remaining_boxes)

        return selected_boxes

    def iou(self, box1, box2):
        x1, y1, x2, y2, _ = box1
        x1b, y1b, x2b, y2b, _ = box2

        # Calculate the coordinates of the intersection rectangle
        ix1 = max(x1, x1b)
        iy1 = max(y1, y1b)
        ix2 = min(x2, x2b)
        iy2 = min(y2, y2b)

        # Compute area of intersection
        intersection_area = max(0, ix2 - ix1) * max(0, iy2 - iy1)

        # Compute area of both boxes
        box1_area = (x2 - x1) * (y2 - y1)
        box2_area = (x2b - x1b) * (y2b - y1b)

        # Compute IoU
        iou = intersection_area / float(box1_area + box2_area - intersection_area)
        return iou
