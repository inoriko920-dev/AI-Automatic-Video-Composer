from __future__ import annotations


def make_primary_button(text: str):
    from PySide6.QtWidgets import QPushButton

    button = QPushButton(text)
    button.setProperty("primary", True)
    return button


def section_title(text: str):
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QLabel

    label = QLabel(text)
    font = QFont()
    font.setPointSize(11)
    font.setBold(True)
    label.setFont(font)
    return label


def muted_label(text: str):
    from PySide6.QtWidgets import QLabel

    label = QLabel(text)
    label.setProperty("muted", True)
    label.setWordWrap(True)
    return label
