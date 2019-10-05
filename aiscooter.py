import pygame
# from tensorflow import keras
# import numpy
# import pandas
from vector import Vector
import math

RED = [255, 0, 0]
WHITE = [255, 255, 255]

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

    def step(self, delta: float):
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

        pygame.draw.polygon(screen, RED, corners)

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
        self.scooter = Scooter()
        self.scooter.pos = Vector(100, 400)
        self.scooter.size = Vector(10, 20)
        self.screen_size = (800, 800)
        self.course_flipped = pygame.image.load("map0.png")
        self.course = pygame.transform.flip(self.course_flipped, False, True)
        self.carry_on = True
        self.scooter.speed = 1
        self.scooter.steering = 0
        self.scooter.steering_rate = 0.05
        self.scooter.heading = 0

    def start(self):
        pygame.init()
        pygame.display.set_caption("AI Scooter!")
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode(self.screen_size)

        while(self.carry_on):
            delta = clock.tick(60) / 1000

            self.scooter.step(1)
            self.handle_events()
            self.user_input()

            screen.fill(WHITE)
            screen.blit(self.course_flipped, (0, 0))
            self.scooter.draw(screen)
            pygame.display.flip()

            print("Collision!" if self.scooter.check_collision(self.course) else "No Collision")

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
        self.scooter.steering = steering

Game().start()
