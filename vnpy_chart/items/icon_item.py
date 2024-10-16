import os
from enum import Enum

import pyqtgraph as pg
from vnpy.trader.ui import QtCore, QtGui
from vnpy.trader.object import BarData

from ..base import BAR_WIDTH
from ..manager import BarManager
from .chart_item import ChartItem


ASSETS_FOLER = os.path.join(os.path.dirname(__file__), '../assets/')


class IconEnum(Enum):
    """
    枚举值为在assets下的文件名
    """
    SMILEY_FACE = 'smiley_face.png'


class IconItem(ChartItem):
    def __init__(self, manager: BarManager) -> None:
        super().__init__(manager)

        self._pixmaps = {}

    def boundingRect(self) -> QtCore.QRectF:
        min_price, max_price = self._manager.get_price_range()
        rect: QtCore.QRectF = QtCore.QRectF(
            0,
            min_price,
            len(self._bar_pictures),
            max_price - min_price
        )
        return rect

    def get_y_range(self, min_ix: int = None, max_ix: int = None) -> tuple[float, float]:
        min_price, max_price = self._manager.get_price_range(min_ix, max_ix)
        return min_price, max_price

    def get_info_text(self, ix: int) -> str:
        return ''

    def _draw_bar_picture(self, ix: int, bar: BarData) -> QtGui.QPicture:
        picture: QtGui.QPicture = QtGui.QPicture()
        painter: QtGui.QPainter = QtGui.QPainter(picture)

        icons: list[tuple[IconEnum, float]] = (
            bar.extra or {}).get('icons') or []
        if len(icons) > 0:
            for icon, y in icons:
                pixmap = self.get_pixmap(icon)
                ratio = self.getAspectRatio()
                client_ratio = self.getClientAspectRatio()
                w = 1
                h = w / ratio * client_ratio
                rect: QtCore.QRectF = QtCore.QRectF(
                    ix - w/2,
                    y,
                    w,
                    h,
                )
                painter.drawPixmap(rect, pixmap, pixmap.rect())

        painter.end()
        return picture

    def y_range_changed(self):
        self._to_repaint = True

    def get_pixmap(self, icon: IconEnum) -> QtGui.QPixmap:
        if not icon.value in self._pixmaps:
            pixmap = QtGui.QPixmap(os.path.join(ASSETS_FOLER, icon.value))

            # 因为Y坐标系是越大越在上，所以要翻转图片
            transform = QtGui.QTransform()
            transform.scale(1, -1)
            transform.translate(0, -pixmap.height())
            pixmap = pixmap.transformed(transform)

            self._pixmaps[icon.value] = pixmap
        return self._pixmaps[icon.value]

    def getClientAspectRatio(self) -> float:
        parent = self.parentItem()
        while parent is not None:
            if isinstance(parent, pg.ViewBox):
                return parent.width() / parent.height()
            parent = parent.parentItem()
        raise Exception('IconItem is not in any ViewBox')

    def getAspectRatio(self) -> float:
        view_rect = self.viewRect()
        return view_rect.width() / view_rect.height()