from copy import deepcopy
from math import trunc

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
            if open == 2: return base_score*2
            else: return 200
        if count == 3:
            if open == 2: return base_score/10
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
        cur_turn_color = my_color if my_turn else (my_color+1) % 2
        if depth == 0:
            score = self.getScore(board, cur_turn_color)
            return score, None, None    # score, x, y
        
        # 주변에 내 돌이 있는 empty 좌표
        candidate_pos = board.getColorPos(-1)  # empty 좌표들
        possible_pos = []
        for x, y in candidate_pos:
            if board.hasNearStone(x, y, cur_turn_color):
                possible_pos.append((x, y))

        # 흑돌인 경우 금수 위치 제거
        if cur_turn_color == 0:
            rm_pos = []
            for x, y in possible_pos:
                board.put(x, y, cur_turn_color)
                relations = board.getAllConnectedRelation(x, y, cur_turn_color) 
                if board.isForbidden(relations):
                    rm_pos.append((x,y))
                board.rollback(x, y, cur_turn_color)
            for pos in rm_pos:
                possible_pos.remove(pos)
        # 판이 다 찬 경우 & 금수만 가능한 경우
        if len(possible_pos) == 0:
            score = self.getScore(board, cur_turn_color)
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
            other_color = (my_color+1)%2
            for x, y in possible_pos:
                new_board = deepcopy(board)
                new_board.put(x, y, other_color)
                tmp_score, _, _ = self.minmax(depth-1, alpha, beta, new_board, other_color, not my_turn)

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
       # 주변에 내 돌이 있는 empty 좌표
        candidate_pos = board.getColorPos(-1)  # empty 좌표들
        possible_pos = []
        for x, y in candidate_pos:
            if board.hasNearStone(x, y, my_color):
                possible_pos.append((x, y))

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
            board.put(x, y, my_color)
            score = self.getScore(board, my_color)
            board.rollback(x, y, my_color)
            if score >= self.win_score:
                return x, y 
        return None, None

    def calDefenceScore(self, board, x, y, my_color, score):
        board.put(x, y, my_color)
        tmp_score = self.getScore(board, my_color)
        board.rollback(x, y, my_color)
        if tmp_score > score:
            score = tmp_score
        return score

    def searchDefencePos(self, board, my_color):
        other_color = (my_color+1)%2
        other_pos = board.getColorPos(other_color)
        all_relations = []
        c3open2 = []
        c2open2 = []
        pos_idx = 0
        for x, y in other_pos:
            relations = board.getAllConnectedRelation(x, y, other_color) 
            all_relations.append(relations)
            for dir_type in range(len(relations)):
                count, start_x, start_y, open = relations[dir_type]
                # _oooox (_:open, x: o와 다른 색)
                if count == 4 and open == 1:
                    left_x, left_y, right_x, right_y = board.getLeftRightxy(count, start_x, start_y, dir_type)
                    print(left_x, left_y, right_x, right_y)
                    if not board.isOutOfRange(left_x, left_y):
                        if board.board_status[left_x][left_y] == my_color:
                            return right_x, right_y
                        else:
                            return left_x, left_y
                elif count == 3 and open == 2:
                    c3open2.append((pos_idx, dir_type))
                elif count == 2 and open == 2:
                    c2open2.append((pos_idx, dir_type))
            pos_idx += 1
        
        score = 0
        pos_x = None
        pos_y = None
        # _oo_o* (_: open, *:_ or o)
        for pos_idx, dir_type in c2open2:
            count, start_x, start_y, open = all_relations[pos_idx][dir_type]
            left_x, left_y, right_x, right_y = board.getLeftRightxy(count, start_x, start_y, dir_type)
            tmp_x1, tmp_y1, tmp_x2, tmp_y2 = board.getLeftRightxy(count+2, left_x, left_y, dir_type)
            if not board.isOutOfRange(tmp_x1, tmp_y1) and board.board_status[tmp_x1][tmp_y1] == other_color:
                tmp_x, tmp_y, _, _ = board.getLeftRightxy(1, tmp_x1, tmp_y1, dir_type)
                if not board.isOutOfRange(tmp_x, tmp_y) and board.board_status[tmp_x][tmp_y] != my_color:
                    tmp_score = self.calDefenceScore(board, left_x, left_y, my_color, score)
                    if tmp_score > score:
                        score = tmp_score
                        pos_x = left_x
                        pos_y = left_y
            elif not board.isOutOfRange(tmp_x2, tmp_y2) and board.board_status[tmp_x2][tmp_y2] == other_color:
                _, _, tmp_x, tmp_y = board.getLeftRightxy(1, tmp_x2, tmp_y2, dir_type)
                if not board.isOutOfRange(tmp_x, tmp_y) and board.board_status[tmp_x][tmp_y] != my_color:
                    tmp_score = self.calDefenceScore(board, right_x, right_y, my_color, score)
                    if tmp_score > score:
                        score = tmp_score
                        pos_x = right_x
                        pos_y = right_y
        # _ooo_ 
        for pos_idx, dir_type in c3open2:
            count, start_x, start_y, open = all_relations[pos_idx][dir_type]
            left_x, left_y, right_x, right_y = board.getLeftRightxy(count, start_x, start_y, dir_type)
            tmp_score = self.calDefenceScore(board, left_x, left_y, my_color, score)
            if tmp_score > score:
                score = tmp_score
                pos_x = left_x
                pos_y = left_y
            tmp_score = self.calDefenceScore(board, right_x, right_y, my_color, score)
            if tmp_score > score:
                score = tmp_score
                pos_x = right_x
                pos_y = right_y

        if score != 0:
            return pos_x, pos_y
        return None, None
