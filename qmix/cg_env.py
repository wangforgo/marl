import time
import copy
import pygame
from pygame.locals import *
from pygame.color import Color
import numpy as np
from enum import IntEnum
import random

MAX_ROUND_NUM = 10
BLOCK_SIZE = 30
W = 21


def is_pos_legal(pos):
    return 0 <= pos[0] < W and 0 <= pos[1] < W


def dist_pos(pos1, pos2):
    return max(abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1]))

def pos_2_int(pos):
    return pos[0] * W + pos[1]


class MP(IntEnum):
    Space = 0
    Home = 1
    Away = 2
    Mountain = 3
    OB_Away_Done = 4 # 只作为单个体观察状态


def get_siblings(steps, include_center):
    sibs = []
    for i in range((steps * 2 + 1) * (steps * 2 + 1)):
        x = i // (steps * 2 + 1) - steps
        y = i % (steps * 2 + 1) - steps
        if x == 0 and y == 0 and not include_center:
            continue
        sibs.append(np.array([x, y]))
    return sibs


def gen_static_data(n_home):
    return [0, 1, 2, 75, 68, 148, 4, 322, 171, 182, 8, 174, 100, 6, 53, 123, 331, 99, 298, 358, 119, 225, 292, 138, 201, 436, 421, 38, 350, 169, 340, 245, 435, 223, 264, 72, 352, 355, 433, 136, 24, 337, 42, 202, 231, 149, 101, 85, 162, 356, 34, 140, 137, 343, 386, 320, 199, 318, 291, 359, 26, 437, 141, 410, 382, 289, 163, 46, 219, 303, 157, 95, 210, 207, 12, 64, 413, 200, 434, 192, 236, 427, 274, 87, 27, 113, 235, 117, 380, 383, 333, 247, 139, 67, 398, 396, 234, 184, 147, 221, 244, 143, 377, 400, 11, 33, 31, 314, 52, 276, 253, 63, 311, 208, 389, 429, 78, 304, 121, 127, 56, 108, 120, 152, 92, 387, 106, 51, 290, 150, 49, 126, 373, 422, 323, 430, 131, 242, 55, 403, 62, 338, 70, 379, 294, 402, 438, 232, 341, 414, 224, 165, 353, 166, 109, 20, 301, 248, 22, 362, 233, 415, 255, 177, 335, 269, 96, 261, 250, 345, 405, 69, 25, 114, 196, 365, 328, 349, 73, 273, 217, 97, 110, 310, 384, 412, 375, 228, 287, 278, 306, 281, 305, 425, 14, 130, 297, 91, 18, 347, 286, 61, 237, 300, 65, 170, 197, 368, 90, 357, 319, 220, 60, 59, 116, 115, 142, 30, 272, 154, 89, 330, 86, 229, 370, 23, 183, 243, 153, 401, 371, 406, 50, 205, 134, 181, 172, 164, 10, 58, 48, 230, 344, 302, 283, 160, 167, 366, 194, 43, 112, 440, 204, 189, 418, 399, 190, 426, 125, 416, 79, 128, 57, 317, 252, 279, 346, 132, 280, 193, 13, 395, 423, 321, 361, 296, 198, 378, 288, 324, 37, 83, 168, 84, 129, 107, 206, 277, 424, 16, 195, 158, 44, 45, 21, 215, 159, 80, 226, 411, 124, 312, 118, 376, 327, 213, 82, 254, 39, 432, 354, 394, 188, 122, 76, 351, 151, 191, 239, 156, 313, 146, 332, 238, 178, 77, 173, 284, 155, 439, 222, 270, 185, 363, 218, 329, 74, 161, 372, 71, 339, 35, 336, 88, 17, 7, 15, 263, 262, 404, 251, 180, 282, 367, 315, 66, 271, 105, 360, 408, 392, 216, 40, 390, 417, 175, 19, 102, 374, 258, 334, 393, 94, 187, 133, 256, 111, 241, 203, 98, 227, 266, 309, 9, 428, 260, 419, 316, 385, 29, 409, 407, 299, 104, 249, 32, 81, 275, 369, 47, 135, 307, 420, 391, 342, 5, 431, 381, 397, 179, 93, 293, 240, 36, 295, 257, 259, 145, 28, 54, 186, 144, 214, 325, 388, 268, 209, 308, 176, 265, 3, 41, 212, 326, 103, 348, 211, 364, 267, 246, 285]
    # start_pos = [np.array((0,0)),np.array((0,1)),np.array((0,2)),
    #              np.array((1,0)),np.array((1,1)),np.array((1,2)),
    #              np.array((2,0)),np.array((2,1)),np.array((2,2)),
    #              np.array((3,0)),]
    # rand_data = []
    # occupy = np.zeros((W*W), dtype=int)
    # for i in range(n_home):
    #     rand_data.append(pos_2_int(start_pos[i]))
    #     occupy[pos_2_int(start_pos[i])] = 1
    # free = []
    # for i in range(W*W):
    #     if occupy[i] == 0:
    #         free.append(i)
    # np.random.shuffle(free)
    # rand_data.extend(free)
    # print("static_data:")
    # print(rand_data)
    # return rand_data




EnableUI = True


class Game:
    def __init__(self):
        self.w = W
        self.n_home = 3
        self.n_away = 10
        self.n_mountain = 40
        self.home = np.zeros((self.n_home, 2), dtype=int)
        self.away = np.zeros((self.n_home, 2), dtype=int)
        self.away_hurt = np.zeros(self.n_away, dtype=int)
        if EnableUI:
            self.screen = pygame.display.set_mode((self.w * BLOCK_SIZE, self.w * BLOCK_SIZE))
            self.screen.fill("white")
            pygame.display.set_caption("Game")
            self.clock = pygame.time.Clock()
        self.score = 0
        self.step_idx = 0
        self.mp = np.zeros((self.w * self.w), dtype=int)
        self.att_record = []

        self.reset()

    def reset(self, *data):
        data = [gen_static_data(self.n_home)]
        self.score = 0
        self.step_idx = 0
        self.home = np.zeros((self.n_home, 2), dtype=int)
        self.away = np.zeros((self.n_away, 2), dtype=int)
        self.mp = np.zeros((self.w * self.w), dtype=int)

        if len(data) > 0:
            if len(data[0]) < self.n_home + self.n_away + self.n_mountain:
                print("data too short")
                quit(-1)
            rand_list = data[0]
        else:
            rand_list = np.arange(self.w * self.w)
            np.random.shuffle(rand_list)
        for i in range(self.n_home):
            p = rand_list[i]
            self.home[i][0] = p // self.w
            self.home[i][1] = p % self.w
            self.mp[p] = MP.Home
        for i in range(self.n_away):
            p = rand_list[self.n_home + i]
            self.away[i][0] = p // self.w
            self.away[i][1] = p % self.w
            self.mp[p] = MP.Away
        for i in range(self.n_mountain):
            p = rand_list[self.n_home + self.n_away + i]
            self.mp[p] = MP.Mountain

        self.att_record = []
        self.away_hurt = np.zeros(self.n_away, dtype=int)
        for i in range(self.n_home):
            self.att_record.append({})
        self.render()

    def render(self):
        if not EnableUI:
            return
        self.screen.fill("white")

        def draw_rect(x, y, color):
            x_, y_ = x, self.w - 1 - y
            pygame.draw.rect(self.screen, Color(color), (x_ * BLOCK_SIZE, y_ * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        def draw_text(text, x, y):
            pygame.font.init()  # you have to call this at the start,
            my_font = pygame.font.SysFont('Comic Sans MS', 20)
            textImage = my_font.render(text, True, "black")
            x_, y_ = x, self.w - 1 - y
            self.screen.blit(textImage, (x_ * BLOCK_SIZE, y_ * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        for p in self.home:
            draw_rect(p[0], p[1], "red")
        for i in range(self.n_away):
            draw_rect(self.away[i][0], self.away[i][1], "blue")
            draw_text(str(self.away_hurt[i]), self.away[i][0], self.away[i][1])

        for p in range(self.w * self.w):
            if self.mp[p] == MP.Mountain:
                draw_rect(p // self.w, p % self.w, "grey")
        pygame.display.update()
        self.clock.tick(30)

    def step(self, actions):
        if EnableUI:
            for ev in pygame.event.get():
                if ev.type == QUIT:
                    pygame.quit()
                    quit()
                elif ev.type == KEYDOWN:
                    if ev.key == K_SPACE:
                        pygame.quit()
                    elif ev.key == K_q:
                        pygame.quit()
                    quit()

        assert len(actions) == self.n_home
        reward = 0

        actions_dp = self.get_avail_actions()
        d_actions = []
        for a in actions:
            d_actions.append(actions_dp[a])

        tgts = self.home + d_actions
        for i in range(len(tgts)):
            if not is_pos_legal(tgts[i]) or self.mp[pos_2_int(tgts[i])] == MP.Mountain or self.mp[pos_2_int(tgts[i])] == MP.Away:
                tgts[i] = self.home[i]
                return -100, True, self.score  # 禁止非法操作
        no_conflict_tgts = move_one_step([self.home, tgts])
        if no_conflict_tgts is None:
            return -100, True, self.score
        # 移动和计算
        for i in range(self.n_home):
            self.mp[pos_2_int(self.home[i])] = MP.Space
            self.mp[pos_2_int(no_conflict_tgts[i])] = MP.Home
            self.home[i] = no_conflict_tgts[i]

            min_dist = W
            for j in range(len(self.away)):
                e = self.away[j]
                if (e[0] * W + e[1]) in self.att_record[i]:
                    continue
                dist = dist_pos(e, self.home[i])
                if dist < min_dist:
                    min_dist = dist
                if dist > 1:
                    continue
                self.att_record[i][e[0] * W + e[1]] = True
                self.away_hurt[j] += 1
                reward += 10
                self.score += 1
            reward += 10 - min_dist/W*10
        self.render()
        self.step_idx += 1
        terminated = self.step_idx == 10
        return reward, terminated, self.score


    def get_avail_actions(self):
        return get_siblings(1, True)

    def get_state(self):
        # 地图
        state = copy.deepcopy(self.mp)
        # 攻击情况
        # def att_record_normalized(home_idx):
        #     att_rec = np.zeros(self.n_away, dtype=int)
        #     for k in self.att_record[home_idx]:
        return state

    def get_obs(self):
        sibs = get_siblings(1, False)
        ob_mp_list = []
        for i in range(self.n_home):
            p = self.home[i]
            ob_walkable = np.zeros(len(sibs), dtype=int)
            ob_home = np.zeros(len(sibs), dtype=int)
            ob_away = np.zeros(len(sibs), dtype=int)
            for j in range(len(sibs)):
                tp = sibs[j] + p
                tp_int = pos_2_int(tp)
                if not is_pos_legal(tp):
                    continue
                v = self.mp[tp_int]
                if v == MP.Space:
                    ob_walkable[j] = 1
                elif v == MP.Home:
                    ob_home[j] = 1
                elif v == MP.Away:
                    if tp_int not in self.att_record[i]:
                        ob_away[j] = 1
            ob_mp_list.append(ob_walkable+ob_home+ob_away)

        return ob_mp_list


def move_one_step(actions):
    prev = actions[0]
    target = copy.deepcopy(actions[1])
    while True:
        tgt_mp = {}
        has_conflict = False
        for i in range(len(target)):
            p_int = target[i][0] * W + target[i][1]
            if tgt_mp.get(p_int) is None:
                tgt_mp[p_int] = [i]
            else:
                tgt_mp[p_int].append(i)
                has_conflict = True
                return None
        if not has_conflict:
            break
        for k in tgt_mp:
            v = tgt_mp[k]
            if len(v) > 1:
                for i in v:
                    target[i] = prev[i]

    return target


# game = Game()
# game.reset(gen_static_data(game.n_home))
# time.sleep(1)
# for i in range(10):
#     print(game.away_hurt)
#     actions = []
#     for j in range(game.n_home):
#         x = random.randint(0, len(game.get_avail_actions()) - 1)
#         actions.append(game.get_avail_actions()[x])
#
#     game.step(actions)
# print(move_one_step([[[0, 0], [1, 1], [2,2]],
#                      [[1, 0], [1, 0],[1,1]]]))
