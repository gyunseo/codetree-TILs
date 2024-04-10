import heapq
import sys

# sys.stdin = open("input12.txt", "r")
input = sys.stdin.readline
N, M, P, C, D = map(int, input().rstrip().split())
rPos = tuple(map(int, input().rstrip().split()))
sPoses = [(0, 0) for _ in range(P + 1)]
scores = [0 for _ in range(P + 1)]
isRetired = [False for _ in range(P + 1)]
isStunned = [False for _ in range(P + 1)]
wakeUpTurn = [0 for _ in range(P + 1)]
rBoard = [[0 for j in range(N + 1)] for i in range(N + 1)]
sBoard = [[0 for j in range(N + 1)] for i in range(N + 1)]
# (충돌유무, 방향, force)
collision = [[(False, (0, 0), 0) for j in range(N + 1)] for i in range(N + 1)]
rdi = [-1, 0, 1, 0, -1, -1, 1, 1]
rdj = [0, 1, 0, -1, 1, -1, 1, -1]
di = [-1, 0, 1, 0]
dj = [0, 1, 0, -1]
for _ in range(P):
    sIdx, sI, sJ = map(int, input().rstrip().split())
    sPoses[sIdx] = (sI, sJ)
    sBoard[sI][sJ] = sIdx

rBoard[rPos[0]][rPos[1]] = 1


# print(f"루돌프 초기 위치: {rPos}")
# print("산타들의 초기 위치:", end=" ")
# print(sPoses[1:])
# print("-" * 64)


class CmpSanta:
    def __init__(self, dist, ci, cj, sIdx):
        self.dist = dist
        self.ci = ci
        self.cj = cj
        self.sIdx = sIdx

    def __lt__(self, other):
        if self.dist < other.dist:
            return True
        if self.dist == other.dist:
            if self.ci == other.ci:
                return self.cj > other.cj
            return self.ci > other.ci
        return False


def r_move():
    """
    루돌프가 움직인다
    """
    global rPos
    h = []
    # 가장 가까운 산타를 선택한다
    for i in range(1, P + 1):
        if isRetired[i]: continue
        cSantaI, cSantaJ = sPoses[i]
        minDist = (rPos[0] - cSantaI) ** 2 + (rPos[1] - cSantaJ) ** 2
        heapq.heappush(h, CmpSanta(minDist, cSantaI, cSantaJ, i))
    # 가장 가까운 산타를 하나 뽑는다
    closest = heapq.heappop(h)
    closestI, closestJ, closestIdx = closest.ci, closest.cj, closest.sIdx
    # print(f"가장 가까운 선택한 산타: {closestIdx}, 위치: {closestI, closestJ}")
    # 10억이면 MAX로 충분
    minDist = int(1e9)
    # 루돌프가 움직일 방향
    rDir = (0, 0)
    for k in range(8):
        ni, nj = rPos[0] + rdi[k], rPos[1] + rdj[k]
        if oob(ni, nj): continue
        tmpDist = (ni - closestI) ** 2 + (nj - closestJ) ** 2
        if tmpDist < minDist:
            minDist = tmpDist
            rDir = (rdi[k], rdj[k])
    # print(f"가장 가까운 선택한 산타로 가기 위해 선택한 방향: {rDir}")
    # 루돌프 보드에서 원래 위치에서 새로 이사 갈 위치로 표시를 해준다
    nRI, nRJ = rPos[0] + rDir[0], rPos[1] + rDir[1]
    rBoard[rPos[0]][rPos[1]] = 0
    rBoard[nRI][nRJ] = 1

    # 충돌 검사를 해준다
    # 어떤 산타가 있다면
    # 루돌프가 온 방향으로 산타는 쭉 밀려나야 한다
    if sBoard[nRI][nRJ]:
        collision[nRI][nRJ] = (True, rDir, C)

    rPos = (nRI, nRJ)


def oob(i, j):
    if i <= 0 or i > N: return True
    if j <= 0 or j > N: return True
    return False


def interact(sIdx, vec):
    # 산타의 현재 위치
    ci, cj = sPoses[sIdx]
    # 산타의 다음 위치
    ni, nj = ci + vec[0], cj + vec[1]

    # 보드밖이면 base condition1
    if oob(ni, nj):
        sBoard[ci][cj] = 0
        sPoses[sIdx] = (0, 0)
        # 리타이어 이외에는 다 초기값으로 설정해 준다
        isRetired[sIdx] = True
        isStunned[sIdx] = False
        wakeUpTurn[sIdx] = 0
        return
    # 다음으로 가는 곳이 아무 산타도 없다면 base condition2
    if sBoard[ni][nj] == 0:
        sBoard[ci][cj] = 0
        sBoard[ni][nj] = sIdx
        sPoses[sIdx] = (ni, nj)
        return
    # 다음으로 가는 곳에 딴 산타가 있다면
    nSIdx = sBoard[ni][nj]
    interact(nSIdx, vec)
    sBoard[ci][cj] = 0
    sBoard[ni][nj] = sIdx
    sPoses[sIdx] = (ni, nj)


def collide(turn):
    """
    collision board를 탐색해서 collide를 검사하고, 상호작용을 일으킨다.
    """
    for i in range(1, N + 1):
        for j in range(1, N + 1):
            if collision[i][j][0]:
                # 일단 부딪혔으니깐 점수를 준다
                sIdx, vec, force = sBoard[i][j], collision[i][j][1], collision[i][j][2]
                # 현재 산타의 위치
                cSI, cSJ = sPoses[sIdx][0], sPoses[sIdx][1]
                # 점수 계산
                scores[sIdx] += collision[i][j][2]
                # 포물선으로 날라갈 지점
                nSI, nSJ = cSI + vec[0] * force, cSJ + vec[1] * force
                # 리타이어된다면
                if oob(nSI, nSJ):
                    sBoard[cSI][cSJ] = 0
                    sPoses[sIdx] = (0, 0)
                    # 리타이어 이외에는 다 초기값으로 설정해 준다
                    isRetired[sIdx] = True
                    isStunned[sIdx] = False
                    wakeUpTurn[sIdx] = 0
                    continue
                # 상호작용이 일어나야 함
                if sBoard[nSI][nSJ]:
                    nSIdx = sBoard[nSI][nSJ]
                    # 상호작용이 시작되는 산타와 방향을 매개 변수로 전달
                    interact(nSIdx, vec)

                # 산타 보드 업데이트
                sBoard[cSI][cSJ] = 0
                sBoard[nSI][nSJ] = sIdx

                # sPoses 업데이트
                sPoses[sIdx] = (nSI, nSJ)

                # isStunned 업데이트
                isStunned[sIdx] = True
                wakeUpTurn[sIdx] = turn + 2


def s_move(sIdx):
    # 기절했거나 탈락한 산타는 제외
    if isStunned[sIdx] or isRetired[sIdx]: return
    cSI, cSJ = sPoses[sIdx]
    # 산타의 현 위치에서 루돌프까지의 거리
    minDistFromR = (rPos[0] - cSI) ** 2 + (rPos[1] - cSJ) ** 2
    sDir = (0, 0)
    for k in range(4):
        ni, nj = cSI + di[k], cSJ + dj[k]
        if oob(ni, nj): continue
        if sBoard[ni][nj]: continue
        tmpDist = (rPos[0] - ni) ** 2 + (rPos[1] - nj) ** 2
        if tmpDist < minDistFromR:
            minDistFromR = tmpDist
            sDir = (di[k], dj[k])
    # 산타는 가까워질 수거 없거나, 움직일 수 있는 칸이 없다면 안 움직일 수도 있다
    if sDir == (0, 0): return
    # 가까워지는 칸을 발견했다면
    nSI, nSJ = cSI + sDir[0], cSJ + sDir[1]

    # 산타 보드에서 이동을 하는데, 루돌프랑 부딪힌다면
    if rBoard[nSI][nSJ]:
        collision[nSI][nSJ] = (True, (-sDir[0], -sDir[1]), D)

    sBoard[cSI][cSJ] = 0
    sBoard[nSI][nSJ] = sIdx
    sPoses[sIdx] = (nSI, nSJ)


def clear_collision():
    for i in range(1, N + 1):
        for j in range(1, N + 1):
            if collision[i][j][0]:
                collision[i][j] = (False, (0, 0), 0)


def wake_up(turn):
    for i in range(1, P + 1):
        if isStunned[i] and wakeUpTurn[i] == turn:
            isStunned[i] = False
            wakeUpTurn[i] = 0


def print_board():
    print("rBoard:")
    for i in range(1, N + 1):
        for j in range(1, N + 1):
            print(rBoard[i][j], end=" ")
        print()
    print("sBoard:")
    for i in range(1, N + 1):
        for j in range(1, N + 1):
            print(sBoard[i][j], end=" ")
        print()


for turn in range(1, M + 1):
    # print(f"{turn}턴 시작 전:")
    # print_board()
    game_end = True
    wake_up(turn)
    r_move()
    collide(turn)
    clear_collision()
    for i in range(1, P + 1):
        s_move(i)
        collide(turn)
        clear_collision()
    # 아직 리타이어 당하지 않은 산타들은 1점씩 얻는다
    for i in range(1, P + 1):
        if not isRetired[i]:
            game_end = False
            scores[i] += 1
    if game_end:
        break
    # print(f"{turn}턴 종료 후:")
    # print_board()

for i, score in enumerate(scores):
    if i == 0: continue
    print(score, end=" ")
print()