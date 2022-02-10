from Board import *
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGraphicsScene, QMessageBox
from PyQt5.QtGui import QPen, QBrush, QPixmap
from PyQt5.QtCore import Qt, QTimer, QEventLoop
from PyQt5 import uic
from MinMax import *
from gomoku_lib import Gomoku

form_class = uic.loadUiType('GameUI.ui')[0]

class MyApp(QWidget, form_class):
    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port
        self.game_start = False
        self.board = Board()
        self.interval = 45
        self.start = 30
        self.end = self.start+self.interval*(self.board.size-1)
        self.circle_size = 40

        # # timer
        # self.timer = QTimer(self)
        # self.timer.start(1000)
        # self.timer.timeout.connect(self.timeout)

        self.initUI()
    
    def connectServer(self):
        self.gomoku = Gomoku(self.ip, self.port, True)    # 나중에 False로@@
        color = self.gomoku.connect()
        if color == -1:
            exit(0)
        self.my_color = color
        self.other_color = (color+1) % 2
        
    def createPlayers(self, id1, is_human1, id2, is_human2):
        self.players = []       # 흑, 백 순서로 insert
        player1 = Player(self.my_color, id1, is_human1)
        player2 = Player(self.other_color, id2, is_human2)
        if self.my_color == 0:
            self.players.append(player1)
            self.players.append(player2)
        else:
            self.players.append(player2)
            self.players.append(player1)
        print(self.players[0].id, self.players[1].id)
        print(self.my_color)
        print(self.players[self.my_color].id)

    def initUI(self):
        self.setupUi(self)

        self.lcdTimer.display(15)
        self.pbExit.clicked.connect(self.exitEvent)
        self.pbReady.clicked.connect(self.readyEvent)
        self.rbHAI.clicked.connect(self.selectMode)
        self.rbHH.clicked.connect(self.selectMode)
        self.rbAIAI.clicked.connect(self.selectMode)
 
        self.scene = QGraphicsScene()        
        self.gvGameBoard.setScene(self.scene)
        pix = QPixmap('board_img.png')
        pix = pix.scaledToWidth(690)
        self.scene.addPixmap(pix)
        
        self.event_loop = QEventLoop()
        self.connectServer()
        self.gomoku.server_msg.connect(self.play)
        self.gomoku.start()
    
        self.setWindowTitle('Gomoku')
        self.show()
    
    def selectMode(self):
        if self.rbHAI.isChecked():
            self.createPlayers("Human", True, "AI", False)
        elif self.rbHH.isChecked():
            self.createPlayers("Human1", True, "Human2", True)
        elif self.rbAIAI.isChecked():
            self.createPlayers("AI1", False, "AI2", False)

    def timeout(self):
        self.lcdTimer.display(self.lcdTimer.value()-1)

    def exitEvent(self):
        self.gomoku.__del__()
        print("게임 강제 종료")
        sys.exit(0)

    def readyEvent(self):
        # 모드 선택 먼저 되어 있어야함
        if not (self.rbHAI.isChecked() or self.rbHH.isChecked() or self.rbAIAI.isChecked()):
            return
        status_list = ['Ready', 'Not Ready']
        status = self.pbReady.text()
        if status == status_list[0]:  
            self.gomoku.ready()       # 준비
            self.pbReady.setText(status_list[1])
            print('my color ' + str(self.my_color))
        else:
            self.gomoku.ready(True)   # 준비 취소
            self.pbReady.setText(status_list[0])

    def play(self, cmd, turn, data): 
        if cmd == 2: # update 명령
            if data == 0:
                self.game_start = True   # game start
            if turn == 0:
                if data != 0:
                    x = (data >> 4) & 0xF
                    y = data & 0xF
                    print("recv" + str((x, y)))
                    self.updateEvent(x, y, self.other_color)
                if not self.players[self.my_color].human:
                    x, y = self.players[self.my_color].getAIPos(3, self.board)
                    print("send" + str((x, y)))
                    self.putStoneEvent(x, y)
                else:
                    self.event_loop.exec_()
                    
        if cmd == 4: # end 명령
            print("Game over")
            print(self.gomoku)
            self.gomoku.stop()
            self.gomoku.__del__()
            self.gameoverEvent(turn, data)
    
    def putStoneEvent(self, x, y):
        res = self.gomoku.put(x, y)
        self.event_loop.exit()
        self.updateEvent(x, y, self.my_color)

    def updateEvent(self, x, y, c):
        # PUT on board
        self.board.put(x, y, c)
        # Game board
        self.drawStone(x, y)
        # History board
        last_player = self.players[c]
        last_color_str = '{0}'.format('백' if last_player.color else '흑')
        self.tbHistoryBoard.append(last_player.id+'['+last_color_str+'] - ('+str(x)+', '+str(y)+')')
        # Timer
        self.lcdTimer.display(15)
        # Turn borad
        self.lTurnBoard.setText(self.players[self.board.cur_player].id+'이(가) 두는 중...')
        
    def drawStone(self, x, y):
        pos_x = self.start + x*self.interval - int(self.circle_size/2) +29  # 29 보정(325-296)
        pos_y = self.start + y*self.interval - int(self.circle_size/2) +29
        print(pos_x, pos_y)
        color = self.board.board_status[x][y]
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        brush = QBrush(Qt.black, Qt.SolidPattern)   # black
        if color == 1:    # white
            brush = QBrush(Qt.white, Qt.SolidPattern)
        self.scene.addEllipse(pos_x, pos_y, self.circle_size, self.circle_size, pen, brush)

    def mousePressEvent(self, e):
        # pos x, y 계산해서 putstoneEvent
        # print(e.pos())
        if not self.game_start:
            return
        if self.board.cur_player == self.my_color and self.players[self.my_color].human:
            cal_x = (e.pos().x()-35) // 45
            cal_y = (e.pos().y()-45) // 45
            # print(cal_x, cal_y)
            if not self.board.isOutOfRange(cal_x, cal_y):
                # return cal_x, cal_y
                self.putStoneEvent(cal_x, cal_y)
    
    def gameoverEvent(self, result, reason):
        # 사유
        if reason == 0:
            err_str = '오류'
        elif reason == 1:
            err_str = '시간 초과'
        else:
            err_str = '오목 완성'
        result_str = 'Win' if result == 1 else 'Lose'
        color_str = '흑' if self.my_color == 0 else '백'
        msg = self.players[self.my_color].id+'['+color_str+'] '+result_str
        self.tbHistoryBoard.append(err_str)
        self.tbHistoryBoard.append(msg)
        reply = QMessageBox.information(self, 'Result', msg, QMessageBox.Ok)
        if reply == QMessageBox.Ok:
            print("Game over")
            sys.exit(0)
    
if __name__ == '__main__':
    import signal
    import sys

    def handler(signal, frame):
        print("\nBye bye~")
        sys.exit(0)

    signal.signal(signal.SIGINT, handler)

    app = QApplication(sys.argv)
    ex = MyApp('localhost', 1234)

    sys.exit(app.exec_())
