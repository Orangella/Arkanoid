import sys
import os

from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, \
    QFileDialog, QAction, QColorDialog, QLabel, QGridLayout, QWidget
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPixmap


class Board(QFrame):

    platform_length = 0
    EMPTY_CUBE = 0
    FULL_CUBE = 1
    init_spots = []
    counts = []
    cubes_color = QColor(0x66CFFC)
    ball_color = QColor(0x006400)

    def __init__(self, parent):
        super().__init__(parent)
        self.speed = 150
        self.parent = parent
        self.timer = QBasicTimer()
        self.is_started = 1
        self.bonus_flag = 0
        self.init_ball_x = 0
        self.init_ball_y = 1
        self.board = []
        self.lives = 3
        self.cycle = 1
        self.gameover = 0
        self.platform_x = 0  # x coord of platform
        self.ball = Ball()
        self.is_paused = True
        self.setFocusPolicy(Qt.StrongFocus)

    def what_at(self, x, y):
        return self.board[(y * Board.BoardWidth) + x]

    def set_cube_at(self, cube, x, y):
        if x != Board.BoardWidth and x >= 0:
            self.board[(y * Board.BoardWidth) + x] = cube

    def platform_move(self):
        px = self.platform_x
        pl = Board.platform_length
        bottom = Board.BoardHeight - 1

        for j in range(px):
            self.set_cube_at(Board.EMPTY_CUBE, j, bottom)
        for j in range(px, px+pl):
            self.set_cube_at(Board.FULL_CUBE, j, bottom)
        for j in range(px+pl, Board.BoardWidth):
            self.set_cube_at(Board.EMPTY_CUBE, j, bottom)

    def get_square_width(self):
        return self.contentsRect().width() // Board.BoardWidth

    def get_square_height(self):
        return self.contentsRect().height() // Board.BoardHeight

    def paintEvent(self, QPaintEvent):
        """Repaint all board except bottom line"""
        painter = QPainter(self)
        rect = self.contentsRect()
        board_top = rect.bottom() - Board.BoardHeight * self.get_square_height()

        for i in range(Board.BoardHeight):
            for j in range(Board.BoardWidth):
                if i == self.ball.cur_y and j == self.ball.cur_x:  # paint ball
                    self.draw_square(painter,
                                     rect.left() + j * self.get_square_width(),
                                     board_top + i * self.get_square_height(),
                                     "ball")
                else:
                    cube = self.what_at(j, i)
                    if cube != Board.EMPTY_CUBE:
                        self.draw_square(painter,
                                         rect.left() + j * self.get_square_width(),
                                         board_top + i * self.get_square_height())

    def keyPressEvent(self, event):
        if not self.is_started:
            super(Board, self).keyPressEvent(event)
            return
        key = event.key()
        if key == Qt.Key_Space:
            self.pause()
            return
        if self.gameover == 1:
            return
        if key == Qt.Key_Left:
            self.try_move(-1)
            return
        elif key == Qt.Key_Right:
            self.try_move(1)
            return

    def try_move(self, new_x):
        x = self.platform_x + new_x
        bottom = Board.BoardHeight - 1

        if x < 0 or (x + Board.platform_length) > Board.BoardWidth:
            return False

        b = self.ball

        # if ball on the line above platform
        if b.cur_y == bottom - 1:
            b_p = self.bounce_platform()
            # move ball if it on the platform
            if b_p:
                if b_p == 1:
                    self.set_cube_at(Board.EMPTY_CUBE, b.cur_x, b.cur_y)
                    b.cur_x += new_x
                    self.set_cube_at(Board.FULL_CUBE, b.cur_x, b.cur_y)
                # change direction
                if new_x == -1 and b.direction == Ball.RD or \
                            new_x == 1 and b.direction == Ball.LD or \
                            b_p == 2 or \
                            b_p == 3:
                    b.reflection()

        # bonus
        if b.cur_y == bottom:
            if (b.cur_x == 0 and self.platform_x == 1 and new_x == -1) or \
                    (b.cur_x == Board.BoardWidth - 1 and
                                 x + Board.platform_length == b.cur_x + 1 and
                                 new_x == 1):
                self.timer.stop()
                self.score += 10000
                self.parent.scores.setText("    " + str(self.current_level + 1) +
                                           " (" + str(self.cycle) + ")\n      " +
                                           str(self.score))

                if self.bonus_flag == 0:
                    self.bonus_flag = 1
                    b.reflection()
                return
            else:
                self.bonus_flag = 0
                self.timer.start(self.speed, self)
        self.platform_x = x
        self.platform_move()
        self.update()
        return True

    def move_ball(self):
        # ball's movement at every tick
        bottom = Board.BoardHeight - 1
        b = self.ball
        x, y = b.get_coords()
        d = b.get_direction()
        nx, ny = b.next_xy()
        # flag if bounce around more then one
        flag_twice = 1

        def set_empty_cube_and_flag(s, pos_x, pos_y):
            nonlocal flag_twice
            flag_twice += 1
            s.set_cube_at(Board.EMPTY_CUBE, pos_x, pos_y)
            s.score += 1

            self.parent.scores.setText("    " + str(self.current_level + 1) +
                                       " (" + str(self.cycle) + ")\n      " +
                                       str(self.score))

            self.current_level_counts -= 1
            if self.current_level_counts == 0:
                raise self.EndOfLvlException()

        def ball_movement(s, pos_x, pos_y):
            nonlocal b
            s.set_cube_at(Board.EMPTY_CUBE, pos_x, pos_y)
            b.set_coords(*b.next_xy())
            s.set_cube_at(Board.FULL_CUBE, *b.get_coords())
            s.update()

        def game_over(s):
            self.lives -= 1
            self.parent.lifes_list[self.lives].setPixmap(QPixmap())
            if self.lives == 0:
                s.timer.stop()
                self.parent.info.setText("Game\nOver")
                self.parent.info.setStyleSheet("background-color: red;")
                self.gameover = 1
            else:
                s.set_cube_at(Board.EMPTY_CUBE, nx, ny)
                s.set_cube_at(Board.EMPTY_CUBE, x, y)
                self.ball.set_coords(self.init_ball_x, self.init_ball_y)
                self.ball.set_direction(Ball.RU)
                self.set_cube_at(Board.FULL_CUBE, *self.ball.get_coords())

        if y == bottom and (d == Ball.RD or d == Ball.LD):
            game_over(self)
            return

        if (nx == Board.BoardWidth or nx == -1) and ny == -1:  # upper corners
            b.reflection()
        elif ny == -1:
            b.rebound_top()
        elif nx == Board.BoardWidth:
            b.rebound_right()
        elif nx == -1:
            b.rebound_left()

        elif ny == bottom:
            b_p = self.bounce_platform()
            if b_p == 2 or b_p == 3:
                b.reflection()
            elif b_p == 1:
                b.rebound_bottom()
            else:
                ball_movement(self, x, y)
                if nx == Board.BoardWidth - 1 or nx == 0:
                    pass
                else:
                    game_over(self)
                return
        else:
            flag_twice = 0

        # if ball not bounce at border
        if flag_twice == 0:
            if self.what_at(nx, ny) == Board.FULL_CUBE:
                b.reflection()
                set_empty_cube_and_flag(self, nx, ny)

        if y != bottom-1 and self.what_at(x, y+1) == Board.FULL_CUBE:
            b.rebound_bottom()
            set_empty_cube_and_flag(self, x, y + 1)

        if ny != -1 and self.what_at(x, y-1) == Board.FULL_CUBE:
            b.rebound_top()
            set_empty_cube_and_flag(self, x, y - 1)

        if nx != Board.BoardWidth and self.what_at(x+1, y) == Board.FULL_CUBE:
            b.rebound_right()
            set_empty_cube_and_flag(self, x + 1, y)

        if nx != -1 and self.what_at(x-1, y) == Board.FULL_CUBE:
            b.rebound_left()
            set_empty_cube_and_flag(self, x - 1, y)

        if flag_twice > 1:
            b.set_direction(d)
            b.reflection()

        # if next x y after changing directory is full cube or border
        nx, ny = b.next_xy()
        if self.what_at(nx, ny) == Board.FULL_CUBE \
                or nx == Board.BoardWidth or nx == -1 \
                or ny == -1 or ny == bottom:
            self.update()
            return

        ball_movement(self, x, y)


    class EndOfLvlException(Exception):
        pass

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            try:
                self.move_ball()
            except self.EndOfLvlException:  # game over
                self.current_level += 1
                self.parent.scores.setText("    " + str(self.current_level + 1) + " (" +
                                           str(self.cycle) + ")\n      "
                                           + str(self.score))
                self.new_lvl()
        else:
            super(Board, self).timerEvent(event)

    def new_game(self):
        Board.init_spots = []
        self.score = 0
        self.current_level = 0
        self.lives = 3
        self.cycle = 1
        self.gameover = 0

        file_name = QFileDialog.getOpenFileName(self, 'Open file')[0]
        with open(file_name, 'r') as f:
            Board.BoardWidth = int(f.readline())
            Board.BoardHeight = int(f.readline()) + 5
            Board.lvl = int(f.readline())

            self.platform_x = Board.BoardWidth // 3
            Board.platform_length = Board.BoardWidth // 3
            self.init_ball_x = self.platform_x + self.platform_length // 2
            # set iniyY = first line above platform
            self.init_ball_y = Board.BoardHeight - 2

            for i in range(Board.lvl):
                Board.init_spots.append([])
                Board.counts.append(0)

            for _ in f:
                if _ != '$$$\n':
                    Board.init_spots[self.current_level].append(((int(_.split('.')[0])), (int(_.split('.')[1]))))
                    # number of counts of lvl
                    Board.counts[self.current_level] += 1
                elif self.current_level < Board.lvl - 1:
                    self.current_level += 1

        self.current_level = 0
        self.setFixedHeight(Board.BoardHeight * 15)
        self.setFixedWidth(Board.BoardWidth * 15)
        self.new_lvl()

    def new_lvl(self):
        self.current_level_counts = 0
        self.board = []
        for i in range(Board.BoardHeight * Board.BoardWidth):
            self.board.append(Board.EMPTY_CUBE)
        self.platform_move()
        self.ball.set_coords(self.init_ball_x, self.init_ball_y)
        self.ball.set_direction(Ball.RU)

        # next iteration of game
        if self.current_level == Board.lvl:
            self.current_level = 0
            self.cycle += 1
            self.parent.scores.setText("    " + str(self.current_level + 1) +
                                       " (" + str(self.cycle) + ")\n      " +
                                       str(self.score))
            self.speed //= 2

        for x, y in Board.init_spots[self.current_level]:
            self.set_cube_at(Board.FULL_CUBE, x, y)

        self.current_level_counts = Board.counts[self.current_level]
        self.set_cube_at(Board.FULL_CUBE, *self.ball.get_coords())
        self.timer.start(self.speed, self)
        self.parent.scores.setText("    " + str(self.current_level + 1) +
                                   " (" + str(self.cycle) + ")\n      " +
                                   str(self.score))

    def pause(self):
        if self.gameover == 1:
            return
        self.is_paused = not self.is_paused
        if not self.is_paused:
            self.timer.stop()
            self.parent.pause.setText("Paused")
            self.parent.pause.setStyleSheet("background-color: yellow;")
        else:
            self.timer.start(self.speed, self)
            self.parent.pause.setText("")
            self.parent.pause.setStyleSheet("")
        self.update()

    def draw_square(self, painter, x, y, obj="cube"):
        if obj != "ball":
            color = Board.cubes_color
        else:
            color = Board.ball_color
        painter.fillRect(x + 1, y + 1, self.get_square_width() - 2,
                         self.get_square_height() - 2, color)
        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.get_square_height() - 1, x, y)
        painter.drawLine(x, y, x + self.get_square_width() - 1, y)
        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.get_square_height() - 1,
                         x + self.get_square_width() - 1, y +
                         self.get_square_height() - 1)
        painter.drawLine(x + self.get_square_width() - 1,
                         y + self.get_square_height() - 1, x +
                         self.get_square_width() - 1, y + 1)

    def bounce_platform(self):
        """
        Return if ball bounce platform at the next tick

        Return options:
        0: not bounce platform
        1: bounce platform
        2: bounce left corner
        3: bounce right corner

        """
        b = self.ball
        if b.cur_x in range(self.platform_x, self.platform_x +
                self.platform_length):  # ball on platform
            return 1
        elif b.cur_x == self.platform_x - 1 and b.direction == Ball.RD:
            # left corner
            return 2
        elif b.cur_x == self.platform_x + self.platform_length and \
                        b.direction == Ball.LD:  # right corner
            return 3
        return 0


class Ball():

    RU = 0  # Right Up
    RD = 1
    LU = 2
    LD = 3

    def __init__(self):
        self.cur_x = 0
        self.cur_y = 0
        self.direction = 0

    def get_coords(self):
        return [self.cur_x, self.cur_y]

    def set_coords(self, x, y):
        self.cur_x = x
        self.cur_y = y

    def get_direction(self):
        return self.direction

    def set_direction(self, a):
        self.direction = a

    def next_xy(self):
        d = self.direction
        if d == Ball.RU:
            return [self.cur_x + 1, self.cur_y - 1]
        elif d == Ball.RD:
            return [self.cur_x + 1, self.cur_y + 1]
        elif d == Ball.LU:
            return [self.cur_x - 1, self.cur_y - 1]
        elif d == Ball.LD:
            return [self.cur_x - 1, self.cur_y + 1]

    def rebound_top(self):
        if self.direction == Ball.RU:
            self.direction = Ball.RD
        else:
            self.direction = Ball.LD

    def rebound_bottom(self):
        if self.direction == Ball.RD:
            self.direction = Ball.RU
        else:
            self.direction = Ball.LU

    def rebound_right(self):
        if self.direction == Ball.RU:
            self.direction = Ball.LU
        else:
            self.direction = Ball.LD

    def rebound_left(self):
        if self.direction == Ball.LU:
            self.direction = Ball.RU
        else:
            self.direction = Ball.RD

    def reflection(self):
        d = self.direction
        if d == Ball.RD:
            self.direction = Ball.LU
        elif d == Ball.RU:
            self.direction = Ball.LD
        elif d == Ball.LU:
            self.direction = Ball.RD
        elif d == Ball.LD:
            self.direction = Ball.RU


class Arkanoid(QMainWindow):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):

        def create_action(name, function, shortcut=''):
            qaction = QAction(name, self)
            qaction.setShortcut(shortcut)
            qaction.triggered.connect(function)
            return qaction

        self.board = None
        self.setMaximumSize(200, 50)

        col_cube = create_action('Cubes', self.color_cube)
        col_ball = create_action('Ball', self.color_ball)

        speed1 = create_action('Easy', self.speed1_a)
        speed2 = create_action('Normal', self.speed2_a)
        speed3 = create_action('Hard', self.speed3_a)

        new_g = create_action('New Game', self.new_game)

        menubar = self.menuBar()
        menubar.addAction(new_g)
        speed_menu = menubar.addMenu('&Speed')

        speed_menu.addAction(speed1)
        speed_menu.addAction(speed2)
        speed_menu.addAction(speed3)

        col_menu = menubar.addMenu('&Color')

        col_menu.addAction(col_cube)
        col_menu.addAction(col_ball)

        self.center()
        self.setWindowTitle('Arkanoid')
        self.setFocus()
        self.show()

    def pause_game(self):
        if self.board:
            self.board.pause()

    def color_cube(self):
        self.pause_game()
        col = QColorDialog.getColor()
        if col.isValid():
            Board.cubes_color = col

    def color_ball(self):
        self.pause_game()
        col = QColorDialog.getColor()
        if col.isValid():
            Board.ball_color = col

    def speed1_a(self):
        self.board.speed = 400
        self.board.timer.start(self.board.speed, self.board)

    def speed2_a(self):
        self.board.speed = 150
        self.board.timer.start(self.board.speed, self.board)

    def speed3_a(self):
        self.board.speed = 50
        self.board.timer.start(self.board.speed, self.board)

    def new_game(self):
        self.pause_game()

        pic_life = QPixmap(os.path.join(os.getcwd(), 'pics', 'life.png'))

        self.life = QLabel()
        pixmap = pic_life
        self.life.setPixmap(pixmap)

        self.life1 = QLabel()
        pixmap1 = pic_life
        self.life1.setPixmap(pixmap1)

        self.life2 = QLabel()
        pixmap2 = pic_life
        self.life2.setPixmap(pixmap2)

        self.lifes_list = [self.life, self.life1, self.life2]

        grid = QGridLayout()
        grid.setSpacing(5)
        grid.addWidget(self.life, 1, 0)
        grid.addWidget(self.life1, 1, 1)
        grid.addWidget(self.life2, 1, 2)

        self.pause = QLabel()
        self.pause.setStyleSheet("")
        grid.addWidget(self.pause, 1, 3, 1, 4)

        self.info = QLabel()
        self.info.setText("Level:\nScore:")
        self.info.setStyleSheet("")

        grid.addWidget(self.info, 1, 5, 1, 7)

        self.scores = QLabel()
        grid.addWidget(self.scores, 1, 8)
        self.board = Board(self)
        self.board.new_game()

        grid.addWidget(self.board, 2, 0, 2, 9)
        self.board.setStyleSheet("margin-bottom: 0; padding-top: -4px; padding-right: -4px;"
                                 "background-color: #f2f5f9;")
        self.setCentralWidget(QWidget())
        m = QWidget()
        m.setLayout(grid)

        self.setCentralWidget(m)

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/4,
                  (screen.height()-size.height() - self.height())/4)

if __name__ == '__main__':
    app = QApplication([])
    arkanoid = Arkanoid()
    sys.exit(app.exec_())