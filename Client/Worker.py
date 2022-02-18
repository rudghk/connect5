from PyQt5.QtCore import QThread, pyqtSignal

# To find AI movement through thread
class Worker(QThread):
    pos = server_msg = pyqtSignal(int, int)

    def __init__(self, player, depth, board):
        QThread.__init__(self)
        self.player = player
        self.depth = depth
        self.board = board
    
    def run(self):
        x,y = self.player.getAIPos(self.depth, self.board)
        self.pos.emit(x, y)
    
    def stop(self):
        self.quit()
        self.wait(100) # 0.1초