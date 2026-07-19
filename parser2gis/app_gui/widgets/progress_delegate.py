from __future__ import annotations

from typing import Any

from PySide6.QtCore import QModelIndex, QRect, Qt, QSize
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem


class ProgressDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option: QStyleOptionViewItem,
              index: QModelIndex) -> None:
        value = index.data(Qt.ItemDataRole.DisplayRole)
        if value is None:
            super().paint(painter, option, index)
            return

        try:
            pct = int(value)
        except (ValueError, TypeError):
            super().paint(painter, option, index)
            return

        painter.save()
        rect = option.rect
        bar_rect = QRect(rect.x() + 2, rect.y() + 2, rect.width() - 4, rect.height() - 4)
        painter.setPen(QPen(QColor("#4472C4"), 1))
        painter.setBrush(QColor("#E8F0FE"))
        painter.drawRect(bar_rect)

        if pct > 0:
            fill_width = int(bar_rect.width() * pct / 100)
            fill_rect = QRect(bar_rect.x(), bar_rect.y(), fill_width, bar_rect.height())
            painter.setBrush(QColor("#4472C4"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(fill_rect)

        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(bar_rect, Qt.AlignmentFlag.AlignCenter, f"{pct}%")
        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        return QSize(100, 24)