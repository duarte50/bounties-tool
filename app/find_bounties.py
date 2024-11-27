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

            scales = [1]  # Only checking scale = 1 for now

            match_count = 0  # To count number of matches

            for scale in scales:
                resized_template = template
                # resized_template = cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

                # Template matching
                result = cv2.matchTemplate(screenshot, resized_template, cv2.TM_CCOEFF_NORMED)
                threshold = 0.9

                # Get the positions and scores where the match is above the threshold
                match_locations = np.where(result >= threshold)
                scores = result[match_locations]

                # Convert match locations to bounding boxes
                boxes = []
                for (y, x), score in zip(zip(*match_locations), scores):
                    box = [x, y, x + resized_template.shape[1], y + resized_template.shape[0], score]
                    boxes.append(box)

                # Apply OpenCV's NMS
                boxes = np.array(boxes)
                if len(boxes) > 0:
                    indices = cv2.dnn.NMSBoxes(
                        boxes[:, :4].tolist(), boxes[:, 4].tolist(), threshold, 0.5
                    )
                    match_count += len(indices)

            return match_count  # Return the total count of matches

        except Exception as e:
            return 0
