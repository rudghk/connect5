from Board import *
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGraphicsScene, QMessageBox
from PyQt5.QtGui import QPen, QBrush, QPixmap
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import uic
from MinMax import *

form_class = uic.loadUiType('GameUI.ui')[0]

class MyApp(QWidget, form_class):
    def __init__(self, player1, player2):
        super().__init__()
        self.board = Board()
        self.interval = 45
        self.start = 30
        self.end = self.start+self.interval*(self.board.size-1)
        self.circle_size = 40
        self.players = [player1, player2]

        # # timer
        # self.timer = QTimer(self)
        # self.timer.start(1000)
        # self.timer.timeout.connect(self.timeout)

        self.initUI()

    def initUI(self):
        self.setupUi(self)

        self.lcdTimer.display(15)
        self.pbExit.clicked.connect(self.exitEvent)
        # ready @
        
        # h vs ai @
        # ai vs ai @
        # h vs h @
        # lModeBoard @
        
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
        print("게임 강제 종료")
        sys.exit(0)

    def putStoneEvent(self, x, y, c):
        # (x,y) 좌표 유효성 확인
        res = self.board.isWrongPosition(x, y)
        if res != 0:
            self.tbHistoryBoard.append('<<잘못된 위치>>')
            self.tbHistoryBoard.append(self.players[c].id+' Lose')
            self.gameoverEvent(c, 'Lose')
        # PUT
        self.board.put(x, y, c)
        # Game board
        self.drawStone(x, y)
        # History board
        last_player = self.players[c]
        last_color_str = '{0}'.format('백' if last_player.color else '흑')
        self.tbHistoryBoard.append(last_player.id+'['+last_color_str+'] - ('+str(x)+', '+str(y)+')')
        # Gameover 판단
        res = self.board.gameover(x, y, c)
        if res != 0:
            if res == 1:
                errStr = '<<금수 발생>>'
                result = 'Lose'
            elif res == 2:
                errStr = '<<오목 완성>>'
                result = 'Win'
            elif res == 3:
                errStr = '<<장목 완성>>'
                result = 'Win'
            self.tbHistoryBoard.append(errStr)
            self.tbHistoryBoard.append(last_player.id+'['+last_color_str+'] '+result)
            self.gameoverEvent(c, result)
        # Timer
        self.lcdTimer.display(15)
        # Turn borad
        self.lTurnBoard.setText(self.players[self.board.cur_player].id+'이(가) 두는 중...')
        
    def drawStone(self, x, y):
        pos_x = self.start + x*self.interval - int(self.circle_size/2)
        pos_y = self.start + y*self.interval - int(self.circle_size/2)
        color = self.board.board_status[x][y]
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        brush = QBrush(Qt.black, Qt.SolidPattern)   # black
        if color == 1:    # white
            brush = QBrush(Qt.white, Qt.SolidPattern)
        self.scene.addEllipse(pos_x, pos_y, self.circle_size, self.circle_size, pen, brush)

    def mousePressEvent(self, e):
        # pos x, y 계산해서 putstoneEvent
        # print(e.pos())
        cal_x = (e.pos().x()-35) // 45
        cal_y = (e.pos().y()-45) // 45
        # print(cal_x, cal_y)
        if not self.board.isOutOfRange(cal_x, cal_y):
            self.putStoneEvent(cal_x, cal_y, self.board.cur_player)
    
    def gameoverEvent(self, c, result):
        result_str = self.players[c].id+' '+result
        reply = QMessageBox.information(self, 'Result', result_str, QMessageBox.Ok)
        if reply == QMessageBox.Ok:
            print("Game over")
            sys.exit(0)
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    player1 = Player()
    player2 = Player()
    player1.setInfo(BLACK,"Human", True)
    player2.setInfo(WHITE,"AI", True)
    ex = MyApp(player1, player2)
    ai = MinMax()

    while(True):
        if(ex.board.cur_player == player1.color):
            print("current player is "+player1.id+".")
            x = input("x 좌표(0 ~ 14) : ")
            y = input("y 좌표(0 ~ 14) : ")
        else:
            print("current player is "+player2.id+".")
            _, x, y = ai.minmax(3, -1, win_score, ex.board, player2.color, True)
            print((x, y))
            # x = input("x 좌표(0 ~ 14) : ")
            # y = input("y 좌표(0 ~ 14) : ")
        ex.putStoneEvent(int(x), int(y), ex.board.cur_player)
        print("==========")
        ex.board.draw()
        print("----------")

    sys.exit(app.exec_())
