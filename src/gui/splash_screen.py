from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


class SplashScreen(QtWidgets.QSplashScreen):
    def __init__( self, pixmap: QtGui.QPixmap, radius: int = 22, message_offset: int = 24,
        message_point_size: int = 16, border_width: int = 3, light_color: QtGui.QColor = QtGui.QColor("lightgray"),):

        super().__init__(pixmap, QtCore.Qt.WindowStaysOnTopHint)
        self._radius = radius
        self._message_offset = message_offset
        self._light_color = light_color
        self._border_width = border_width

        message_font = self.font()
        message_font.setPointSize(message_point_size)
        message_font.setBold(True)
        self.setFont(message_font)

        self._apply_rounded_mask()

    def _apply_rounded_mask(self):
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), self._radius, self._radius)
        region = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_rounded_mask()

    def drawContents(self, painter: QtGui.QPainter):
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        painter.setPen(self._light_color)
        painter.setFont(self.font())
        message_rect = self.rect().adjusted(0, 0, 0, -self._message_offset)
        painter.drawText(message_rect, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom, self.message())

        pen = QtGui.QPen(self._light_color)
        pen.setWidth(self._border_width)
        painter.setPen(pen)
        half_pen = self._border_width / 2
        border_rect = QtCore.QRectF(self.rect()).adjusted(half_pen, half_pen, -half_pen, -half_pen)
        painter.drawRoundedRect(border_rect, self._radius, self._radius)


def create_brewery_splash(message: str = "Brauerei Steuerung wird gestartet...") -> SplashScreen:
    splash_pixmap = QtGui.QPixmap(512, 384)
    splash_pixmap.fill(QtGui.QColor(36, 31, 49))

    brewery_icon = QtGui.QIcon(str(ASSETS_DIR / "icon_brewery.png"))
    logo_pixmap = brewery_icon.pixmap(240, 240)

    painter = QtGui.QPainter(splash_pixmap)
    logo_x = (splash_pixmap.width() - logo_pixmap.width()) // 2
    logo_y = (splash_pixmap.height() - logo_pixmap.height()) // 2 - 25
    painter.drawPixmap(logo_x, logo_y, logo_pixmap)
    painter.end()

    splash = SplashScreen(splash_pixmap)
    splash.showMessage(message, QtCore.Qt.AlignBottom | QtCore.Qt.AlignCenter, splash._light_color)
    return splash
