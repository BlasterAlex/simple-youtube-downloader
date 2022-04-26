import urllib.request

from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPixmap, QImage


# Get youtube thumbnail
def get_youtube_thumbnail(url: str, width: int = -1) -> QPixmap:
    data = urllib.request.urlopen(url).read()
    image = QImage()
    image.loadFromData(data)

    img_width = image.width()
    img_height = int(img_width * 9 / 16)
    rect = QRect(
        0,
        int((image.height() - img_height) / 2),
        img_width,
        img_height,
    )
    image = image.copy(rect)

    pixmap = QPixmap(image)
    if width != -1:
        pixmap = pixmap.scaledToWidth(width)
    return pixmap
