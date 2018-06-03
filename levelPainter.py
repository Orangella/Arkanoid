import sys, random, os
from mimetypes import init
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QAction, QLabel, QSpinBox, QSizePolicy, \
    QPushButton, QFileDialog, QColorDialog
from PyQt5.QtGui import QPainter, QColor, QIcon, QFont
from PyQt5.QtCore import Qt


# tools
POINT, BRUSH, RECTANGLE = [0, 1, 2]
# modes
EMPTY, FULL, INVERT = [0, 1, 2]


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.painter = Painter()
        self.filename = ''

        # active 0 state, disable 0 state etc
        self.button_state_list = {'a0':0, 'd0':1, 'a1':2, 'd1':3, 'a2':4, 'd2':5}

        #state of each button tool
        self.button_state = ['d2', 'd2', 'a2']
        self.prev_button_state = [None, None, None]

        self.icons = []
        for i in range(3):
            self.icons.append([])
        for n, item in [[0, 'point'], [1, 'brush'], [2, 'rect']]:
            for i in range(3):
                for j in range(2):
                    self.icons[n].append(
                        QIcon(os.path.join(os.getcwd(),
                        'pics', item + str(i) + str(j) + '.png')))

        def create_toolbar_action(name, function):
            qaction = QAction('&' + name, self)
            qaction.triggered.connect(function)
            self.toolbar = self.addToolBar(name)
            self.toolbar.addAction(qaction)
            return qaction

        self.point_action = create_toolbar_action('Point', self.point_action)
        self.brush_action = create_toolbar_action('Brush', self.brush_action)
        self.rect_action = create_toolbar_action('Rectangle', self.rect_action)

        # spacer widget for left
        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(left_spacer)

        def level_change():
            self.painter.current_level = self.number_of_level.value() - 1
            self.painter.change_level()

        self.number_of_level = QSpinBox()
        self.number_of_level.setMinimum(1)
        self.number_of_level.setMaximum(self.painter.levels)
        self.number_of_level.valueChanged.connect(level_change)
        self.toolbar.addWidget(self.number_of_level)

        self.change_buttons_image()

        menubar = self.menuBar()

        def create_action(name, function, shortcut=''):
            qaction = QAction(name, self)
            qaction.setShortcut(shortcut)
            qaction.triggered.connect(function)
            return qaction

        new = create_action('New', self.new_action, 'Ctrl+N')
        load = create_action('Load', self.load_action, 'Ctrl+L')
        save = create_action('Save', self.save_action, 'Ctrl+S')
        save_as = create_action('Save As', self.save_as_action)

        file_menu = menubar.addMenu('&File')
        file_menu.addAction(new)
        file_menu.addAction(load)
        file_menu.addAction(save)
        file_menu.addAction(save_as)

        col_cube = create_action('Cells', self.color_cube)

        col_menu = menubar.addMenu('&Color')
        col_menu.addAction(col_cube)

        self.setGeometry(300, 300, 200, 230)
        self.setWindowTitle('Level Painter')
        self.show()

    def new_action(self):
        class NewForm(QWidget):
            def __init__(self):
                super().__init__()

                def create_label(x, y, text):
                    label = QLabel(self)
                    label.move(x, y)
                    label.setText(text)
                    label.setFont(QFont('', 10, QFont.Bold))
                    return label

                def create_spin_box(x, y, minim, maxim):
                    sb = QSpinBox(self)
                    sb.move(x, y)
                    sb.setMinimum(minim)
                    sb.setMaximum(maxim)
                    return sb

                def btn_click():
                    main_window.painter.initUI(
                        self.sbx.value(),
                        self.sby.value(),
                        self.sbn.value()
                    )
                    main_window.number_of_level.setMaximum(
                        main_window.painter.levels)
                    main_window.setCentralWidget(main_window.painter)
                    main_window.filename = ''
                    self.close()

                self.label_size = create_label(95, 10, 'Size')
                self.sbx = create_spin_box(65, 35, 10, 50)
                self.label_x = create_label(108, 38, 'x')
                self.sby = create_spin_box(120, 35, 10, 50)
                self.labelcx = create_label(77, 58, 'X')
                self.labelcy = create_label(132, 58, 'Y')
                self.label_num = create_label(10, 83,
                                              'Number of levels (1-15):')
                self.sbn = create_spin_box(179, 81, 1, 15)
                self.btn = QPushButton('OK', self)
                self.btn.clicked.connect(btn_click)
                self.btn.move(70, 110)
                self.setGeometry(340, 340, 230, 140)
                self.setWindowTitle('New Levels Settings')
                self.setFocus()

        self.new_form = NewForm()
        self.new_form.show()

    def load_action(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file')[0]
        if fname:
            self.filename = fname
        else:
            return

        with open(self.filename, 'r') as f:
            w = int(f.readline())
            h = int(f.readline())
            lvl = int(f.readline())
            p = self.painter
            p.initUI(w, h, lvl)

            p.current_level = 0
            for _ in f:
                if _ != '$$$\n':
                    p.set_cube_at(Painter.FULL_CUBE,
                                  int(_.split('.')[0]), int(_.split('.')[1]))
                elif p.current_level < p.levels - 1:
                    p.current_level += 1
                    p.change_level()
        p.current_level = 0
        p.change_level()
        self.number_of_level.setMaximum(self.painter.levels)
        self.setCentralWidget(p)

    def save_action(self):
        if not hasattr(self.painter, 'boards'):
            return
        if self.filename == '':
            self.save_as_action()
            return
        p = self.painter
        w = p.width
        f = open(self.filename, 'w')
        f.write(str(p.width) + '\n')
        f.write(str(p.height) + '\n')
        f.write(str(p.levels) + '\n')
        for board in p.boards:
            i = 0
            for elem in board:
                if elem:
                    f.write(str(i % w) + '.' + str(i // w) + '\n')
                i += 1
            f.write('$$$' + '\n')
        f.close()

    def save_as_action(self):
        if not hasattr(self.painter, 'boards'):
            return

        fname = QFileDialog.getSaveFileName(self, 'Save File', 'new.ark',
                                            'Arkanoid (*.ark)')[0]
        if fname:
            self.filename = fname
            self.save_action()
        else:
            return

    def color_cube(self):
        col = QColorDialog.getColor()
        if col.isValid():
            Painter.CELL_COLOR = col

    def point_action(self):
        self.change_button_state(POINT)

    def brush_action(self):
        self.change_button_state(BRUSH)

    def rect_action(self):
        self.change_button_state(RECTANGLE)

    def change_buttons_image(self):
        def foo(i, action):
            state = self.button_state[i]
            if state != self.prev_button_state[i]:
                action.setIcon(self.icons[i][self.button_state_list.get(state)])

        foo(POINT, self.point_action)
        foo(BRUSH, self.brush_action)
        foo(RECTANGLE, self.rect_action)

    def change_button_state(self, tool):
        # next active state of current tool
        def next_button_state():
            self.painter.mode = (self.painter.mode + 1) % 3
            self.button_state[self.painter.tool] = 'a' + str(self.painter.mode)

        # new active tool
        def switch_to_active(tool):
            # freeze and disable current tool state
            self.button_state[self.painter.tool] = 'd' + \
                                self.button_state[self.painter.tool][1]
            # set new active state
            self.button_state[tool] = 'a' + self.button_state[tool][1]
            self.painter.tool = tool

        if self.button_state[tool][0] == 'a':
            next_button_state()
        else:
            switch_to_active(tool)
        self.change_buttons_image()
        # rectangle_mode for rectangle
        if self.painter.tool == RECTANGLE:
            if self.painter.mode == EMPTY:
                self.painter.rectangle_mode = EMPTY
            else:
                self.painter.rectangle_mode = FULL

        self.prev_button_state = self.button_state.copy()
        self.painter.mode = int(self.button_state[tool][1])


class Painter(QWidget):

    EMPTY_CUBE = 0
    FULL_CUBE = 1
    CELL_COLOR = QColor(0x66CFFC)
    X = 0
    Y = 1

    def __init__(self):
        super().__init__()
        # tools: 0 - point, 1 - brush, 2 - rectangle
        self.tool = RECTANGLE
        # mode: 0 - empty, 1 - full, 2 - invert
        self.mode = INVERT
        self.levels = 1

    def initUI(self, w, h, lvl):
        self.width = w
        self.height = h
        self.levels = lvl
        self.current_level = 0

        self.boards = []
        for i in range(lvl):
            self.boards.append([])
            for _ in range(self.height * self.width):
                self.boards[i].append(Painter.EMPTY_CUBE)

        self.board = self.boards[self.current_level]
        self.prevCube = None
        self.startCube = None

        self.rectangle_mode = FULL  # filling or erasing rectangle
        self.states_under_rect = {}
        # if mouse move at other cell
        # (for rectangle mode draw point on single click)
        self.flag_move = False

    def change_level(self):
        self.board = self.boards[self.current_level]
        self.update()

    def what_at(self, x, y):
        try:
            return self.board[(y * self.width) + x]
        except:
            pass

    def set_cube_at(self, cube, x, y):
        if x != self.width and x >= 0:
            try:
                self.board[(y * self.width) + x] = cube
            except:
                pass

    def reverse_cube(self, x, y):
        if self.what_at(x, y) == Painter.EMPTY_CUBE:
            self.set_cube_at(Painter.FULL_CUBE, x, y)
        else:
            self.set_cube_at(Painter.EMPTY_CUBE, x, y)

    def square_width(self):
        return self.contentsRect().width() // self.width

    def square_height(self):
        return self.contentsRect().height() // self.height

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        rect = self.contentsRect()
        board_top = rect.bottom() - self.height * self.square_height()
        for i in range(self.height):
            for j in range(self.width):
                    cube = self.what_at(j, i)
                    if cube == Painter.EMPTY_CUBE:
                        self.draw_square(painter,
                                         rect.left() + j * self.square_width(),
                                         board_top + i * self.square_height())
                    else:
                        self.draw_square(painter,
                                         rect.left() + j * self.square_width(),
                                         board_top + i * self.square_height(),
                                         "full")

    def draw_square(self, painter, x, y, fill="emp"):
        color1 = QColor(0xC0C0C0)
        if fill == "emp":
            color2 = QColor(0xFFFFFF)
        else:
            color2 = Painter.CELL_COLOR

        painter.fillRect(x + 1, y + 1, self.square_width() - 2,
                         self.square_height() - 2, color2)
        painter.setPen(color1)
        painter.drawLine(x, y + self.square_height() - 1, x, y)
        painter.drawLine(x, y, x + self.square_width() - 1, y)
        painter.drawLine(x + 1, y + self.square_height() - 1,
                         x + self.square_width() - 1, y + self.square_height() - 1)
        painter.drawLine(x + self.square_width() - 1,
                         y + self.square_height() - 1, x + self.square_width() - 1, y + 1)

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return

        rect = self.contentsRect()
        board_top = rect.bottom() - self.height * self.square_height()
        cur_x = (e.x() - rect.left()) // self.square_width()
        cur_y = (e.y() - board_top) // self.square_height()

        if self.tool == RECTANGLE:
            self.flag_move = False
            self.states_under_rect = {}

            if self.mode == INVERT:
                self.reverse_cube(cur_x, cur_y)
                self.rectangle_mode = FULL \
                    if self.what_at(cur_x, cur_y) == Painter.FULL_CUBE \
                    else EMPTY
            elif self.mode == FULL:
                self.set_cube_at(Painter.FULL_CUBE, cur_x, cur_y)
            elif self.mode == EMPTY:
                self.set_cube_at(Painter.EMPTY_CUBE, cur_x, cur_y)
            self.startCube = (cur_x, cur_y)
            self.prevCube = (cur_x, cur_y)
        elif self.tool == BRUSH or self.tool == POINT:
            if self.tool == BRUSH:
                self.prevCube = (cur_x, cur_y)
            if self.mode == INVERT:
                self.reverse_cube(cur_x, cur_y)
            elif self.mode == FULL:
                self.set_cube_at(Painter.FULL_CUBE, cur_x, cur_y)
            elif self.mode == EMPTY:
                self.set_cube_at(Painter.EMPTY_CUBE, cur_x, cur_y)
        self.update()

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton:
            return

        if self.tool == RECTANGLE and self.flag_move:
            rect = self.contentsRect()
            board_top = rect.bottom() - self.height * self.square_height()
            cur_x = (e.x() - rect.left()) // self.square_width()
            cur_y = (e.y() - board_top) // self.square_height()

            if self.startCube == (cur_x, cur_y):
                self.reverse_cube(cur_x, cur_y)
                self.update()

    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.LeftButton:
            return

        rect = self.contentsRect()
        board_top = rect.bottom() - self.height * self.square_height()
        cur_x = (e.x() - rect.left()) // self.square_width()
        cur_y = (e.y() - board_top) // self.square_height()

        if (e.x() < 0) or (e.x() > rect.right()) or \
                (e.y() <= (rect.bottom() - self.square_height()
                    * self.height)) or \
                (e.y() > rect.bottom()):
            return

        if self.tool == POINT:
            return
        # not leave current cell
        if self.prevCube == (cur_x, cur_y):
            return
        if self.tool == RECTANGLE:
            self.flag_move = True
            self.draw_rectangle(e)
        elif self.tool == BRUSH:
            if self.mode == INVERT:
                self.reverse_cube(cur_x, cur_y)
            elif self.mode == FULL:
                self.set_cube_at(Painter.FULL_CUBE, cur_x, cur_y)
            elif self.mode == EMPTY:
                self.set_cube_at(Painter.EMPTY_CUBE, cur_x, cur_y)
            self.prevCube = (cur_x, cur_y)
        self.update()
        return

    def draw_rectangle(self, e):
        rect = self.contentsRect()
        boardTop = rect.bottom() - self.height * self.square_height()
        curX = (e.x() - rect.left()) // self.square_width()
        curY = (e.y() - boardTop) // self.square_height()

        x = Painter.X
        y = Painter.Y

        # if compression
        if curX < self.prevCube[x] and self.prevCube[x] > self.startCube[x] or \
                                curX > self.prevCube[x] and \
                                self.prevCube[x] < self.startCube[x] or \
                                curY < self.prevCube[y] and \
                                self.prevCube[y] > self.startCube[y] or \
                                curY > self.prevCube[y] and \
                                self.prevCube[y] < self.startCube[y]:
                self.compression_rectangle(curX, curY)
        else:
            self.extension_rectangle(curX, curY)
        self.prevCube = (curX, curY)

    def compression_rectangle(self, cur_x, cur_y):
        x = Painter.X
        y = Painter.Y

        if self.startCube[x] > cur_x:
            side_x = cur_x - 1
        elif self.startCube[x] == cur_x and self.prevCube[x] < self.startCube[x]:
            side_x = cur_x - 1
        else:
            side_x = cur_x + 1

        if self.startCube[y] > cur_y:
            side_y = cur_y - 1
        elif self.startCube[y] == cur_y and self.prevCube[y] < self.startCube[y]:
            side_y = self.prevCube[y]
        else:
            side_y = cur_y + 1 if cur_y != -1 else self.height

        # return last states
        del_from_states = []
        for k in self.states_under_rect.keys():
            if k[0] == side_x or k[1] == side_y:
                c = self.states_under_rect.get(k)
                self.set_cube_at(c, *k)
                del_from_states.append(k)

        for k in del_from_states:
            self.states_under_rect.pop(k)

    def extension_rectangle(self, cur_x, cur_y):
        x = Painter.X
        y = Painter.Y

        if self.mode == EMPTY or self.rectangle_mode == EMPTY:
            filler = Painter.EMPTY_CUBE
        else:
            filler = Painter.FULL_CUBE

        if self.startCube[0] > cur_x:
            range_x = range(cur_x, self.startCube[x] + 1)
        else:
            range_x = range(self.startCube[x], cur_x + 1)

        if self.startCube[1] > cur_y:
            range_y = range(cur_y, self.startCube[y] + 1)
        else:
            range_y = range(self.startCube[y], cur_y + 1)

        for i in range_x:
            if self.states_under_rect.get((i, cur_y)) is None:
                self.states_under_rect[(i, cur_y)] = self.what_at(i, cur_y)
                self.set_cube_at(filler, i, cur_y)
        for j in range_y:
            if self.states_under_rect.get((cur_x, j)) is None:
                self.states_under_rect[(cur_x, j)] = self.what_at(cur_x, j)
                self.set_cube_at(filler, cur_x, j)


if __name__ == '__main__':
    app = QApplication([])
    main_window = Main()
    sys.exit(app.exec_())
