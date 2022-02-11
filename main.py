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
        self.event_loop = QEventLoop()
        self.gomoku = None

        # # timer
        # self.timer = QTimer(self)
        # self.timer.start(1000)
        # self.timer.timeout.connect(self.timeout)

        self.initUI()

    def initUI(self):
        self.setupUi(self)

        self.lcdTimer.display(15)
        self.pbExit.clicked.connect(self.exitEvent)
        self.pbReady.clicked.connect(self.readyEvent)
 
        self.scene = QGraphicsScene()        
        self.gvGameBoard.setScene(self.scene)
        pix = QPixmap('board_img.png')
        pix = pix.scaledToWidth(690)
        self.scene.addPixmap(pix)
           
        self.setWindowTitle('Gomoku')
        self.show()
    
    def timeout(self):
        self.lcdTimer.display(self.lcdTimer.value()-1)

    def exitEvent(self):
        if self.gomoku != None:
            self.gomoku.stop()
            self.gomoku.__del__()
        print("게임 종료")
        sys.exit(0)

    def readyEvent(self):
        type = self.cbType.currentText()
        type = type.split()
        if self.rbSingle.isChecked():
            self.game_mode = 1 # Single
        else:
            self.game_mode = 2 # Online

        status_list = ['Ready', 'Not Ready']
        status = self.pbReady.text()
        if status == status_list[0]:  
            if self.game_mode == 1:
                self.createPlayers(0, type[0]=='Human', 1, type[-1]=='Human')
                self.singlePlay()
            elif self.game_mode == 2:
                if self.gomoku == None:
                    color1 = self.connectServer()
                    self.gomoku.server_msg.connect(self.onlinePlay)
                    self.gomoku.start()
                else:
                    color1 = self.my_color
                self.createPlayers(color1, type[0]=='Human', (color1+1)%2, type[0]=='Human')
                self.gomoku.ready()       # 준비
                self.pbReady.setText(status_list[1])
                print('my color ' + str(self.my_color))
        else:
            if self.game_mode == 2:
                self.gomoku.ready(True)   # 준비 취소
            self.pbReady.setText(status_list[0])
        
    def createPlayers(self, color1, is_human1, color2, is_human2):
        self.players = []       # 흑, 백 순서로 insert
        player1 = Player(color1, is_human1)
        player2 = Player(color2, is_human2)
        self.my_color = color1
        self.other_color = color2
        if self.my_color == 0:
            self.players.append(player1)
            self.players.append(player2)
        else:
            self.players.append(player2)
            self.players.append(player1)
        print("Create plyaers "+str(self.my_color))
        print(self.players[self.my_color].human)

    def connectServer(self):
        self.gomoku = Gomoku(self.ip, self.port, True)    # 나중에 False로@@
        color = self.gomoku.connect()
        if color == -1:
            exit(0)
        return color

    def onlinePlay(self, cmd, turn, data): 
        if cmd == 2: # update 명령
            if data == 0:
                self.game_start = True   # game start
            if turn == 0:
                if data != 0:
                    x = (data >> 4) & 0xF
                    y = data & 0xF
                    print("recv" + str((x, y)))
                    self.updateEvent(x-1, y-1, self.other_color)
                if not self.players[self.my_color].human:
                    x, y = self.players[self.my_color].getAIPos(3, self.board)
                    print("send" + str((x, y)))
                    self.putStoneEvent(x, y)
                else:
                    self.event_loop.exec_()  
        if cmd == 4: # end 명령
            print("Game over")
            print(self.gomoku)
            self.gameoverEvent(turn, data)
    
    def singlePlay(self):
        print("k")

    def putStoneEvent(self, x, y):
        self.event_loop.exit()
        if self.game_mode == 2:
            res = self.gomoku.put(x+1, y+1)
        self.updateEvent(x, y, self.my_color)

    def updateEvent(self, x, y, c):
        # PUT on board
        self.board.put(x, y, c)
        # Game board
        self.drawStone(x, y)
        # History board
        last_color_str = '{0}'.format('백' if c else '흑')
        self.tbHistoryBoard.append('['+last_color_str+'] - ('+str(x)+', '+str(y)+')')
        # Timer
        self.lcdTimer.display(15)
        # Turn borad
        cur_color_str = '{0}'.format('백' if (c+1)%2 else '흑')
        self.lTurnBoard.setText('['+cur_color_str+']이 두는 중...')
        
    def drawStone(self, x, y):
        pos_x = self.start + x*self.interval - int(self.circle_size/2) # +29  # 29 보정(325-296)
        pos_y = self.start + y*self.interval - int(self.circle_size/2) # +29
        # print(pos_x, pos_y)
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
            x = (reason >> 4) & 0xF
            y = reason & 0xF
            print("recv" + str((x, y)))
            if result != 1:     # 상대가 오목을 완성한 경우, 최종 수 표현
                if self.game_mode == 2:
                    x = x-1
                    y = y-1
                self.updateEvent(x, y, self.other_color)
        result_str = 'Win' if result == 1 else 'Lose'
        color_str = '흑' if self.my_color == 0 else '백'
        msg = '['+color_str+'] '+result_str
        self.tbHistoryBoard.append(err_str)
        self.tbHistoryBoard.append(msg)
        reply = QMessageBox.information(self, 'Result', msg, QMessageBox.Ok)
        if reply == QMessageBox.Ok:
            print("Msg Game over")
            self.exitEvent()

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
