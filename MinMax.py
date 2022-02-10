from copy import deepcopy
from Board import *

class MinMax:
    def __init__(self) -> None:
        self.win_score = 100000000

    # 패턴 수치화@@
    def calScoreOfRelation(self, count, open) -> int:
        base_score = 10000
        if count > 5:   # 장목
            return base_score*2
        if count < 5 and open == 0:
            return 0
        if count == 5:
            return self.win_score
        if count == 4:
            if open == 2: return base_score
            else: return 200
        if count == 3:
            if open == 2: return base_score/50
            else: return 10
        if count == 2:
            if open == 2: return 7
            else: return 3
        if count == 1:
            return 1

    # color 돌 기준으로 borad의 점수 계산
    def getScore(self, board, color) -> int:
        color_pos = board.getColorPos(color)  # 해당 color 돌이 있는 자표

        # 해당 color의 관계(count, open 등) 파악
        all_relations = {'horizontal':[], 'dialogL2R':[], 'vertical':[], 'dialogR2L':[]}
        for x, y in color_pos:
            relations = board.getAllConnectedRelation(x, y, color)
            i  = 0
            for value in all_relations.values():
                value.append(relations[i])
                i += 1
        # 중복 제거
        for key in all_relations.keys():
            all_relations[key] = list(set(all_relations[key]))

        # 보드판에 최종 점수 계산
        total = 0
        for dir_relations in all_relations.values():
            for count, _, _, open in dir_relations:
                total += self.calScoreOfRelation(count, open)
        return total
    
    def minmax(self, depth, alpha, beta, board, my_color, my_turn):
        # leaf node
        if depth == 0:
            score = self.getScore(board, my_color)
            return score, None, None    # score, x, y
        
        # 주변에 stone이 있는 empty 좌표
        possible_pos = board.getColorPos(-1)  # empty 좌표들
        rm_pos = []
        for x, y in possible_pos:
            if not board.hasNearStone(x, y):
                rm_pos.append((x, y))
        for pos in rm_pos:
            possible_pos.remove(pos)

        # 흑돌인 경우 금수 위치 제거
        if my_color == 0:
            rm_pos = []
            for x, y in possible_pos:
                board.put(x, y, my_color)
                relations = board.getAllConnectedRelation(x, y, my_color) 
                if board.isForbidden(relations):
                    rm_pos.append((x,y))
                board.rollback(x, y, my_color)
            for pos in rm_pos:
                possible_pos.remove(pos)
        # 판이 다 찬 경우 & 금수만 가능한 경우
        if len(possible_pos) == 0:
            score = self.getScore(board, my_color)
            return score, None, None

        if my_turn: 
            score = -1
            pos_x = None
            pos_y = None
            for x, y in possible_pos:
                new_board = deepcopy(board)
                new_board.put(x, y, my_color)
                tmp_score, _, _ = self.minmax(depth-1, alpha, beta, new_board, my_color, not my_turn)

                if score < tmp_score:
                    score = tmp_score
                    pos_x = x
                    pos_y = y
                
                if score > alpha:
                    alpha = score
                if beta <= alpha:
                    break
            return score, pos_x, pos_y
        else:
            score = self.win_score
            pos_x = None
            pos_y = None
            for x, y in possible_pos:
                new_board = deepcopy(board)
                new_board.put(x, y, my_color)
                tmp_score, _, _ = self.minmax(depth-1, alpha, beta, new_board, my_color, not my_turn)

                if score > tmp_score:
                    score = tmp_score
                    pos_x = x
                    pos_y = y

                if score < beta:
                    beta = score
                if beta <= alpha:
                    break
            return score, pos_x, pos_y

    def searchWinPos(self, board, my_color):
        # 주변에 stone이 있는 empty 좌표
        possible_pos = board.getColorPos(-1)  # empty 좌표들
        rm_pos = []
        for x, y in possible_pos:
            if not board.hasNearStone(x, y):
                rm_pos.append((x, y))
        for pos in rm_pos:
            possible_pos.remove(pos)

        # 흑돌인 경우 금수 위치 제거
        if my_color == 0:
            rm_pos = []
            for x, y in possible_pos:
                board.put(x, y, my_color)
                relations = board.getAllConnectedRelation(x, y, my_color) 
                if board.isForbidden(relations):
                    rm_pos.append((x,y))
                board.rollback(x, y, my_color)
            for pos in rm_pos:
                possible_pos.remove(pos)

        for x, y in possible_pos:
            new_board = deepcopy(board)
            new_board.put(x, y, my_color)
            if self.getScore(new_board, my_color) >= self.win_score:
                return x, y
        return None, None


# if __name__ == '__main__':
#     board = Board()
#     depth = 3
#     board.board_status[7][7] = 0
#     # board.board_status[7][8] = 1
#     # board.board_status[6][9] = 
#     my_color = 1
#     my_turn = True
#     ai = MinMax()
#     score, pos_x, pos_y = ai.minmax(depth, -1, ai.win_score, board, my_color, my_turn)
#     if pos_x == None and pos_y == None:
#         pos_x = 7
#         pos_y = 7
#     print("+++ board +++")
#     board.put(pos_x, pos_y, my_color)
#     board.draw()
#     print("============")
#     print(pos_x, pos_y)
