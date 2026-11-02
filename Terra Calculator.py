import sys

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QGridLayout, QVBoxLayout, QGraphicsDropShadowEffect
)

from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve
)

from PySide6.QtGui import (
    QPainter, QColor, QLinearGradient, QPen, QFont
)


# =====================================
# GLASS BUTTON
# =====================================

class GlassButton(QPushButton):

    def __init__(self, text, kind="number"):
        super().__init__(text)

        self.kind = kind
        self.setFixedSize(78, 78)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(100, 110, 130, 45))

        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):

        painter = QPainter(self)

        try:
            painter.setRenderHint(
                QPainter.RenderHint.Antialiasing
            )

            rect = self.rect().adjusted(3, 3, -3, -3)

            gradient = QLinearGradient(
                0, 0, 0, self.height()
            )

            if self.kind == "operator":
                gradient.setColorAt(
                    0, QColor(235, 245, 255, 245)
                )
                gradient.setColorAt(
                    1, QColor(190, 215, 245, 175)
                )

            elif self.kind == "equal":
                gradient.setColorAt(
                    0, QColor(255, 255, 255, 250)
                )
                gradient.setColorAt(
                    1, QColor(210, 220, 238, 210)
                )

            elif self.kind == "utility":
                gradient.setColorAt(
                    0, QColor(255, 255, 255, 240)
                )
                gradient.setColorAt(
                    1, QColor(220, 225, 235, 190)
                )

            else:
                gradient.setColorAt(
                    0, QColor(255, 255, 255, 245)
                )
                gradient.setColorAt(
                    1, QColor(235, 238, 245, 185)
                )

            painter.setBrush(gradient)

            painter.setPen(
                QPen(QColor(255, 255, 255, 230), 1.5)
            )

            painter.drawRoundedRect(rect, 25, 25)

            # Glass reflection
            painter.setPen(
                QPen(QColor(255, 255, 255, 180), 1)
            )

            painter.drawLine(
                20, 9, self.width() - 20, 9
            )

            # Button text
            painter.setPen(QColor(35, 39, 48))

            font = QFont("Arial", 23)
            font.setWeight(QFont.Weight.Medium)

            painter.setFont(font)

            painter.drawText(
                rect,
                Qt.AlignmentFlag.AlignCenter,
                self.text()
            )

        finally:
            painter.end()


# =====================================
# TERRA CALCULATOR
# =====================================

class TerraCalculator(QWidget):

    def __init__(self):
        super().__init__()

        self.current = "0"
        self.first_number = None
        self.operator = None
        self.reset_display = False
        self.animations = []

        self.setup_ui()

    # =================================
    # USER INTERFACE
    # =================================

    def setup_ui(self):

        self.setWindowTitle("Terra Calculator")
        self.setFixedSize(410, 670)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.setStyleSheet("""
            QWidget {
                background-color: #F3F4F7;
                color: #202124;
                font-family: Arial;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 25, 24, 25)
        main_layout.setSpacing(15)

        # Branding

        self.title = QLabel("terra")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title.setStyleSheet("""
            QLabel {
                color: #252832;
                font-size: 29px;
                font-weight: 600;
                letter-spacing: 4px;
                background: transparent;
                padding: 12px;
            }
        """)

        main_layout.addWidget(self.title)

        # Display

        self.display = QLabel("0")
        self.display.setAlignment(
            Qt.AlignmentFlag.AlignRight |
            Qt.AlignmentFlag.AlignVCenter
        )

        self.display.setMinimumHeight(115)

        self.display.setStyleSheet("""
            QLabel {
                background-color: rgba(255,255,255,90);
                color: #202124;
                font-size: 48px;
                font-weight: 300;
                padding: 20px;
                border: 1px solid rgba(255,255,255,180);
                border-radius: 22px;
            }
        """)

        main_layout.addWidget(self.display)

        # Keypad

        grid = QGridLayout()
        grid.setSpacing(12)

        buttons = [
            ("AC", 0, 0, "utility"),
            ("⌫", 0, 1, "utility"),
            ("±", 0, 2, "utility"),
            ("÷", 0, 3, "operator"),

            ("7", 1, 0, "number"),
            ("8", 1, 1, "number"),
            ("9", 1, 2, "number"),
            ("×", 1, 3, "operator"),

            ("4", 2, 0, "number"),
            ("5", 2, 1, "number"),
            ("6", 2, 2, "number"),
            ("−", 2, 3, "operator"),

            ("1", 3, 0, "number"),
            ("2", 3, 1, "number"),
            ("3", 3, 2, "number"),
            ("+", 3, 3, "operator"),

            ("0", 4, 0, "number"),
            (".", 4, 2, "number"),
            ("=", 4, 3, "equal"),
        ]

        for text, row, col, kind in buttons:

            button = GlassButton(text, kind)

            if text == "0":
                button.setFixedWidth(168)
                grid.addWidget(button, row, col, 1, 2)
            else:
                grid.addWidget(button, row, col)

            button.clicked.connect(
                lambda checked=False, value=text:
                self.button_clicked(value)
            )

            button.pressed.connect(
                lambda b=button:
                self.animate_button(b)
            )

        main_layout.addLayout(grid)
        main_layout.addStretch()

    # =================================
    # KEYBOARD CONTROLS
    # =================================

    def keyPressEvent(self, event):

        key = event.key()
        text = event.text()

        # Numbers
        if text in "0123456789" and text:
            self.button_clicked(text)

        # Decimal
        elif key == Qt.Key.Key_Period or text == ",":
            self.button_clicked(".")

        # Addition
        elif key in (
            Qt.Key.Key_Plus,
            Qt.Key.Key_Equal
        ) and text == "+":
            self.button_clicked("+")

        # Subtraction
        elif key == Qt.Key.Key_Minus:
            self.button_clicked("−")

        # Multiplication
        elif key in (
            Qt.Key.Key_Asterisk,
            Qt.Key.Key_X
        ):
            self.button_clicked("×")

        # Division
        elif key == Qt.Key.Key_Slash:
            self.button_clicked("÷")

        # Equals
        elif key in (
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter
        ):
            self.button_clicked("=")

        # Equals using the keyboard
        elif key == Qt.Key.Key_Equal:
            self.button_clicked("=")

        # Backspace
        elif key == Qt.Key.Key_Backspace:
            self.button_clicked("⌫")

        # Clear
        elif key == Qt.Key.Key_Escape:
            self.button_clicked("AC")

        # Sign change
        elif key == Qt.Key.Key_N:
            self.button_clicked("±")

        else:
            super().keyPressEvent(event)

    # =================================
    # BUTTON ANIMATION
    # =================================

    def animate_button(self, button):

        animation = QPropertyAnimation(
            button, b"geometry", self
        )

        animation.setDuration(130)
        animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

        original = button.geometry()

        animation.setStartValue(original)

        animation.setKeyValueAt(
            0.5,
            original.adjusted(3, 3, -3, -3)
        )

        animation.setEndValue(original)

        self.animations.append(animation)

        animation.finished.connect(
            lambda a=animation:
            self.animations.remove(a)
            if a in self.animations else None
        )

        animation.start()

    # =================================
    # CALCULATOR LOGIC
    # =================================

    def button_clicked(self, value):

        if value.isdigit():

            if self.current == "0" or self.reset_display:
                self.current = value
                self.reset_display = False
            else:
                self.current += value

        elif value == ".":

            if self.reset_display:
                self.current = "0"
                self.reset_display = False

            if "." not in self.current:
                self.current += "."

        elif value == "AC":

            self.current = "0"
            self.first_number = None
            self.operator = None
            self.reset_display = False

        elif value == "⌫":

            if not self.reset_display and len(self.current) > 1:
                self.current = self.current[:-1]
            else:
                self.current = "0"

        elif value == "±":

            if self.current != "0":
                self.current = str(-float(self.current))

        elif value in ["+", "−", "×", "÷"]:

            self.first_number = float(self.current)
            self.operator = value
            self.reset_display = True

        elif value == "=":

            if self.operator is not None:

                second_number = float(self.current)

                if self.operator == "+":
                    result = (
                        self.first_number + second_number
                    )

                elif self.operator == "−":
                    result = (
                        self.first_number - second_number
                    )

                elif self.operator == "×":
                    result = (
                        self.first_number * second_number
                    )

                elif self.operator == "÷":

                    if second_number == 0:
                        self.current = "Cannot divide by zero"
                        self.operator = None
                        self.display.setText(self.current)
                        return

                    result = (
                        self.first_number / second_number
                    )

                if result == int(result):
                    self.current = str(int(result))
                else:
                    self.current = str(round(result, 8))

                self.operator = None
                self.reset_display = True

        self.display.setText(self.current)


# =====================================
# START APPLICATION
# =====================================

app = QApplication(sys.argv)

window = TerraCalculator()
window.show()

sys.exit(app.exec())