import heapq
import sys

# sys.stdin = open("input1.txt", "r")
input = sys.stdin.readline
N, M, P, C, D = map(int, input().rstrip().split())
santas = [None for _ in range(P)]
rudolph_pos = tuple(map(lambda x: int(x) - 1, input().rstrip().split()))
board = [[None for j in range(N)] for i in range(N)]
board[rudolph_pos[0]][rudolph_pos[1]] = 100
rudolph_dirs = [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1) if i != 0 or j != 0]
# 상우하좌
santa_dirs = [(-1, 0), (0, 1), (1, 0), (0, -1)]


class cmp_santa:
    def __init__(self, dist, pos, idx):
        self.dist = dist
        self.ci = pos[0]
        self.cj = pos[1]
        self.idx = idx

    def __lt__(self, other):
        if self.dist < other.dist:
            return True
        elif self.dist == other.dist:
            if self.ci == other.ci:
                return self.cj > other.cj
            return self.ci > other.ci
        else:
            return False

    def __str__(self):
        return f"dist: {self.dist}, ci: {self.ci}, cj: {self.cj}, idx: {self.idx}"


def get_dist(pos1, pos2):
    i1, j1 = pos1
    i2, j2 = pos2
    return (i1 - i2) ** 2 + (j1 - j2) ** 2


def find_closest_santa(src_pos, target_poses):
    h = []
    ret_idx = -1
    min_dist = int(1e9)
    len_targets = len(target_poses)
    for i in range(len_targets):
        if is_retired[i]: continue
        tmp_dist = get_dist(src_pos, target_poses[i])
        heapq.heappush(h, cmp_santa(tmp_dist, target_poses[i], i))

    ret = heapq.heappop(h)
    ret_idx = ret.idx
    return ret_idx


def OOB(i, j):
    if i < 0 or i >= N: return True
    if j < 0 or j >= N: return True

    return False


def move_from_cur_to_new(c_pos, n_pos, something):
    ci, cj = c_pos
    ni, nj = n_pos
    board[ci][cj] = None
    board[ni][nj] = something


def rudolph_select_dir(src_pos, santa_pos):
    h = []
    ret_dir = (None, None)
    ci, cj = src_pos
    dist_from_santa = get_dist(src_pos, santa_pos)
    for k in range(8):
        di, dj = rudolph_dirs[k]
        ni, nj = ci + di, cj + dj
        if OOB(ni, nj): continue
        tmp_dist_from_santa = get_dist((ni, nj), santa_pos)
        if tmp_dist_from_santa < dist_from_santa:
            dist_from_santa = tmp_dist_from_santa
            ret_dir = (di, dj)
    # print(f"루돌프가 선택한 dir: {ret_dir}")
    return ret_dir


# 전파되는 방향, 현재 pos, 밀리는 산타의 idx
def interact(vec, cur_pos, pushed_santa_idx, turn_th):
    ci, cj = cur_pos[0], cur_pos[1]
    ni, nj = ci + vec[0], cj + vec[1]
    # base condition1
    # 보드밖으로 나갈 때
    if OOB(ni, nj):
        # 밀렸다는 건 민 사람이 있다는 건데 민 사람이 있는 자리를 None으로 만들면 안된다
        # 내가 갈 자리를 덮어 쓰면 된다
        is_retired[pushed_santa_idx] = True
        update_santa_info(pushed_santa_idx, (None, None))
        return

    # base condition2
    # 밀렸는데 뒤에 사람이 없을 때
    if board[ni][nj] == None:
        # 밀렸다는 건 민 사람이 있다는 건데 민 사람이 있는 자리를 None으로 만들면 안된다
        # 내가 갈 자리를 덮어 쓰면 된다
        board[ni][nj] = pushed_santa_idx
        update_santa_info(pushed_santa_idx, (ni, nj))
        return

    # 밀렸는데 뒤에 사람이 있을 때
    santa_behind_me = board[ni][nj]
    # 밀렸다는 건 민 사람이 있다는 건데 민 사람이 있는 자리를 None으로 만들면 안된다
    # 내가 갈 자리를 덮어 쓰면 된다
    board[ni][nj] = pushed_santa_idx
    update_santa_info(pushed_santa_idx, (ni, nj))
    interact(vec, (ni, nj), santa_behind_me, turn_th)


def update_santa_info(santa_idx, new_pos):
    santas[santa_idx][1] = new_pos[0]
    santas[santa_idx][2] = new_pos[1]


def update_stun(santa_idx, turn_th):
    is_stunned[santa_idx] = True
    wake_up_turn_th[santa_idx] = turn_th + 2


def push_santa(src_pos, vec, force, pushed_santa_idx, turn_th):
    # src_pos를 마지막에 100(루돌프)으로 채우고
    # vec * force 만큼 밀어낸다
    # c_pos: 루돌프가 있는 곳, santa_pos: 돌진하기 직전에 산타가 있던 곳, n_pos: 루돌프가 산타를 날려 버린 곳
    ci, cj = src_pos[0], src_pos[1]
    santa_pos = (santas[pushed_santa_idx][1], santas[pushed_santa_idx][2])
    ni, nj = ci + vec[0] * force, cj + vec[1] * force
    # 산타가 날라 갔는데 거기가 board밖이라면?
    if OOB(ni, nj):
        is_retired[pushed_santa_idx] = True
        # move_from_cur_to_new를 못써서 이 한줄로 대체
        board[santa_pos[0]][santa_pos[1]] = None
        update_santa_info(pushed_santa_idx, (None, None))
        board[ci][cj] = 100
        return
    # 산타가 날라 갔는데 거기가 공석이라면
    if board[ni][nj] == None:
        move_from_cur_to_new(santa_pos, (ni, nj), pushed_santa_idx)
        # 산타 정보 업데이트
        update_santa_info(pushed_santa_idx, (ni, nj))
        update_stun(pushed_santa_idx, turn_th)
        board[ci][cj] = 100
        return

    # None이 아닌 뭔가가 있다면
    if board[ni][nj] != None:
        # 전파해야 함
        # 먼저 최초의 밀려난 산타에 대한 처리를 한다
        santa_behind_me = board[ni][nj]
        move_from_cur_to_new(santa_pos, (ni, nj), pushed_santa_idx)
        update_santa_info(pushed_santa_idx, (ni, nj))
        update_stun(pushed_santa_idx, turn_th)
        # 날라간 곳으로 부터 연쇄 인터랙트가 시작된다
        interact(vec, (ni, nj), santa_behind_me, turn_th)
        board[ci][cj] = 100


def rudolph_move(turn_th):
    global rudolph_pos

    # 아직 retired가 아닌 산타 중에서 가장 가까운 산타를 찾는다
    santa_poses = [*map(lambda x: (x[1], x[2]), santas)]
    # print(f"santa_poses: {santa_poses}")
    # print(f"rudolph_pos: {rudolph_pos}")
    # 가장 가까운 산타를 찾는다
    selected_santa_idx = find_closest_santa(rudolph_pos, santa_poses)
    # 돌진한다
    selected_santa_i, selected_santa_j = santa_poses[selected_santa_idx]
    selected_dir = rudolph_select_dir(rudolph_pos, (selected_santa_i, selected_santa_j))
    if selected_dir == (None, None):
        print("루돌프가 움직일 dir를 선택하지 못했습니다!")
        exit(1)

    ci, cj = rudolph_pos
    ni, nj = ci + selected_dir[0], cj + selected_dir[1]
    if board[ni][nj] != None:
        # collide 발생
        board[ci][cj] = None
        pushed_santa = board[ni][nj]
        push_santa((ni, nj), selected_dir, C, pushed_santa, turn_th)
        # 점수 계산
        santa_scores[pushed_santa] += C
        rudolph_pos = (ni, nj)

    else:
        # 100이 루돌프를 나타냄
        move_from_cur_to_new((ci, cj), (ni, nj), 100)
        # update rudolph_pos
        rudolph_pos = (ni, nj)


def santa_select_dir(src_pos):
    h = []
    ret_dir = (None, None)
    ci, cj = src_pos
    dist_from_rudolph = get_dist(src_pos, rudolph_pos)
    for k in range(4):
        di, dj = santa_dirs[k]
        ni, nj = ci + di, cj + dj
        # 보드밖으로 가거나
        if OOB(ni, nj): continue
        # 다른 산타가 있으면은
        if board[ni][nj] != None and board[ni][nj] != 100: continue
        tmp_dist_from_rudolph = get_dist((ni, nj), rudolph_pos)
        if tmp_dist_from_rudolph < dist_from_rudolph:
            dist_from_rudolph = tmp_dist_from_rudolph
            ret_dir = (di, dj)
    # print(f"산타가 선택한 dir: {ret_dir}")
    return ret_dir


def santas_move(turn_th):
    santa_poses = list(map(lambda x: (x[1], x[2]), santas))
    for i in range(P):
        if is_retired[i] or is_stunned[i]:
            continue
        selected_dir = santa_select_dir(santa_poses[i])
        # 가까워지는 선택을 할 수 없거나 딴 산타가 다 점유중이면 continue
        if selected_dir == (None, None): continue
        ci, cj = santa_poses[i]
        ni, nj = ci + selected_dir[0], cj + selected_dir[1]
        if board[ni][nj] == 100:
            # 루돌프가 있다는 것 -> collide 발생
            # print(f"밀려날 산타: {i}, 산타가 돌진했던 방향: {selected_dir}")
            push_santa((ni, nj), (-selected_dir[0], -selected_dir[1]), D, i, turn_th)
            santa_scores[i] += D
        else:
            move_from_cur_to_new((ci, cj), (ni, nj), i)
            update_santa_info(i, (ni, nj))
            # 부딪히지는 않았으니깐 stun은 처리하지 않는다


def wake_up(turn_th):
    for i in range(P):
        if is_stunned[i] and wake_up_turn_th[i] == turn_th:
            is_stunned[i] = False
            wake_up_turn_th[i] = None


def is_game_over():
    for i in range(P):
        if not is_retired[i]:
            return False
    return True


def plus_one_santa_scores():
    for i in range(P):
        if not is_retired[i]:
            santa_scores[i] += 1


def print_board():
    for i in range(N):
        for j in range(N):
            print(board[i][j], end=' ')
        print()


for i in range(P):
    santa_idx, ci, cj = map(lambda x: int(x) - 1, input().rstrip().split())
    santas[santa_idx] = [santa_idx, ci, cj]
    board[ci][cj] = i

santa_scores = [0 for _ in range(P)]
is_retired = [False for _ in range(P)]
is_stunned = [False for _ in range(P)]
wake_up_turn_th = [None for _ in range(P)]

for i in range(M):
    wake_up(i)
    rudolph_move(i)
    santas_move(i)
    if is_game_over():
        break
    plus_one_santa_scores()
for i in range(P):
    print(santa_scores[i], end=" ")