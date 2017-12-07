cpdef unsigned char [:, :, :] segment(unsigned char [:, :, :] image, char w0, char w1, char w2, int threshold, int minimum_brightness):
    h = image.shape[0]
    w = image.shape[1]
    for x in range(w):
        for y in range (h):
            if (w0 * image[y, x, 0] + w1 * image[y, x, 1] + w2 * image[y, x, 2]) < threshold or (image[y, x, 0] + image[y, x, 1] + image[y, x, 2] < 3 * minimum_brightness):
                image[y, x, 0] = 255
                image[y, x, 1] = 0
                image[y, x, 2] = 0
    return image
