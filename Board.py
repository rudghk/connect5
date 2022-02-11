from MinMax import *

BLACK = 0
WHITE = 1


class Board:
    def __init__(self) -> None:
        self.size = 15
        self.board_status = [[-1 for _ in range(self.size)] for _ in range(self.size)]
        self.cur_player = BLACK

    def draw(self) -> None:
        for x in range(self.size):
            for y in range(self.size):
                print(self.board_status[x][y], end='')
            print("") 

    def put(self, x, y, c) -> None:
        self.board_status[x][y] = c
        if c == BLACK:
            self.cur_player = WHITE
        else:
            self.cur_player = BLACK
    
    def rollback(self, x, y, c) -> None:
        self.board_status[x][y] = -1
        if c == BLACK:
            self.cur_player = BLACK
        else:
            self.cur_player = WHITE

    # (-1,0)부터 반시계 방향 + 자기 자신
    def direction(self, idx):
        x = [-1, -1, 0, 1, 1, 1, 0, -1, 0]
        y = [0, -1, -1, -1, 0, 1, 1, 1, 0]
        return x[idx], y[idx]

    # 판 범위 벗어나는지 확인
    def isOutOfRange(self, x, y):
        if x >= self.size or x < 0 or y >= self.size or y < 0:
                return True
        return False

    def getConnectedRelation(self, x, y, c, dir_type):
        # count, start_X, start_y
        count = 1
        for i in range(2):
            dir_x, dir_y = self.direction(4*i+dir_type)
            tmp_x = x + dir_x
            tmp_y = y + dir_y
            while(not self.isOutOfRange(tmp_x, tmp_y)):
                if self.board_status[tmp_x][tmp_y] != c:
                    break
                count += 1
                tmp_x += dir_x 
                tmp_y += dir_y
            if i == 0:
                start_x = tmp_x - dir_x
                start_y = tmp_y - dir_y
        # 양쪽 open 상태
        open = 0
        dir_x1, dir_y1 = self.direction(dir_type)
        dir_x2, dir_y2 = self.direction(4+dir_type)
        left_x = start_x + dir_x1
        left_y = start_y + dir_y1
        right_x = start_x + count*dir_x2
        right_y = start_y + count*dir_y2
        # print(dir_type, (start_x, start_y), (left_x, left_y), (right_x, right_y)) @@
        if not self.isOutOfRange(left_x, left_y) and self.board_status[left_x][left_y] == -1:
            open += 1
        if not self.isOutOfRange(right_x, right_y) and self.board_status[right_x][right_y] == -1:
            open += 1
        return count, start_x, start_y, open


    def getAllConnectedRelation(self, x, y, c):
        relations = []
        # 가로 : (-1,0)(1,0) => 4*i+0
        # 대각선(↘) : (-1,-1)(1,1) => 4*i+1
        # 세로 : (0,-1)(0,1) => 4*i+2
        # 대각선(↙) : (1,-1)(-1,1) => 4*i+3
        for i in range(4):
            relations.append(self.getConnectedRelation(x, y, c, i))
        return relations
    
    # 0(게임 끝x), 4(패/범위), 5(패/중복)
    def isWrongPosition(self, x, y) -> int:
        # 판 범위 벗어나는 수
        if(self.isOutOfRange(x, y)):
            return 4    # 패/범위
        # 이미 돌이 있는 위치
        if self.board_status[x][y] != -1:
            return 5    # 패/중복
        return 0

    def getOpen_3_4(self, relations):
        open3 = []  # relations에서 열린 연속된 3x3인 index
        open4 = []  # relations에서 열린 연속된 4x4인 index

        for idx in range(len(relations)):
            count, _, _, open = relations[idx]
            if count == 3 and open == 2:
                open3.append(idx)
            elif count == 4 and open == 2:
                open4.append(idx)
        # @@
        # print(relations)
        # print(open3)
        # print(open4)
        return open3, open4

    def isForbidden(self, relations) -> bool:
        # Gett open3, open4 dir_type
        open3, open4 = self.getOpen_3_4(relations)

        # 3x3
        if len(open3) > 1:
            return True
        if len(open3) == 1:
            dir_type = open3[0]
            count, start_x, start_y, _ = relations[dir_type]
            c = self.board_status[start_x][start_y]
            for i in range(count):
                dir_x, dir_y = self.direction(4+dir_type)
                tmp_relations = self.getAllConnectedRelation(start_x+i*dir_x, start_y+i*dir_y, c)
                tmp_open3, _ = self.getOpen_3_4(tmp_relations)
                if len(tmp_open3) > 1:
                    return True

        # 4x4
        if len(open4) > 1:
            return True
        if len(open4) == 1:
            dir_type = open4[0]
            count, start_x, start_y, _ = relations[dir_type]
            c = self.board_status[start_x][start_y]
            for i in range(count):
                dir_x, dir_y = self.direction(4+dir_type)
                tmp_relations = self.getAllConnectedRelation(start_x+i*dir_x, start_y+i*dir_y, c)
                _, tmp_open4 = self.getOpen_3_4(tmp_relations)
                if len(tmp_open4) > 1:
                    return True
        
        return False
    
    # 흑 기준 승/패 판단
    def gameover(self, x, y, c):
        relations = self.getAllConnectedRelation(x, y, c)
        # (흑) 금수 
        if c == BLACK:
            print("금수 체크")
            if self.isForbidden(relations):
                return 0, 0     # 흑 패-금수
        # 오목 완성
        for count, _, _, _ in relations:
            if count >= 5:
                xy = (x<<4) | y
                if c == BLACK:
                    return 1, xy    # 흑 승-오목/장목 완성(흑)
                else:
                    return 0, xy    # 흑 패-오목/장목 완성(백)
        return -1, -1

    # for minmax
    def getColorPos(self, color):  # color가 -1(empty), 0(black), 1(white)
        color_pos = []
        for x in range(self.size):
            for y in range(self.size):
                if self.board_status[x][y] == color:
                    color_pos.append((x, y))
        return color_pos

    # for minmax
    # 8 방향 내에 stone이 있는지 확인
    def hasNearStone(self, x, y):
        for idx in range(8):
            dir_x, dir_y = self.direction(idx)
            pos_x = x + dir_x
            pos_y = y + dir_y
            if not self.isOutOfRange(pos_x, pos_y):
                if self.board_status[pos_x][pos_y] != -1:
                    return True
        return False

class Player:
    def __init__(self, color, is_human) -> None:
        self.color = color # 0(black), 1(white)
        self.human = is_human
        if not is_human:
            self.ai = MinMax()
        else:
            self.ai = None
    
    def getAIPos(self, depth=3, board=None):
        if not self.human:
            print("search win pos")
            x, y = self.ai.searchWinPos(board, self.color)
            if x == None and y == None:
                print("before minmax")
                _, x, y = self.ai.minmax(depth, -1, self.ai.win_score, board, self.color, True)
                if x == None and y == None:
                    x = 7
                    y = 7
            return x, y