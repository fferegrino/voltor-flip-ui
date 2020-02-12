import logging
from pathlib import Path

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from voltorb_flip.game import GameState, UnableToFlipException, VoltorbFlip

RESOURCES = Path(__file__).parent / "resources"


class GameWidget(QWidget):  # pylint: disable=too-many-instance-attributes

    BOARD_LABEL_MARGIN = 3

    # pylint: disable=line-too-long
    INSTRUCTIONS = (
        "There are twenty-five green squares, and these squares each contain either a Voltorb"
        "(equivalent to zero) or the numbers 1, 2 or 3. When you tap a square, you will flip it over to see what it contains.\n\n"
        "At any point in the game, your score is equal to all the numbers you've flipped over multiplied together."
        "This inevitably means that once you flip over a zero, you've lost all your points and can never get them back. "
        "(after all, there's no point in continuing when your score has a multiplier of zero in it). "
        "The goal of the game is to flip over all the 2s and 3s on the table, and once you've done that you'll get your payout and advance to the next level."
    )

    def __init__(self, app_context):
        self.app_context = app_context
        self.logger = logging.getLogger(__name__)
        self.app = QApplication([])
        self._game = VoltorbFlip()
        self.buttons = None
        self.vertical_labels = []
        self.vertical_bombs = []
        self.horizontal_labels = []
        self.horizontal_bombs = []
        super().__init__()

        self.setObjectName("mainWindow")
        with open(self.app_context.get_resource("classic.css")) as readable:
            images_folder  = self.app_context.get_resource("images")
            self.setStyleSheet(readable.read().replace("${images_folder}", images_folder))
        QtGui.QFontDatabase.addApplicationFont(self.app_context.get_resource("VCR_OSD_MONO_1.001.ttf"))

        self.logger.info("new game started")

        main_layout = QHBoxLayout()
        board = self._create_board()
        main_layout.addWidget(board)
        main_layout.addWidget(self._create_hud())
        self.setLayout(main_layout)
        self.reset_game()

    def reset_game(self):
        self._reset_buttons()
        self._reset_board_labels()
        self._update_score()
        self._update_level()

    def _update_score(self):
        self.current.setText(f"Score {self._game.current_score:06d}")
        self.accumulated.setText(f"Total {self._game.accumulated_score:06d}")

    def _update_level(self):
        self.level.setText(f"lvl {self._game.level}")

    def _reset_buttons(self):
        for row_values, row_buttons in zip(self._game.board, self.buttons):
            for value, button in zip(row_values, row_buttons):
                button.setProperty("value", str(value))
                button.setProperty("state", "hidden")
                self.style().polish(button)

    # pylint: disable=bad-continuation
    def _reset_board_labels(self):
        for value, bombs, value_label, bomb_label in zip(
            self._game.horizontal_points,
            self._game.horizontal_bombs,
            self.horizontal_labels,
            self.horizontal_bombs,
        ):
            value_label.setText(str(value))
            bomb_label.setText(str(bombs))

        for value, bombs, value_label, bomb_label in zip(
            self._game.vertical_points,
            self._game.vertical_bombs,
            self.vertical_labels,
            self.vertical_bombs,
        ):
            value_label.setText(str(value))
            bomb_label.setText(str(bombs))

    def _create_board(self,):
        board_widget = QWidget(objectName="board")
        parent = QGridLayout()

        help_button = QPushButton()
        help_button.setProperty("value", "help")
        help_button.setCursor(QtCore.Qt.WhatsThisCursor)
        help_button.clicked.connect(self.__show_help)
        parent.addWidget(help_button, 5, 5)

        self.buttons = self._create_button_board(parent)

        for i in range(5):
            vertical_widget = QWidget()
            vertical_widget.setProperty("function", "label")
            vertical_layout = QVBoxLayout()
            vertical_layout.setContentsMargins(
                GameWidget.BOARD_LABEL_MARGIN,
                GameWidget.BOARD_LABEL_MARGIN,
                GameWidget.BOARD_LABEL_MARGIN,
                GameWidget.BOARD_LABEL_MARGIN,
            )
            vertical_layout.setSpacing(0)
            points_vertical = QLabel()
            points_vertical.setAlignment(QtCore.Qt.AlignCenter)
            bombs_vertical = QLabel()
            bombs_vertical.setAlignment(QtCore.Qt.AlignCenter)
            points_vertical.setProperty("label_to", "points")
            bombs_vertical.setProperty("label_to", "bombs")

            vertical_layout.addWidget(points_vertical)
            vertical_layout.addWidget(bombs_vertical)

            vertical_widget.setLayout(vertical_layout)
            parent.addWidget(vertical_widget, 5, i)

            horizontal_widget = QWidget()
            horizontal_widget.setProperty("function", "label")
            horizontal_layout = QVBoxLayout()
            horizontal_layout.setContentsMargins(
                GameWidget.BOARD_LABEL_MARGIN,
                GameWidget.BOARD_LABEL_MARGIN,
                GameWidget.BOARD_LABEL_MARGIN,
                GameWidget.BOARD_LABEL_MARGIN,
            )
            horizontal_layout.setSpacing(0)

            points_horizontal = QLabel()
            points_horizontal.setAlignment(QtCore.Qt.AlignCenter)
            bombs_horizontal = QLabel()
            bombs_horizontal.setAlignment(QtCore.Qt.AlignCenter)
            points_horizontal.setProperty("label_to", "points")
            bombs_horizontal.setProperty("label_to", "bombs")

            horizontal_layout.addWidget(points_horizontal)
            horizontal_layout.addWidget(bombs_horizontal)
            horizontal_widget.setLayout(horizontal_layout)
            parent.addWidget(horizontal_widget, i, 5)

            self.vertical_bombs.append(bombs_vertical)
            self.vertical_labels.append(points_vertical)
            self.horizontal_bombs.append(bombs_horizontal)
            self.horizontal_labels.append(points_horizontal)

        board_widget.setLayout(parent)
        return board_widget

    def _create_button_board(self, parent):
        buttons = []
        for i in range(5):
            row = []
            for j in range(5):
                button = QPushButton()
                button.setProperty("i", i)
                button.setProperty("j", j)
                button.clicked.connect(self.__card_clicked)
                button.setCursor(QtCore.Qt.PointingHandCursor)
                parent.addWidget(button, i, j)
                row.append(button)
            buttons.append(row)
        return buttons

    def _create_button_set(self):
        buttons = QWidget()
        button_layout = QHBoxLayout()
        restart_button = QPushButton("Restart game")
        restart_button.clicked.connect(self.__reset_game_clicked)
        button_layout.addWidget(restart_button)
        buttons.setLayout(button_layout)
        return buttons

    def _create_hud(self):
        hud = QWidget()
        hud.setObjectName("hud")
        layout = QVBoxLayout()
        self.accumulated = QLabel()
        self.accumulated.setAlignment(QtCore.Qt.AlignCenter)
        self.level = QLabel()
        self.level.setAlignment(QtCore.Qt.AlignCenter)
        self.current = QLabel()
        self.current.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.level)
        layout.addWidget(self.accumulated)
        layout.addWidget(self.current)
        layout.addWidget(self._create_button_set())
        hud.setLayout(layout)
        return hud

    def game_over(self):
        if self._game.state == GameState.WON:
            self.logger.info("game won")
            QMessageBox.about(self, "Great", "You won! moving on to the next level")
            self._game.bump_level()
        elif self._game.state == GameState.LOST:
            self.logger.info("game lost")
            QMessageBox.critical(
                self,
                "Game over",
                "You lost the game, we are taking you to the previous level",
                QMessageBox.Yes,
            )
            self._game.remove_level()

        self.reset_game()

    def __show_help(self):
        QMessageBox.about(self, "Help", GameWidget.INSTRUCTIONS)

    def __reset_game_clicked(self):
        self._game.reset_level()
        self.reset_game()

    def __card_clicked(self):
        button = self.sender()
        i, j = button.property("i"), button.property("j")
        self.logger.info(f"will flip ({i}, {j})")
        try:
            button.setProperty("state", "visible")
            self.style().polish(button)
            self._game.flip(i, j)
        except UnableToFlipException:
            self.logger.error("cell already flipped")

        if self._game.state != GameState.IN_PROGRESS:
            self.game_over()

        self._update_score()

    def run(self):
        self.show()
        return self.app_context.app.exec_()
