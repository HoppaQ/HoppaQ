import cv2 as cv
import numpy as np
from PIL import Image


def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
    """Return a sharpened version of the image, using an unsharp mask."""
    blurred = cv.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)
    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
    return sharpened


if __name__ == "__main__":
    image = cv.imread('Cropped_images/image_crop_num104.jpg')

    # im = Image.open("Cropped_images/image_crop_num104.jpg")
    # im.save("test-600.png", dpi=(1024,1024))

    size = 200, int(200*image.shape[0]/image.shape[1])
    im = Image.open("Cropped_images/image_crop_num104.jpg")
    im_resized = im.resize(size, Image.ANTIALIAS)
    im_resized.save("my_image_resized.png", "PNG")
    image = cv.imread('my_image_resized.png')

    kernel = np.array([[-1, -1, -1], 
                   [-1, 9,-1], 
                   [-1, -1, -1]])

    # Sharpen image
    image_sharp = cv.filter2D(image, -1, kernel)
    # sharpened_image = unsharp_mask(image)
    cv.imwrite('my-sharpened-image.jpg', image_sharp)