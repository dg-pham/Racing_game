import math
import time

import pygame

from utils import scale_image, blit_rotate_center, blit_text_center

# font
pygame.font.init()
MAIN_FONT = pygame.font.SysFont('comicsans', 44)

# load & scale images
GRASS = scale_image(pygame.image.load('imgs/grass.jpg'), 2.5)
TRACK = scale_image(pygame.image.load('imgs/track.png'), 0.9)

TRACK_BORDER = scale_image(pygame.image.load('imgs/track-border.png'), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = pygame.image.load('imgs/finish.png')
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130, 250)

RED_CAR = scale_image(pygame.image.load('imgs/red-car.png'), 0.55)
GREEN_CAR = scale_image(pygame.image.load('imgs/green-car.png'), 0.55)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()

WIN = pygame.display.set_mode((WIDTH, HEIGHT))

images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]

# AI path
PATH = [(175, 119), (110, 70), (56, 133), (70, 481), (318, 731), (404, 680), (418, 521), (507, 475), (600, 551),
        (613, 715), (736, 713),
        (734, 399), (611, 357), (409, 343), (433, 257), (697, 258), (738, 123), (581, 71), (303, 78), (275, 377),
        (176, 388), (178, 260)]

# caption
pygame.display.set_caption('Racing Game!')


# classes
class GameInfo:
    LEVELS = 10

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def game_finished(self):
        # king of games
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        # get level's time
        return round(time.time() - self.level_start_time)


class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        # counterclockwise
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        # draw car
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        # speed increase from 0 to max_vel with acceleration
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        # speed decrease from vel to 0 and increase from 0 to max_vel / 2 (backward) with acceleration
        self.vel = max(self.vel - self.acceleration, -self.max_vel / 2)
        self.move()

    def move(self):
        # theta = PI / 2 - angle
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        # straight
        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        # Returns the point of intersection
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0


class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (180, 200)

    def reduce_speed(self):
        # speed decrease from vel to 0 with acceleration = acceleration / 2
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        # reverse vel when bounce
        self.vel = -self.vel * 0.75
        self.move()


class ComputerCar(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (150, 200)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    # check algorithm
    # def draw_points(self, win):
    #     for point in self.path:
    #         pygame.draw.circle(win, (255, 0, 0), point, 5)

    def draw(self, win):
        super().draw(win)
        # check algorithm
        # self.draw_points(win)

    def calculate_angle(self):
        # get path
        target_x, target_y = self.path[self.current_point]
        # get different coordinates
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        # x forward
        if y_diff == 0:
            desired_radian_angle = math.pi / 2
        # get angle
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)

        # turn down if higher than target
        if target_y > self.y:
            desired_radian_angle += math.pi

        # get diff in angle
        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        # normalize
        if difference_in_angle >= 180:
            difference_in_angle -= 360

        # move as AI
        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            # next path
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            return

        self.calculate_angle()
        self.update_path_point()
        super().move()

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.2
        self.current_point = 0


# functions
def draw(win, images, player_car, computer_car, game_info):
    # draw static images
    for img, pos in images:
        win.blit(img, pos)

    # draw level
    level_text = MAIN_FONT.render(
        f'Level {game_info.level}', 1, (255, 255, 255))
    win.blit(level_text, (10, HEIGHT - level_text.get_height() - 70))

    # draw time
    time_text = MAIN_FONT.render(
        f'Time: {game_info.get_level_time()}s', 1, (255, 255, 255))
    win.blit(time_text, (10, HEIGHT - time_text.get_height() - 40))

    # draw velocity
    vel_text = MAIN_FONT.render(
        f'Vel: {round(player_car.vel, 1)}px/s', 1, (255, 255, 255))
    win.blit(vel_text, (10, HEIGHT - vel_text.get_height() - 10))

    # draw cars
    player_car.draw(win)
    computer_car.draw(win)
    # update frames
    pygame.display.update()


def move_player(player_car):
    # set keyboard for this game
    keys = pygame.key.get_pressed()
    moved = False

    # turning
    if keys[pygame.K_LEFT]:
        player_car.rotate(left=True)
    if keys[pygame.K_RIGHT]:
        player_car.rotate(right=True)
    # moving
    if keys[pygame.K_UP]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_DOWN]:
        moved = True
        player_car.move_backward()
    # stopping
    if not moved:
        player_car.reduce_speed()


def handle_collision(player_car, computer_car, game_info):
    # border collide
    if player_car.collide(TRACK_BORDER_MASK) is not None:
        player_car.bounce()

    # lost
    computer_finish_poi_collide = computer_car.collide(FINISH_MASK, *FINISH_POSITION)
    if computer_finish_poi_collide is not None:
        blit_text_center(WIN, MAIN_FONT, 'You lost!')
        pygame.display.update()
        # wait 5s before game restart
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()
        computer_car.reset()

    # win (next level)
    finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if finish_poi_collide is not None:
        # don't go wrong way
        if finish_poi_collide[1] == 0:
            player_car.bounce()
        # next level
        else:
            game_info.next_level()
            player_car.reset()
            computer_car.next_level(game_info.level)


# variables
FPS = 60
run = True
clock = pygame.time.Clock()
player_car = PlayerCar(4, 4)
computer_car = ComputerCar(2, 4, PATH)
game_info = GameInfo()

# run game
while run:
    # compute how many milliseconds have passed since the previous call
    clock.tick(FPS)

    # draw games
    draw(WIN, images, player_car, computer_car, game_info)

    # start game
    while not game_info.started:
        # waiting screen
        blit_text_center(
            WIN, MAIN_FONT, f'Press any key to start level {game_info.level}!')
        pygame.display.update()

        # game events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break
            # press any key
            if event.type == pygame.KEYDOWN:
                game_info.start_level()

    # game events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    # move
    move_player(player_car)
    computer_car.move()

    # handle collision
    handle_collision(player_car, computer_car, game_info)

    # win (finish)
    if game_info.game_finished():
        blit_text_center(WIN, MAIN_FONT, 'You won the game!')
        pygame.display.update()
        # wait 5s before game restart
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()
        computer_car.reset()

# exit game
pygame.quit()
