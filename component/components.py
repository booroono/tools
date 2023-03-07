from PySide2.QtCore import Qt
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QPushButton, QGroupBox, QVBoxLayout, QLabel, QHBoxLayout, QCheckBox, QTextEdit, \
    QSizePolicy


class Button(QPushButton):
    def __init__(self, str, expanding=False):
        super(Button, self).__init__(str)
        if expanding:
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.background_color = '#E1E1E1'

    def set_style_sheet(self):
        self.setStyleSheet(
            f"background-color: {self.background_color};"
            f"font: bold;"
        )

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, color):
        self._background_color = color
        self.set_style_sheet()


class Label(QLabel):
    def __init__(self, txt=''):
        super(Label, self).__init__(txt)
        self.background_color = 'white'
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('font-weight: bold;'
                           f'background-color: {self.background_color};')
        self.color = 'yellow'
        self.fontSize = 100

    def clean(self):
        self.set_background_color()
        self.set_color("white")
        self.clear()

    def set_background_color(self, color="black"):
        self.background_color = color
        self.set_style_sheet()

    def keyPressEvent(self, event):
        pass

    def set_font_size(self, size=None):
        self.fontSize = size or self.fontSize
        self.set_style_sheet()

    def set_color(self, color):
        self.color = color
        self.set_style_sheet()

    def set_style_sheet(self):
        self.setStyleSheet(f'background-color: {self.background_color};'
                           f'font-weight: bold;'
                           f'color: {self.color};'
                           f'font-size: {self.fontSize}px')

    def setText(self, txt: str) -> None:
        super().setText(txt)
        if not txt:
            self.clean()


class GroupLabel(QGroupBox):
    def __init__(self, title=''):
        super(GroupLabel, self).__init__()
        self.label = Label()
        self.setTitle(title)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.set_background_color("black")

    def set_font_size(self, value):
        self.label.set_font_size(value)

    def set_background_color(self, value):
        self.label.set_background_color(value)

    def set_text_color(self, color):
        self.label.set_color(color)

    def setText(self, value):
        self.label.setText(value)

    def clean(self):
        self.label.clean()

    def clear(self):
        self.label.clear()


class CheckButton(QHBoxLayout):
    def __init__(self, process_name):
        super(CheckButton, self).__init__()
        self.addWidget(checkbox := QCheckBox())
        self.addWidget(button := Button(process_name, expanding=True))
        self.setStretchFactor(checkbox, 1)
        self.setStretchFactor(button, 9)

        self.button = button
        self.checkbox = checkbox


class TextEdit(QTextEdit):
    def __init__(self):
        super(TextEdit, self).__init__()

    def add_text_with_color(self, text, color='black'):
        if color == 'red':
            color = QColor(255, 0, 0)
        elif color == 'green':
            color = QColor()
        self.setTextColor(color)


def change_color_selected_button(button_list, button):
    for item in button_list:
        item.background_color = '#E1E1E1'
    button.background_color = 'lightskyblue'
