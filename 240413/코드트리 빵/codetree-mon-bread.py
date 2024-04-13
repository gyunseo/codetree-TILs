import heapq
from collections import deque

# sys.stdin = open("input5.txt", "r")

DEBUG = print


def OOB(i, j):
    if i <= 0 or i > n: return True
    if j <= 0 or j > n: return True
    return False


class CmpPos:
    def __init__(self, dist, i, j):
        self.dist = dist
        self.i = i
        self.j = j

    def __lt__(self, other):
        if self.dist == other.dist:
            if self.i == other.i:
                return self.j < other.j
            return self.i < other.i
        return self.dist < other.dist


class Person:
    def __init__(self, index=0, target_pos=(0, 0)):
        self.index = index
        self.curPos = (0, 0)
        self.targetPos = target_pos
        self.visitedTarget = False
        self.inOfBound = False

    def move(self):
        if not self.inOfBound: return
        if self.visitedTarget: return
        ci, cj = self.curPos
        h = []
        for k in range(4):
            ni, nj = ci + DI[k], cj + DJ[k]
            if OOB(ni, nj): continue
            if isVisited[ni][nj]: continue
            tmp_dist = abs(ni - self.targetPos[0]) + abs(nj - self.targetPos[1])
            heapq.heappush(h, CmpPos(tmp_dist, ni, nj))
        closest = heapq.heappop(h)
        self.curPos = closest.i, closest.j

    def make_target_pos_unreachable(self):
        if self.curPos == self.targetPos:
            isVisited[self.curPos[0]][self.curPos[1]] = True
            self.visitedTarget = True

    def check_reachable_with_dist(self, base_camp_pos):
        q = deque()
        q.append(base_camp_pos)
        dist = [[0 for j in range(n + 1)] for i in range(n + 1)]
        dist[base_camp_pos[0]][base_camp_pos[1]] = 1
        while q:
            ci, cj = q.popleft()
            for k in range(4):
                ni, nj = ci + DI[k], cj + DJ[k]
                if OOB(ni, nj): continue
                if isVisited[ni][nj] or dist[ni][nj] > 0: continue
                dist[ni][nj] = dist[ci][cj] + 1
                q.append((ni, nj))

        return dist[self.targetPos[0]][self.targetPos[1]]

    def go_to_basecamp(self):
        if self.inOfBound: return
        if self.visitedTarget: return
        # choose the closest basecamp
        h = []
        for base_camp_pos in baseCampPoses:
            bsc_i, bsc_j = base_camp_pos
            # 이미 isVisited된 거는 패스해야 된다.
            if isVisited[bsc_i][bsc_j]: continue
            tmp_dist = self.check_reachable_with_dist(base_camp_pos)
            if tmp_dist <= 0: continue
            heapq.heappush(h, CmpPos(tmp_dist, bsc_i, bsc_j))
        closest = heapq.heappop(h)
        # 사람의 현재 위치 갱신
        self.curPos = (closest.i, closest.j)
        # 이제 board안으로 들어왔음을 갱신
        self.inOfBound = True
        # 해당 베이스 캠프는 isVisited됐음을 갱신
        isVisited[closest.i][closest.j] = True

    def __str__(self):
        return f"idx: {self.index}, curPos: {self.curPos}, targetPos: {self.targetPos}, visitedTarget: {self.visitedTarget}"


def DEBUG_board():
    print("-" * 64)
    print("board:")
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            print(board[i][j], end=" ")
        print()


def DEBUG_isVisited():
    print("-" * 64)
    print("isVisited:")
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            print(isVisited[i][j], end=" ")
        print()


def DEBUG_persons():
    print("-" * 64)
    print("persons:")
    for person in persons[1:]:
        print(person)


DI = (-1, 0, 0, 1)
DJ = (0, -1, 1, 0)
n, m = map(int, input().rstrip().split())
board = [[0 for j in range(n + 1)] for i in range(n + 1)]
isVisited = [[False for j in range(n + 1)] for i in range(n + 1)]
baseCampPoses = []
persons = [Person()]
for i in range(1, n + 1):
    row = list(map(int, input().rstrip().split()))
    for j in range(1, n + 1):
        board[i][j] = row[j - 1]
        if board[i][j] == 1:
            baseCampPoses.append((i, j))
for i in range(1, m + 1):
    targetI, targetJ = map(int, input().rstrip().split())
    persons.append(Person(i, (targetI, targetJ)))

# DEBUG_board()

timer = 1
while True:
    # DEBUG(f"{timer}분 이동 전: ")
    # DEBUG_isVisited()
    # DEBUG_persons()
    for idx in range(1, m + 1):
        persons[idx].move()

    for idx in range(1, m + 1):
        persons[idx].make_target_pos_unreachable()

    if timer <= m:
        persons[timer].go_to_basecamp()

    # 모든 사람이 target에 도착했는지 확인하는 코드
    game_end = True
    for idx in range(1, m + 1):
        if not persons[idx].visitedTarget:
            game_end = False
            break

    if game_end:
        break
    # DEBUG(f"{timer}분 이동 후: ")
    # DEBUG_isVisited()
    # DEBUG_persons()
    timer += 1

# DEBUG("-" * 64)
# for person in persons[1:]:
#     DEBUG(person)
print(timer)