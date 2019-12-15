from imagekit import ImageSpec, register
from imagekit.processors import ResizeToFill, ResizeToFit


class ThumbnailSmallSpec(ImageSpec):
    processors = [ResizeToFill(50, 50)]
    format = "JPEG"
    options = {"quality": 80}


class ThumbnailLargeSpec(ImageSpec):
    processors = [ResizeToFit(250, 250)]
    format = "JPEG"
    options = {"quality": 90}


register.generator("thumbnail-small", ThumbnailSmallSpec)
register.generator("thumbnail-large", ThumbnailLargeSpec)
