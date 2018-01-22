from vision import *
from skimage import feature

def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    print(lower,upper)
    edged = cv2.Canny(image, lower, upper)
    # return the edged image
    return edged

def RoutineAlfalfaRedshift(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='redshift')
    # UpdateWindow('bgr', bgr, image_file.replace('downloaded/', 'temp/') + '.jpeg')
    bgr = Resize(bgr, 0.2)
    hsv = ToHSV(bgr)
    # UpdateWindow('hsv', hsv)

    EnablePaletteCreator(bgr, hsv)

    if True:
        mask = SegmentGoodPalette(hsv, 'colors.pkl' , 4.0)
        # mask = Dilate(mask)
        UpdateWindow('totalpalette', mask)
        UpdateWindow('foreground', MaskedImage(bgr, mask))
        UpdateWindow('background', MaskedImage(bgr, Inverted(mask)))

    #edges = np.uint8(feature.canny(BGRToGray(bgr), sigma=2.0, low_threshold=20, high_threshold=50, use_quantiles=False)) * 255
    #UpdateWindow('canny1', edges)

    # edged = auto_canny(bgr)
    #edged = cv2.Canny(bgr, 100, 200)
    #UpdateWindow('canny2', edged)