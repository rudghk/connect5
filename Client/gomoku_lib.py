from socket import *
from typing import Tuple
from PyQt5.QtCore import QThread, pyqtSignal

class Gomoku(QThread):
    server_msg = pyqtSignal(int, int, int)

    BUF_SIZE = 3
    TURN_BLACK = 0
    TURN_WHITE = 1

    def __init__(self, addr: str, port: int, print_mode: bool = False):
        QThread.__init__(self)
        self.socket = None
        self.color = ""
        self.print_mode = print_mode

        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        clientSocket.setsockopt(SOL_SOCKET, SO_SNDBUF, 3)
        clientSocket.setsockopt(SOL_SOCKET, SO_RCVBUF, 3)
        clientSocket.connect((addr, port))
        self.socket = clientSocket

        self.power = False


    def __del__(self):
        if self.socket:
            self.socket.close()

    def run(self):
        while not self.power:
            msg = self.socket.recv(Gomoku.BUF_SIZE)
            if msg != b'':
                print("== msg ==")
                print(msg)
                self.server_msg.emit(msg[0], msg[1], msg[2])

    def stop(self):
        self.power = True
        self.quit()
        self.wait(100) # 0.1초


    def recv(self) -> Tuple[bytes, bytes, bytes]:
        msg = self.socket.recv(Gomoku.BUF_SIZE)
        return msg[0], msg[1], msg[2]


    def send(self, cmd: int, turn: int, data: int) -> bool:
        try:
            self.socket.send(bytes([cmd, turn, data]))
            return True
        except Exception:
            return False
        

    def connect(self) -> int:
        try:
            self.send(0, 0, 0)
            cmd, turn, data = self.recv()
            if(data == 1):
                self.color = "black" if turn == 0 else "white"
                if self.print_mode:
                    print("Your color is {}".format(self.color))
                return turn
            elif(data == 2):
                if self.print_mode:
                    print("Cannot Connect")
                return -1
            else:
                if self.print_mode:
                    print("Error during connect")
                return -1
        except Exception as e:
            if self.print_mode:
                print("{} exception during connect".format(e))
            return -1


    def ready(self, cancel: bool = False) -> bool:
        try:
            if self.color == "black":
                turn_color = Gomoku.TURN_BLACK
            elif self.color == "white":
                turn_color = Gomoku.TURN_WHITE
            
            if cancel:
                self.send(1, turn_color, 0)
                if self.print_mode:
                    print("cancel ready")
                return True
            else:
                self.send(1, turn_color, 1)
                if self.print_mode:
                    print("ready")
                return True
        except Exception as e:
            if self.print_mode:
                print("{} exception during ready".format(e))


    def put(self, x: int, y: int) -> bool:
        try:
            x_byte = x << 4
            xy_byte = x_byte + y
            ret = self.send(3, 0, xy_byte)
            if not ret:
                raise Exception("send error")
            if self.print_mode:
                print("put {}, {}".format(x, y))
            return True
        except Exception as e:
            if self.print_mode:
                print("{} exception during put".format(e))
            return False


    def update_or_end(self) -> Tuple[bool, int, int, bytes]:
        try:
            cmd, turn, data = self.recv()
            cmd, turn = int(cmd), int(turn)
            if cmd == 2:
                if self.print_mode:
                    print("update")
                return (True, cmd, turn, data)
            elif cmd == 4:
                if self.print_mode:
                    print("end")
                return (True, cmd, turn, data)
            else:
                if self.print_mode:
                    print("error during update_or_end")
                return (False, 0, 0, 0)
        except Exception as e:
            if self.print_mode:
                print("{} exception during update_or_end".format(e))
            return (False, 0, 0, 0)
        
