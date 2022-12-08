from paddleocr import PaddleOCR, draw_ocr
import cv2


language = "ch"  # Chinese & English
# anguage = "en"  English
pd_ocr = PaddleOCR(use_angle_cls=True, use_gpu=True, lang=language)


# The model file will be downloaded automatically when executed for the first time


def read_resized_cv2_image(image_file, resize_rate=None):
    if resize_rate is None:
        cv_image = cv2.imread(image_file)
    else:
        cv_image = cv2.imread(image_file)
        (h, w) = cv_image.shape[:2]
        dim = (int(h * resize_rate), int(w * resize_rate))
        cv_image = cv2.resize(cv_image, dim, interpolation=cv2.INTER_AREA)
    return cv_image


def ocr(image_file, cv_image=None, resize_rate=None):
    if cv_image is None:
        cv_image = read_resized_cv2_image(image_file, resize_rate)
    cv_image = cv_image[75:1920, 0:1080]
    # Paddle一般是一个文本块作为一个检测结果"""
    paddle_result = pd_ocr.ocr(cv_image, cls=True)
    # print(paddle_result)
    word2_loc = {}
    boxes = []
    text = []
    for region in paddle_result:
        # Paddle box may have rotations
        # print(region)
        lt, rt, rb, lb = tuple(region[0])
        x_min = int(min(lt[0], rt[0], rb[0], lb[0]))
        x_max = int(max(lt[0], rt[0], rb[0], lb[0]))
        y_min = int(min(lt[1], rt[1], rb[1], lb[1]))
        y_max = int(max(lt[1], rt[1], rb[1], lb[1]))
        word = region[1][0]
        word2_loc[word] = [x_min, y_min, x_max - x_min, y_max - y_min]

    word2_loc = sorted(word2_loc.items(), key=lambda x: x[1][1])

    for item in word2_loc:
        text.append(item[0])
        boxes.append(item[1])

    return text, boxes


if __name__ == "__main__":
    text, boxes = ocr("E:\PythonProject\Datainput\data\\trivago\screen_2022-07-31_132558.png")
    print(text)
    print(boxes)
    # pass






