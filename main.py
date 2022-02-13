from Board import *
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGraphicsScene, QMessageBox
from PyQt5.QtGui import QPen, QBrush, QPixmap
from PyQt5.QtCore import Qt, QTimer, QEventLoop
from PyQt5 import uic
from Worker import Worker
from gomoku_lib import Gomoku

form_class = uic.loadUiType('GameUI.ui')[0]

IP = 'localhost'
PORT = 1234
DEPTH = 3

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
        self.xy = (-1, -1)   

        self.initUI()

    def initUI(self):
        self.setupUi(self)

        # timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeout)

        self.lcdTimer.display(18)
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
        left_time = self.lcdTimer.value()
        if left_time < 0:
            result = 0 if self.my_color == self.board.cur_player else 1
            self.gameoverEvent(result, 1)
        self.lcdTimer.display(left_time-1)

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
                self.game_start = True
                self.timer.start(1000)
                self.pbReady.setText('Playing...')
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

    # Calcuate AI pos
    def workerGetAIPos(self, x, y):
        self.xy = (x, y)
        self.event_loop.exit()

    # user's mouse input 기반 x, y 계산
    def mousePressEvent(self, e):
        # print(e.pos())
        if not self.game_start:
            return
        flag = False
        if self.game_mode == 1:
            turn = self.board.cur_player
            if self.players[turn].human:
                flag = True
        elif self.game_mode == 2:
            turn = self.my_color
            if self.board.cur_player == turn and self.players[turn].human:
                flag = True
        if flag:
            cal_x = (e.pos().x()-35) // 45
            cal_y = (e.pos().y()-45) // 45
            # print(cal_x, cal_y)
            if not self.board.isOutOfRange(cal_x, cal_y):
                self.xy = (cal_x, cal_y)
                self.event_loop.exit()

    def onlinePlay(self, cmd, turn, data): 
        if cmd == 2: # update 명령
            if data == 0:
                self.game_start = True   # game start
                self.pbReady.setText('Playing...')
                self.timer.start(1000)
            if turn == 0:
                if data != 0:
                    x = ((data >> 4) & 0xF) -1
                    y = (data & 0xF) -1
                    print("recv" + str((x, y)))
                    self.updateEvent(x, y, self.other_color)
                if not self.players[self.my_color].human:
                    worker = Worker(self.players[self.my_color], DEPTH, self.board)
                    worker.pos.connect(self.workerGetAIPos)
                    worker.start()
                self.event_loop.exec_()     # wait for 'getting AI pos' or 'user's mouse input'
                if not self.players[self.my_color].human:
                    worker.stop()           # worker 종료
                self.putStoneEvent(self.xy[0], self.xy[1], self.my_color) 
                self.xy = (-1, -1)  # 초기화
        if cmd == 4: # end 명령
            print("Game over")
            print(self.gomoku)
            self.gameoverEvent(turn, data)

    def singlePlay(self):
        while(True):
            turn = self.board.cur_player
            if not self.players[turn].human:
                worker = Worker(self.players[turn], DEPTH, self.board)
                worker.pos.connect(self.workerGetAIPos)
                worker.start()
            self.event_loop.exec_()     # wait for 'getting AI pos' or 'user's mouse input'
            origin = self.board.board_status[self.xy[0]][self.xy[1]]
            if not self.players[turn].human:
                worker.stop()   # worker 종료
            self.putStoneEvent(self.xy[0], self.xy[1], turn)
            # 흑 기준으로 승패 결과 반환
            # result : -1(게임 끝x,)1(흑 승), 2(흑 패)
            if origin != -1:    # 기존 돌이 있는 위치에 수를 놓은 경우
                if turn == 0:
                    result = 0
                else:
                    result = 1
                self.gameoverEvent(result, 0)  
            else:
                result, reason = self.board.gameover(self.xy[0], self.xy[1], turn)
                self.xy = (-1, -1)   # 초기화
                if result != -1:
                    self.gameoverEvent(result, reason)

    def putStoneEvent(self, x, y, c):
        if self.game_mode == 2:
            res = self.gomoku.put(x+1, y+1)
        self.updateEvent(x, y, c)

    def updateEvent(self, x, y, c):
        # PUT on board
        self.board.put(x, y, c)     # cur_player 변경됨
        # Game board
        self.drawStone(x, y)
        # History board
        last_color_str = '{0}'.format('백' if c else '흑')
        self.tbHistoryBoard.append('['+last_color_str+'] - ('+str(x)+', '+str(y)+')')
        # Timer
        self.lcdTimer.display(18)       # 15+3(서버 딜레이 고려)
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
    
    def gameoverEvent(self, result, reason):
        self.timer.stop()
        # 사유
        if reason == 0:
            err_str = '오류'
        elif reason == 1:
            err_str = '시간 초과'
        else:
            err_str = '오목 완성'
            if result != 1:     # 상대가 오목을 완성한 경우, 최종 수 표현
                if self.game_mode == 2:
                    x = ((reason >> 4) & 0xF) -1
                    y = (reason & 0xF) -1
                    print("recv" + str((x, y)))
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
    app = QApplication(sys.argv)
    ex = MyApp(IP, PORT)

    sys.exit(app.exec_())
