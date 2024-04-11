import heapq
import sys

# sys.stdin = open("input1.txt", "r")
input = sys.stdin.readline
DEBUG = print

# "상하"좌우
DI = [-1, 1, 0, 0]
DJ = [0, 0, -1, 1]


def oob(ci, cj):
    if ci <= 0 or ci > N: return True
    if cj <= 0 or cj > N: return True
    return False


class Runner:
    def __init__(self, pos=(0, 0), running_dist=0, exited=False):
        self.pos = pos
        self.runningDist = running_dist
        self.exited = exited
        self.matrix = [[0 for j in range(N + 1)] for i in range(N + 1)]

    def update_pos(self, c_pos, n_pos):
        ci, cj = c_pos
        ni, nj = n_pos
        self.matrix[ci][cj] = 0
        self.matrix[ni][nj] = 1

        self.pos = (ni, nj)

    def move(self):
        """
        움직였다면 옮긴 좌표를 반환
        아니면 False 반환
        """

        ci, cj = self.pos

        dist_from_exit = abs(ci - MAZE.exit_pos[0]) + abs(cj - MAZE.exit_pos[1])
        for k in range(4):
            ni, nj = ci + DI[k], cj + DJ[k]
            tmp_dist = abs(ni - MAZE.exit_pos[0]) + abs(nj - MAZE.exit_pos[1])
            if oob(ni, nj): continue
            if MAZE.matrix[ni][nj] > 0: continue
            if tmp_dist >= dist_from_exit: continue
            self.update_pos((ci, cj), (ni, nj))
            self.runningDist += 1
            if (ni, nj) == MAZE.exit_pos:
                self.exited = True
                self.matrix[self.pos[0]][self.pos[1]] = 0
                self.pos = (0, 0)
            return self.pos
        return False

    def rotate(self, si, sj, sq_size):
        tmp_matrix = [[0 for j in range(sq_size)] for i in range(sq_size)]
        for j in range(sq_size):
            for i in range(sq_size):
                tmp_matrix[j][i] = self.matrix[si + sq_size - 1 - i][sj + j]

        for i in range(sq_size):
            for j in range(sq_size):
                self.matrix[si + i][sj + j] = tmp_matrix[i][j]
                if self.matrix[si + i][sj + j] == 1:
                    self.pos = (si + i, sj + j)

    def DEBUG_matrix(self):
        print("-" * 64)
        for i in range(1, N + 1):
            for j in range(1, N + 1):
                print(self.matrix[i][j], end=" ")
            print()


class Maze:
    def __init__(self):
        self.matrix = [[0 for j in range(N + 1)] for i in range(N + 1)]
        self.exit_pos = (0, 0)

    def check_exit(self, start_pos, sq_size):
        si, sj = start_pos
        for i in range(si, si + sq_size):
            for j in range(sj, sj + sq_size):
                if oob(i, j): continue
                # 이건 벽이니깐 볼 필요도 없음
                if self.matrix[i][j] > 0: continue
                if (i, j) == self.exit_pos:
                    return True
        return False

    def check_runners(self, start_pos, sq_size):
        runners_poses = list(map(lambda x: x.pos, runners))
        # print(runners_poses)
        si, sj = start_pos
        ret = []
        for i in range(si, si + sq_size):
            for j in range(sj, sj + sq_size):
                tmp_pos = (i, j)
                if oob(i, j): continue
                # 이건 벽이니깐 볼 필요 없음
                if self.matrix[i][j] > 0: continue
                for idx in range(1, M + 1):
                    # 아직 탈출 안 한 러너들 중에서
                    if not runners[idx].exited and tmp_pos == runners_poses[idx]:
                        ret.append(idx)
        return ret

    def rotate(self):
        h = []
        for sq_size in range(2, N + 1):
            for i in range(1, N + 1):
                for j in range(1, N + 1):
                    # oob를 써서 최적화의 여지가 있음
                    if not self.check_exit((i, j), sq_size): continue
                    runners_list = self.check_runners((i, j), sq_size)
                    if len(runners_list) > 0:
                        heapq.heappush(h, (sq_size, i, j, runners_list))

        smallest = heapq.heappop(h)
        sq_size, si, sj, runners_list = smallest

        tmp_matrix = [[0 for j in range(sq_size)] for i in range(sq_size)]
        for j in range(sq_size):
            for i in range(sq_size):
                tmp_matrix[j][i] = self.matrix[si + sq_size - 1 - i][sj + j]

        for i in range(sq_size):
            for j in range(sq_size):
                # 벽이라면 1씩 까이면서 들어간다
                self.matrix[si + i][sj + j] = (tmp_matrix[i][j] - 1) if tmp_matrix[i][j] > 0 else tmp_matrix[i][j]
                if self.matrix[si + i][sj + j] == -1: self.exit_pos = (si + i, sj + j)
        # 러너들 각자의 매트릭스도 회전시킨다
        # print(f"회전해야 되는 러너들의 idx: {runners_list}")
        for idx in runners_list:
            runners[idx].rotate(si, sj, sq_size)

    def DEBUG_maze(self):
        for i in range(1, N + 1):
            for j in range(1, N + 1):
                print(self.matrix[i][j], end=" ")
            print()


N, M, K = map(int, input().rstrip().split())
MAZE = Maze()
runners = [Runner() for _ in range(M + 1)]
for i in range(1, N + 1):
    row = list(map(int, input().rstrip().split()))

    for j in range(1, N + 1):
        MAZE.matrix[i][j] = row[j - 1]

for idx in range(1, M + 1):
    i, j = map(int, input().rstrip().split())
    runners[idx].update_pos((0, 0), (i, j))
MAZE.exit_pos = tuple(map(int, input().rstrip().split()))
MAZE.matrix[MAZE.exit_pos[0]][MAZE.exit_pos[1]] = -1

for sec in range(1, K + 1):
    game_end = True
    for idx in range(1, M + 1):
        if runners[idx].exited: continue
        runners[idx].move()

    for idx in range(1, M + 1):
        if not runners[idx].exited:
            game_end = False
    if game_end:
        break
    MAZE.rotate()
    # DEBUG(f"{sec}초 회전 후:")
    # MAZE.DEBUG_maze()
    # for idx in range(1, M + 1):
    #         DEBUG(f"{idx}러너의 현상황:")
    # runners[idx].DEBUG_matrix()

ans = 0
for idx in range(1, M + 1):
    ans += runners[idx].runningDist
print(ans)
print(MAZE.exit_pos[0], MAZE.exit_pos[1])