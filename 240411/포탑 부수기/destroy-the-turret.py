import heapq
import sys
from collections import deque

# sys.stdin = open("input6.txt", "r")
input = sys.stdin.readline
N, M, K = map(int, input().rstrip().split())
board = [[0 for j in range(M + 1)] for i in range(N + 1)]
# (dist, preI, preJ)
dist = [[(0, 0, 0) for j in range(M + 1)] for i in range(N + 1)]

# 가장 최근에 공격한 시기
attackTurnBoard = [[0 for j in range(M + 1)] for i in range(N + 1)]
# 가장 최근에 공격당한 시기
attackedTurnBoard = [[0 for j in range(M + 1)] for i in range(N + 1)]

canonDI = [0, 1, -1, 0, 1, 1, -1, -1]
canonDJ = [1, 0, 0, -1, 1, -1, 1, -1]
# 우하상좌
di = [0, 1, -1, 0]
dj = [1, 0, 0, -1]
for i in range(1, N + 1):
    row = list(map(int, input().rstrip().split()))
    for j in range(1, M + 1):
        board[i][j] = row[j - 1] if row[j - 1] > 0 else 0
        # 부서진 포탑 기록


class CmpWeak:
    def __init__(self, attack_ability, attack_turn, pos_sum, j):
        self.attackAbility = attack_ability
        self.attackTurn = attack_turn
        self.posSum = pos_sum
        self.j = j

    def __lt__(self, other):
        if self.attackAbility == other.attackAbility:
            if self.attackTurn == other.attackTurn:
                if self.posSum == other.posSum:
                    return self.j > other.j

                return self.posSum > other.posSum

            return self.attackTurn > other.attackTurn

        return self.attackAbility < other.attackAbility


class CmpStrong:
    def __init__(self, attack_ability, attack_turn, pos_sum, j):
        self.attackAbility = attack_ability
        self.attackTurn = attack_turn
        self.posSum = pos_sum
        self.j = j

    def __lt__(self, other):
        if self.attackAbility == other.attackAbility:
            if self.attackTurn == other.attackTurn:
                if self.posSum == other.posSum:
                    return self.j < other.j

                return self.posSum < other.posSum

            return self.attackTurn < other.attackTurn

        return self.attackAbility > other.attackAbility


def print_board():
    for i in range(1, N + 1):
        for j in range(1, M + 1):
            print(board[i][j], end=" ")
        print()


def select_attacker():
    h = []
    for i in range(1, N + 1):
        for j in range(1, M + 1):
            if board[i][j] <= 0: continue
            heapq.heappush(h, CmpWeak(board[i][j], attackTurnBoard[i][j], i + j, j))
    weakest = heapq.heappop(h)
    weakest_pos = (weakest.posSum - weakest.j, weakest.j)
    return weakest_pos


def select_attackee(attacker_pos):
    h = []
    for i in range(1, N + 1):
        for j in range(1, M + 1):
            if (i, j) == attacker_pos: continue
            heapq.heappush(h, CmpStrong(board[i][j], attackTurnBoard[i][j], i + j, j))
    strongest = heapq.heappop(h)
    strongest_pos = (strongest.posSum - strongest.j, strongest.j)
    return strongest_pos


def oob_i(ci):
    if ci <= 0 or ci > N: return True
    return False
def oob_j(cj):
    if cj <= 0 or cj > M: return True
    return False

def init_dist():
    for i in range(1, N + 1):
        for j in range(1, M + 1):
            dist[i][j] = (0, 0, 0)

def laser(attacker_pos, attackee_pos, turn):
    Q = deque()
    Q.append(attackerPos)
    init_dist()
    dist[attackerPos[0]][attackerPos[1]] = (1, 0, 0)
    attack_ability = board[attacker_pos[0]][attacker_pos[1]]
    while Q:
        ci, cj = Q.popleft()
        for k in range(4):
            ni, nj = ci + di[k], cj + dj[k]

            if oob_i(ni):
                ni = ni % N if ni > 0 else N
            if oob_j(nj):
                nj = nj % M if nj > 0 else M
            # 부서진 포탑이 있는 곳은 못 가
            if board[ni][nj] <= 0: continue
            # 이미 갔던 곳도 안돼 이건 당연
            if dist[ni][nj][0] > 0: continue

            dist[ni][nj] = (dist[ci][cj][0] + 1, ci, cj)
            Q.append((ni, nj))
            if (ni, nj) == attackee_pos:
                # 가는 길에 있던 포탑들은 1/2만큼 까임
                pre_i, pre_j = dist[ni][nj][1], dist[ni][nj][2]
                while (pre_i, pre_j) != attacker_pos:
                    board[pre_i][pre_j] -= attack_ability // 2
                    attackedTurnBoard[pre_i][pre_j] = turn
                    # print(f"{(pre_i, pre_j)}에서 레이저 지나가는 길이어서 {attack_ability//2}만큼 까임")
                    pre_i, pre_j = dist[pre_i][pre_j][1], dist[pre_i][pre_j][2]
                # attacker의 공격력만큼 까임
                board[ni][nj] -= attack_ability
                attackedTurnBoard[ni][nj] = turn
                # 공격에 성공
                attackTurnBoard[attacker_pos[0]][attacker_pos[1]] = turn
                return True
    # 공격에 실패
    return False




def canon(attacker_pos, attackee_pos, turn):
    # 공격하기
    attack_ability = board[attacker_pos[0]][attacker_pos[1]]
    board[attackee_pos[0]][attackee_pos[1]] -= attack_ability
    attackTurnBoard[attacker_pos[0]][attacker_pos[1]] = turn
    attackedTurnBoard[attackee_pos[0]][attackee_pos[1]] = turn
    # 주변부 폭격
    for k in range(8):
        ni, nj = attackee_pos[0] + canonDI[k], attackee_pos[1] + canonDJ[k]

        if oob_i(ni):
            ni = ni % N if ni > 0 else N
        if oob_j(nj):
            nj = nj % M if nj > 0 else M
        # 공격자는 폭격에서 영향을 안 받는다
        if (ni, nj) == attacker_pos: continue

        # 이미 부서진 거는 볼 필요가 없다
        if board[ni][nj] <= 0: continue
        # 절반만 까준다
        board[ni][nj] -= attack_ability // 2
        attackedTurnBoard[ni][nj] = turn

def break_towers():
    for i in range(1, N + 1):
        for j in range(1, M + 1):
            if board[i][j] <= 0:
                board[i][j] = 0

def count_unbroken_towers():
    cnt = 0
    for i in range(1, N + 1):
        for j in range(1, M + 1):
            if board[i][j] > 0:
                cnt += 1
    return cnt

def print_strongest_attack_ability():
    maxAttackAbility = -1
    pos = (0, 0)
    for i in range(1, N + 1):
        for j in range(1, M + 1):
            if board[i][j] > maxAttackAbility:
                maxAttackAbility = board[i][j]
                pos = (i, j)
    print(f"현재 {pos}에서 {maxAttackAbility}로 가장 높은 공격력을 갖고 있다.")

for turn in range(1, K + 1):
    attackerPos = select_attacker()
    # 공격력 추가
    board[attackerPos[0]][attackerPos[1]] += (N + M)
    attackeePos = select_attackee(attackerPos)
    # print()
    # print(f"{attackerPos}에서 {attackeePos}로 공격합니다. 공격력: {board[attackerPos[0]][attackerPos[1]]}")
    # 레이저 공격에 실패하면은
    if not laser(attackerPos, attackeePos, turn):
        # 폭격으로 공격
        # print("폭격했음")
        canon(attackerPos, attackeePos, turn)
    break_towers()
    # 안 부서진 포탑이 1개가 되면 게임 바로 종료
    if count_unbroken_towers() == 1:
        break

    # print("-" * 64)
    # print(f"{turn}턴 공격후: 재정비 전")
    print_board()
    # 포탑 재정비
    for i in range(1, N + 1):
        for j in range(1, M + 1):
            if board[i][j] <= 0: continue
            if attackedTurnBoard[i][j] == turn or attackTurnBoard[i][j] == turn:
                continue
            board[i][j] += 1
    # print("-" * 64)
    # print(f"{turn}턴 공격후: 재정비 후")
    print_board()
    print_strongest_attack_ability()



maxAttackAbility = -1
for i in range(1, N + 1):
    for j in range(1, M + 1):
        if board[i][j] > maxAttackAbility:
            maxAttackAbility = board[i][j]
print(maxAttackAbility)