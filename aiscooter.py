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

    def __init__(self):
        self.steering_rate = 0.5

    def step(self, delta: float):
        self.set_heading(self.heading + self.steering * delta * self.steering_rate)
        self.pos = self.pos.add(Vector.from_angle(self.heading).scale(delta * self.speed))

    def draw(self, screen):
        corners = [self.tl_pos().to_tuple(), self.tr_pos().to_tuple(), self.br_pos().to_tuple(), self.bl_pos().to_tuple()]
        pygame.draw.polygon(screen, RED, corners)

    def tl_pos(self):
        return self.pos.add(Vector(-self.size.x/2, self.size.y/2).rotate(self.heading))

    def tr_pos(self):
        return self.pos.add(Vector(self.size.x/2, self.size.y/2).rotate(self.heading))
    
    def bl_pos(self):
        return self.pos.add(Vector(-self.size.x/2, -self.size.y/2).rotate(self.heading))

    def br_pos(self):
        return self.pos.add(Vector(self.size.x/2, -self.size.y/2).rotate(self.heading))

    def set_heading(self, heading):
        two_pi = 2 * math.pi
        self.heading = (heading + two_pi) % two_pi

    def steer(self, dir):
        self.steering = dir    

class Game(object):
    def __init__(self):
        self.scooter = Scooter()
        self.scooter.pos = Vector(400, 400)
        self.scooter.size = Vector(10, 20)
        self.screen_size = (800, 800)
        self.carry_on = True
        self.scooter.speed = 40
        self.scooter.steering = 0
        self.scooter.steering_rate = 1
        self.scooter.heading = 0

    def start(self):
        pygame.init()
        pygame.display.set_caption("AI Scooter!")
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode(self.screen_size)

        while(self.carry_on):
            delta = clock.tick(10) / 1000

            self.scooter.step(delta)
            self.handle_events()
            self.user_input()

            screen.fill(WHITE)
            self.scooter.draw(screen)
            pygame.display.flip()

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
        self.scooter.steer(steering)

Game().start()
