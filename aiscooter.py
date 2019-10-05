import pygame
# from tensorflow import keras
# import numpy
# import pandas
from vector import Vector
import math

GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
TRAN_BLUE = (0, 0, 255, 100)

def clamp(val, lower, upper):
    return max(min(val, upper), lower)

class Scooter(object):
    pos: Vector
    size: Vector
    speed: float
    heading: float
    steering: int
    steering_rate: float
    speed: float
    is_alive = True
    next_checkpoint = 0
    score = 0

    def step(self, delta: float):
        if not self.is_alive:
            return

        self.set_heading(self.heading + self.steering * delta * self.steering_rate)
        self.pos = self.pos.add(Vector.from_angle(self.heading).scale(delta * self.speed))

    def draw(self, screen):
        height = screen.get_size()[1]
        corners = [
            self.tl_pos(),
            self.tr_pos(),
            self.br_pos(),
            self.bl_pos()
        ]
        for i, point in enumerate(corners):
            point.y = height - point.y
            corners[i] = point.to_tuple()

        color = GREEN if self.is_alive else RED
        pygame.draw.polygon(screen, color, corners)

    def tl_pos(self):
        return self.pos.add(Vector(-self.size.x/2, self.size.y/2).rotate(-self.heading))

    def tr_pos(self):
        return self.pos.add(Vector(self.size.x/2, self.size.y/2).rotate(-self.heading))
    
    def bl_pos(self):
        return self.pos.add(Vector(-self.size.x/2, -self.size.y/2).rotate(-self.heading))

    def br_pos(self):
        return self.pos.add(Vector(self.size.x/2, -self.size.y/2).rotate(-self.heading))

    def set_heading(self, heading):
        two_pi = 2 * math.pi
        self.heading = (heading + two_pi) % two_pi

    def check_collision(self, map_image):
        for point in self.perimeter_points():
            color = map_image.get_at((int(point.x), int(point.y)))
            if color[0] == 0 and color[1] == 0 and color[2] == 0:
                return True
        return False

    def perimeter_points(self):
        tl = self.tl_pos()
        tr = self.tr_pos()
        bl = self.bl_pos()
        br = self.br_pos()

        points = self.points_on_line(tl, tr)
        points.extend(self.points_on_line(tr, br))
        points.extend(self.points_on_line(br, bl))
        points.extend(self.points_on_line(bl, tr))

        return points

    def points_on_line(self, pointA, pointB):
        points = []
        aX = int(pointA.x)
        aY = int(pointA.y)
        bX = int(pointB.x)
        bY = int(pointB.y)
        
        if aX == bX:
            for i in range(aY, bY, 1 if aY > bY else -1):
                points.append(Vector(pointA.X, i))
        else:
            slope = (bY - aY) / (bX - aX)
            intercept = aY - slope * aX

            for i in range(aX, bX, 1 if bX > aX else -1):
                y = slope * i + intercept
                points.append(Vector(i, y))

        return points


class Game(object):
    def __init__(self):
        self.make_scooters(1, Vector(100, 400))
        self.screen_size = (800, 800)
        self.course_flipped = pygame.image.load("map0.png")
        self.course = pygame.transform.flip(self.course_flipped, False, True)
        self.carry_on = True
        self.frame_rate = 0
        self.screen = None
        self.tran_surface = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        self.checkpoints = [
            (Vector(120, 700), 80),
            (Vector(700, 660), 80),
            (Vector(290, 500), 80),
            (Vector(690, 250), 80),
            (Vector(150, 200), 80)
        ]

    def make_scooters(self, count, start_pos):
        scooters = []
        for _ in range(count):
            scooter = Scooter()
            scooter.pos = Vector(start_pos.x, start_pos.y)
            scooter.size = Vector(10, 20)
            scooter.speed = 1
            scooter.steering = 0
            scooter.steering_rate = 0.05
            scooter.heading = 0
            scooters.append(scooter)
        self.scooters = scooters

    def start(self):
        pygame.init()
        pygame.display.set_caption("AI Scooter!")
        clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.screen_size)

        while(self.carry_on):
            delta = 1
            if self.frame_rate > 0:
                delta = clock.tick(self.frame_rate) / 1000

            self.user_input()
            self.handle_events()
            self.update_scooters(delta)
            self.screen.fill(WHITE)
            self.screen.blit(self.course_flipped, (0, 0))
            self.draw_scooters()
            self.draw_checkpoints()

            pygame.display.flip()

        print("Scores: {0}".format(', '.join(str(s.score) for s in self.scooters)))

    def update_scooters(self, delta):
        any_alive = False

        for scooter in self.scooters:
            if scooter.is_alive:
                any_alive = True
                scooter.step(delta)
                scooter.is_alive = not scooter.check_collision(self.course)
                if not scooter.is_alive:
                    scooter.score -= 20

                next_point = self.checkpoints[scooter.next_checkpoint]
                if next_point[0].sub(scooter.pos).magsqr() < next_point[1] * next_point[1]:
                    scooter.score += 5
                    scooter.next_checkpoint = 0 if scooter.next_checkpoint == len(self.checkpoints)-1 else scooter.next_checkpoint + 1
                    print("next checkpoint {0}".format(scooter.next_checkpoint))

        self.carry_on = any_alive

    def draw_scooters(self):
        for scooter in self.scooters:
            scooter.draw(self.screen)

    def draw_checkpoints(self):
        for checkpoint in self.checkpoints:
            pygame.draw.circle(self.tran_surface, TRAN_BLUE, (checkpoint[0].x, self.screen_size[1] - checkpoint[0].y), checkpoint[1])

        self.screen.blit(self.tran_surface, (0, 0))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.carry_on = False

    def user_input(self):
        keys = pygame.key.get_pressed()
        steering = 0
        if keys[pygame.K_a]:
            steering -= 1
        if keys[pygame.K_d]:
            steering += 1

        for scooter in self.scooters:
            scooter.steering = steering

Game().start()
