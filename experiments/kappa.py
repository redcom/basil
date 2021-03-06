from vision import *

measurements = []
jitter = []

def RoutineKappa(image_file, bgr, box):
    bgr = CropImage(bgr, cropname='blueshift')
    bgr = Resize(bgr, 0.5)
    hsv = ToHSV(bgr)
    hsv = MedianBlurred(hsv, size=5)
    try:
        read_mean,read_std = LoadColorStats('kappa.temp')
    except:
        read_mean = (41, 200, 183)
        read_std = (2, 30, 17)

    h = cv2.split(hsv)[0]
    s = cv2.split(hsv)[1]
    v = cv2.split(hsv)[2]

    h = SimilarityToReference(h, read_mean[0])
    h = TruncateAndZero(h, 255, max(4, read_std[0]), 0.0, 2.8)

    s = TruncateAndZero(s, read_mean[1], max(28, read_std[1]), 2.0, 3.0)
    v = TruncateAndZero(v, read_mean[2], max(20, read_std[1]), 1.0, 3.0)

    UpdateWindow('hsv', hsv)
    UpdateWindow('dh', h)
    UpdateWindow('ds', s)
    UpdateWindow('dv', v)

    mult = cv2.multiply(h, cv2.multiply(v, s, scale=1.0/255.0), scale=1.0/255.0)
    Normalize(mult)

    # print(ExifKeywords(image_file))

    mult_bgr = GrayToBGR(mult)
    inv_mult_bgr = GrayToBGR(255 - mult)
    foreground = cv2.multiply(mult_bgr, bgr, scale=1.0/255.0)
    background = cv2.multiply(inv_mult_bgr, bgr, scale=1.0/255.0)
    UpdateWindow('back', background)
    biomass = cv2.mean(mult)[0] / 231.0 * 100.0
    Echo(foreground, 'biomass p-index %.1f' % (biomass))
    biomass = biomass + 10
    if len(measurements) > 0:
        smooth_biomass = 0.5 * biomass + 0.5 * measurements[-1]
        jitter.append(biomass - smooth_biomass)
        biomass = smooth_biomass
        jit = np.std(jitter)
        print('jitter %.3f hue %.1f' % (jit, read_mean[0]))
    measurements.append(biomass)
    h,w = bgr.shape[:2]
    for i in range(1, len(measurements)):
        last = measurements[i]
        previous = measurements[i - 1]
        cv2.line(foreground, ((i - 1) * 10 + 50, int(h - previous * 9)), (i * 10 + 50, int(h - last * 9)), (255, 255, 255), 3)
    UpdateWindow('foreground', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')
    # update stats
    ret,mask = cv2.threshold(mult, 250, 255, cv2.THRESH_BINARY)
    (mean_biomass,stddev_biomass) = cv2.meanStdDev(hsv, mask=mask)[0:3]
    print(mean_biomass, stddev_biomass)
    print('')
    mean_biomass[0] = read_mean[0] * 0.0 + 1.0 * mean_biomass[0]
    SaveColorStats(mean_biomass, stddev_biomass, 'kappa.temp')
