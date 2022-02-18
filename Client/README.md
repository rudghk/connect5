# 오목 게임

## 게임 설명
### 게임 실행
- main.py를 통해 게임 실행
### 게임 룰 
- 15x15로 0 ~ 14 범위 사용
  - 사람의 경우 마우스 클릭을 통해 입력
- (흑/백) 이미 놓은 위치, 판 범위 벗어나는 수 => 패
- (흑) 돌이 연속된 3x3 또는 4x4 => 패
- (흑/백) 오목 완성 => 승
- (백) 장목 완성 => 승
- (흑) 장목 완성 => 승리도 패배도 아님
### Single mode
- Human(흑) vs Human(백)
- Human(흑) vs AI(백)
- AI(흑) vs Human(백)
- AI(흑) vs AI(백)
### Online mode(서버 필요)
- Human vs Human : 사람으로 게임에 참여
- Human vs AI : 사람으로 게임에 참여
- AI vs Human : AI로 게임에 참여
- AI vs AI : AI로 게임에 참여
