import sys
from collections import deque

# sys.stdin = open("input1.txt", "r")
input = sys.stdin.readline
DEBUG = print


def oob(i, j):
    if i <= 0 or i > L: return True
    if j <= 0 or j > L: return True
    return False


class Knight:
    def __init__(self, idx=0, pos=(0, 0), h=0, w=0, hp=0):
        self.idx = idx
        self.pos = pos
        self.h = h
        self.w = w
        self.hp = hp
        self.retired = False
        self.damagedMount = 0
        self.movedWhen = 0
        ci, cj = pos
        for i in range(ci, ci + h):
            for j in range(cj, cj + w):
                kBoard[i][j] = idx

    def update_pos(self, new_pos):
        pass

    def check_any_wall_in_board(self, new_anchor):
        ci, cj = new_anchor
        for i in range(ci, ci + self.h):
            for j in range(cj, cj + self.w):
                # oob도 벽 취급
                if oob(i, j): return True
                if board[i][j] == 2: return True
        return False

    def check_any_other_knight(self, new_anchor):
        ret_knight_idx_set = set()
        ci, cj = new_anchor
        for i in range(ci, ci + self.h):
            for j in range(cj, cj + self.w):
                if kBoard[i][j] > 0 and kBoard[i][j] != self.idx:
                    ret_knight_idx_set.add(kBoard[i][j])
        return ret_knight_idx_set

    def clear_cur_pos_in_kBoard(self):
        ci, cj = self.pos
        for i in range(ci, ci + self.h):
            for j in range(cj, cj + self.w):
                kBoard[i][j] = 0

    def update_by_new_anchor_in_kBoard(self, new_anchor):
        ci, cj = new_anchor
        for i in range(ci, ci + self.h):
            for j in range(cj, cj + self.w):
                kBoard[i][j] = self.idx

    def can_move(self, d):
        q = deque()
        dist = [[0 for j in range(L + 1)] for i in range(L + 1)]
        q.append(self.pos)
        dist[self.pos[0]][self.pos[1]] = 1
        while q:
            ci, cj = q.popleft()
            for k in range(4):
                ni, nj = ci + DI[k], cj + DJ[k]
                if oob(ni, nj):
                    # 방향이 d이랑 일치한다면 oob도 벽 취급
                    if k == d: return False
                    continue
                # d 방향일 때 다음 칸이 벽이라면 못 움직인다
                if k == d and board[ni][nj] == 2: return False
                if kBoard[ni][nj] <= 0: continue
                if dist[ni][nj] > 0: continue

                dist[ni][nj] = dist[ci][cj] + 1
                q.append((ni, nj))

        return True

    def move(self, d, turn):
        # 이미 체스판 밖에 있는 기사에게 명령을 내려도 의미가 없음
        if self.retired: return False
        ci, cj = self.pos
        new_anchor = ci + DI[d], cj + DJ[d]
        # 새로운 anchor 좌표가 OOB인지 확인 (base condition #1)
        if oob(new_anchor[0], new_anchor[1]): return False
        # 이동하려는 칸에 벽(은 oob도 포함이다)이 하나라도 있는지 확인 (base condition #2)
        if self.check_any_wall_in_board(new_anchor): return False
        # 이동하려는 곳에 벽도 없다면, 딴 기사가 점유하고 있는지 확인
        knight_list = list(self.check_any_other_knight(new_anchor))
        knight_list.sort()
        # 점유 하고 있는 딴 기사가 없다면 (base condition #3)
        if len(knight_list) <= 0:
            self.clear_cur_pos_in_kBoard()
            self.update_by_new_anchor_in_kBoard(new_anchor)
            # self.pos 업데이트
            self.pos = new_anchor
            # 옮겨진 turn도 기록
            self.movedWhen = turn
            return True

        # 점유 중인 딴 기사들이 있다면 (recrusion trigger)
        for k_idx in knight_list:
            knights[k_idx].move(d, turn)

        self.clear_cur_pos_in_kBoard()
        self.update_by_new_anchor_in_kBoard(new_anchor)
        # self.pos 업데이트
        self.pos = new_anchor
        # 옮겨진 turn 기록
        self.movedWhen = turn
        return True

    def get_damage(self, turn):
        if self.movedWhen != turn: return
        ci, cj = self.pos
        cnt = 0
        for i in range(ci, ci + self.h):
            for j in range(cj, cj + self.w):
                if board[i][j] == 1:
                    cnt += 1
        self.hp -= cnt
        self.damagedMount += cnt
        # hp가 0이하면 retired
        if self.hp <= 0:
            ci, cj = self.pos
            for i in range(ci, ci + self.h):
                for j in range(cj, cj + self.w):
                    kBoard[i][j] = 0

            self.pos = (0, 0)
            self.h = 0
            self.w = 0
            self.hp = 0
            self.retired = True

    def __str__(self):
        return f"idx: {self.idx}, pos: {self.pos}, h: {self.h}, w: {self.w}, hp: {self.hp}, retired: {self.retired}, damagedMount: {self.damagedMount}, movedWhen: {self.movedWhen}"


def DEBUG_board():
    print("board:")
    for i in range(1, L + 1):
        for j in range(1, L + 1):
            print(board[i][j], end=" ")
        print()


def DEBUG_kBoard():
    print("knight board:")
    for i in range(1, L + 1):
        for j in range(1, L + 1):
            print(kBoard[i][j], end=" ")
        print()


# 위쪽, 오른쪽, 아래쪽, 왼쪽
DI = [-1, 0, 1, 0]
DJ = [0, 1, 0, -1]
L, N, Q = map(int, input().rstrip().split())
board = [[0 for j in range(L + 1)] for i in range(L + 1)]
for i in range(1, L + 1):
    row = list(map(int, input().rstrip().split()))
    for j in range(1, L + 1):
        board[i][j] = row[j - 1]
kBoard = [[0 for j in range(L + 1)] for i in range(L + 1)]
knights = [Knight()]
# 처음에는 서로 board에서 안 겹치게 unique하게 주어진다
for i in range(1, N + 1):
    r, c, h, w, k = map(int, input().rstrip().split())
    knights.append(Knight(i, (r, c), h, w, k))

for q in range(1, Q + 1):
    # DEBUG(f"{q}번 명령 수행전 :")
    # DEBUG("-" * 64)
    # DEBUG_board()
    # DEBUG("-" * 64)
    # DEBUG_kBoard()
    knightIdx, kDir = map(int, input().rstrip().split())
    # 기사가 이동하려는 방향 끝에 벽이 있는지 없는지 확인
    if knights[knightIdx].can_move(kDir):
        knights[knightIdx].move(kDir, q)
        # DEBUG(f"{q}번 이동후 :")
        # DEBUG_kBoard()
        for idx in range(1, N + 1):
            if idx == knightIdx: continue
            knights[idx].get_damage(q)
    # DEBUG(f"{q}번 명령 수행후 :")
    # DEBUG("-" * 64)
    # DEBUG_board()
    # DEBUG("-" * 64)
    # DEBUG_kBoard()
    # for knight in knights[1:]:
    #     DEBUG(knight)

ans = 0
for knight in knights[1:]:
    if knight.retired: continue
    ans += knight.damagedMount
print(ans)