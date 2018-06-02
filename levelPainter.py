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

        self.icons = [
            [QIcon(os.path.join(os.getcwd(),'pics', 'point0.png')), QIcon(os.path.join(os.getcwd(),'pics', 'point01.png')),
             QIcon(os.path.join(os.getcwd(),'pics', 'point1.png')), QIcon(os.path.join(os.getcwd(),'pics', 'point11.png')),
             QIcon(os.path.join(os.getcwd(),'pics', 'point2.png')), QIcon(os.path.join(os.getcwd(),'pics', 'point21.png'))],
            [QIcon(os.path.join(os.getcwd(), 'pics', 'brush0.png')), QIcon(os.path.join(os.getcwd(), 'pics', 'brush01.png')),
             QIcon(os.path.join(os.getcwd(), 'pics', 'brush1.png')), QIcon(os.path.join(os.getcwd(), 'pics', 'brush11.png')),
             QIcon(os.path.join(os.getcwd(), 'pics', 'brush2.png')), QIcon(os.path.join(os.getcwd(), 'pics', 'brush21.png'))],
            [QIcon(os.path.join(os.getcwd(), 'pics', 'rect0.png')), QIcon(os.path.join(os.getcwd(), 'pics', 'rect01.png')),
             QIcon(os.path.join(os.getcwd(), 'pics', 'rect1.png')), QIcon(os.path.join(os.getcwd(), 'pics', 'rect11.png')),
             QIcon(os.path.join(os.getcwd(), 'pics', 'rect2.png')), QIcon(os.path.join(os.getcwd(), 'pics', 'rect21.png'))]
        ]

        def create_toolbar_action(name, function):
            qaction = QAction('&' +name, self)
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

        def create_action(name, function, shortcut = ''):
            qaction = QAction(name, self)
            qaction.setShortcut(shortcut)
            qaction.triggered.connect(function)
            return qaction

        new = create_action('New', self.new_action, 'Ctrl+N')
        load = create_action('Load', self.load_action, 'Ctrl+L')
        save = create_action('Save', self.save_action, 'Ctrl+S')
        saveAs = create_action('Save As', self.save_as_action)

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(new)
        fileMenu.addAction(load)
        fileMenu.addAction(save)
        fileMenu.addAction(saveAs)

        col_cube = create_action('Cells', self.color_cube)

        colMenu = menubar.addMenu('&Color')
        colMenu.addAction(col_cube)

        self.setGeometry(300, 300, 200, 230)
        self.setWindowTitle('Level Painter')
        self.show()


    def new_action(self):
        class newForm(QWidget):
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
                    main_window.number_of_level.setMaximum(main_window.painter.levels)
                    main_window.setCentralWidget(main_window.painter)
                    main_window.filename = ''
                    self.close()

                self.label_size = create_label(95, 10, 'Size')
                self.sbx = create_spin_box(65, 35, 10, 50)
                self.label_x = create_label(108, 38, 'x')
                self.sby = create_spin_box(120, 35, 10, 50)
                self.labelcx = create_label(77, 58, 'X')
                self.labelcy = create_label(132, 58, 'Y')

                self.label_num = create_label(10, 83, 'Number of levels (1-15):')
                self.sbn = create_spin_box(179, 81, 1, 15)

                self.btn = QPushButton('OK', self)
                self.btn.clicked.connect(btn_click)
                self.btn.move(70, 110)

                self.setGeometry(340, 340, 230, 140)
                self.setWindowTitle('New Levels Settings')
                self.setFocus()

        self.new_form = newForm()
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
                    p.set_cube_at(Painter.FULL_CUBE, int(_.split('.')[0]), int(_.split('.')[1]))
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

        fname = QFileDialog.getSaveFileName(self, 'Save File', 'new.ark','Arkanoid (*.ark)')[0]
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
            self.button_state[self.painter.tool] = 'd' + self.button_state[self.painter.tool][1]
            # set new active state
            self.button_state[tool] = 'a' + self.button_state[tool][1]
            self.painter.tool = tool

        if self.button_state[tool][0] == 'a':
            next_button_state()
        else:
            switch_to_active(tool)
        self.change_buttons_image()
        #rectangle_mode for rectangle
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
        #tools: 0 - point, 1 - brush, 2 - rectangle
        self.tool = RECTANGLE
        #mode: 0 - empty, 1 - full, 2 - invert
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
            self.board = self.boards[i]
            self.clear_board()

        self.board = self.boards[self.current_level]
        self.prevCube = None
        self.startCube = None

        self.rectangle_mode = FULL  # filling or disfilling rectangle
        self.states_under_rect = {}
        self.flag_move = False  # if mouse move at other cell (for rectangle mode draw point on single click)


    def change_level(self):
        self.board = self.boards[self.current_level]
        self.update()

    def clear_board(self):
        for i in range(self.height * self.width):
            self.board.append(Painter.EMPTY_CUBE)

    def what_at(self, x, y):
        try:
            return self.board[(y * self.width) + x]
        except:
            print(y, x)

    def set_cube_at(self, cube, x, y):
        if x != self.width and x >= 0:
            try:
                self.board[(y * self.width) + x] = cube
            except:
                print(x, y, (y * self.width) + x)

    def reverse_cube(self, x, y):
        if self.what_at(x, y) == Painter.EMPTY_CUBE:
            self.set_cube_at(Painter.FULL_CUBE, x, y)
        else:
            self.set_cube_at(Painter.EMPTY_CUBE, x, y)

    def squareWidth(self):
        return self.contentsRect().width() // self.width

    def squareHeight(self):
        return self.contentsRect().height() // self.height

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        rect = self.contentsRect()
        boardTop = rect.bottom() - self.height * self.squareHeight()
        for i in range(self.height):
            for j in range(self.width):
                    cube = self.what_at(j, i)
                    if cube == Painter.EMPTY_CUBE:
                        self.drawSquare(painter,
                                        rect.left() + j * self.squareWidth(),
                                        boardTop + i * self.squareHeight())
                    else:
                        self.drawSquare(painter,
                                        rect.left() + j * self.squareWidth(),
                                        boardTop + i * self.squareHeight(), "full")

    def drawSquare(self, painter, x, y, type = "e"):
        color1 = QColor(0xC0C0C0)
        if type == "e":
            color2 = QColor(0xFFFFFF)
        else:
            color2 = Painter.CELL_COLOR

        painter.fillRect(x + 1, y + 1, self.squareWidth() - 2,
            self.squareHeight() - 2, color2)
        painter.setPen(color1)
        painter.drawLine(x, y + self.squareHeight() - 1, x, y)
        painter.drawLine(x, y, x + self.squareWidth() - 1, y)
        painter.drawLine(x + 1, y + self.squareHeight() - 1,
            x + self.squareWidth() - 1, y + self.squareHeight() - 1)
        painter.drawLine(x + self.squareWidth() - 1,
            y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return

        rect = self.contentsRect()
        boardTop = rect.bottom() - self.height * self.squareHeight()
        curX = (e.x() - rect.left()) // self.squareWidth()
        curY = (e.y() - boardTop ) // self.squareHeight()

        if self.tool == RECTANGLE:
            self.flag_move = False
            self.states_under_rect = {}

            if self.mode == INVERT:
                self.reverse_cube(curX, curY)
                self.rectangle_mode = FULL if self.what_at(curX, curY) == Painter.FULL_CUBE else EMPTY
            elif self.mode == FULL:
                self.set_cube_at(Painter.FULL_CUBE, curX, curY)
            elif self.mode == EMPTY:
                self.set_cube_at(Painter.EMPTY_CUBE, curX, curY)
            self.startCube = (curX, curY)
            self.prevCube = (curX, curY)
        elif self.tool == BRUSH or self.tool == POINT:
            if self.tool == BRUSH:
                self.prevCube = (curX, curY)
            if self.mode == INVERT:
                self.reverse_cube(curX, curY)
            elif self.mode == FULL:
                self.set_cube_at(Painter.FULL_CUBE, curX, curY)
            elif self.mode == EMPTY:
                self.set_cube_at(Painter.EMPTY_CUBE, curX, curY)
        self.update()


    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton:
            return

        if self.tool == RECTANGLE and self.flag_move:
            rect = self.contentsRect()
            boardTop = rect.bottom() - self.height * self.squareHeight()
            curX = (e.x() - rect.left()) // self.squareWidth()
            curY = (e.y() - boardTop) // self.squareHeight()

            if self.startCube == (curX , curY):
                self.reverse_cube(curX, curY)
                self.update()

    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.LeftButton:
            return

        rect = self.contentsRect()
        boardTop = rect.bottom() - self.height * self.squareHeight()
        curX = (e.x() - rect.left()) // self.squareWidth()
        curY = (e.y() - boardTop) // self.squareHeight()

        if (e.x() < 0) or (e.x() > rect.right()) or \
                (e.y() <= (rect.bottom() - self.squareHeight() * self.height)) or \
                (e.y() > rect.bottom()):
            return

        if self.tool == POINT:
            return
        # not leave current cell
        if self.prevCube == (curX, curY):
            return
        if self.tool == RECTANGLE:
            self.flag_move = True
            self.draw_rectangle(e)
        elif self.tool == BRUSH:
            if self.mode == INVERT:
                self.reverse_cube(curX, curY)
            elif self.mode == FULL:
                self.set_cube_at(Painter.FULL_CUBE, curX, curY)
            elif self.mode == EMPTY:
                self.set_cube_at(Painter.EMPTY_CUBE, curX, curY)
            self.prevCube = (curX, curY)
        self.update()
        return

    def draw_rectangle(self, e):
        rect = self.contentsRect()
        boardTop = rect.bottom() - self.height * self.squareHeight()
        curX = (e.x() - rect.left()) // self.squareWidth()
        curY = (e.y() - boardTop) // self.squareHeight()

        X = Painter.X
        Y = Painter.Y

        #if compression
        if curX < self.prevCube[X] and self.prevCube[X] > self.startCube[X] or \
                                curX > self.prevCube[X] and self.prevCube[X] < self.startCube[X] or \
                                curY < self.prevCube[Y] and self.prevCube[Y] > self.startCube[Y] or \
                                curY > self.prevCube[Y] and self.prevCube[Y] < self.startCube[Y]:
                self.compressionRectangle(curX, curY)
        else:
            self.extensionRectangle(curX, curY)
        self.prevCube = (curX, curY)

    def compressionRectangle(self, curX, curY):
        X = Painter.X
        Y = Painter.Y

        if self.startCube[X] > curX:
            side_x = curX - 1
        elif self.startCube[X] == curX and self.prevCube[X] < self.startCube[X]:
            side_x = curX - 1
        else:
            side_x = curX + 1

        if self.startCube[Y] > curY:
            side_y = curY - 1
        elif self.startCube[Y] == curY and self.prevCube[Y] < self.startCube[Y]:
            side_y = self.prevCube[Y]
        else:
            side_y = curY + 1 if curY != -1 else self.height

        #return last states
        del_from_states = []
        for k in self.states_under_rect.keys():
            if k[0] == side_x or k[1] == side_y:
                c = self.states_under_rect.get(k)
                self.set_cube_at(c, *k)
                del_from_states.append(k)

        for k in del_from_states:
            self.states_under_rect.pop(k)

    def extensionRectangle(self,curX, curY):
        X = Painter.X
        Y = Painter.Y

        if self.mode == EMPTY or self.rectangle_mode == EMPTY:
            filler = Painter.EMPTY_CUBE
        else:
            filler = Painter.FULL_CUBE

        if self.startCube[0] > curX:
            rangeX = range(curX, self.startCube[X] + 1)
        else:
            rangeX = range(self.startCube[X], curX + 1)

        if self.startCube[1] > curY:
            rangeY = range(curY, self.startCube[Y] + 1)
        else:
            rangeY = range(self.startCube[Y], curY + 1)

        for i in rangeX:
            if self.states_under_rect.get((i, curY)) == None:
                self.states_under_rect[(i, curY)] = self.what_at(i, curY)
                self.set_cube_at(filler, i, curY)
        for j in rangeY:
            if self.states_under_rect.get((curX, j)) == None:
                self.states_under_rect[(curX, j)] = self.what_at(curX, j)
                self.set_cube_at(filler, curX, j)


if __name__ == '__main__':
    app = QApplication([])
    main_window = Main()
    sys.exit(app.exec_())
