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
TRAN_GREEN = (0, 255, 0, 100)

def clamp(val, lower, upper):
    return max(min(val, upper), lower)

def normalize_angle(angle):
    return (angle + math.pi * 2.0) % (math.pi * 2.0)

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

    def draw(self, surface):
        corners = [
            self.tl_pos().to_tuple(),
            self.tr_pos().to_tuple(),
            self.br_pos().to_tuple(),
            self.bl_pos().to_tuple()
        ]

        color = GREEN if self.is_alive else RED
        pygame.draw.polygon(surface, color, corners)

    def tl_pos(self):
        return self.pos.add(Vector(-self.size.x/2, self.size.y/2).rotate(-self.heading))

    def tr_pos(self):
        return self.pos.add(Vector(self.size.x/2, self.size.y/2).rotate(-self.heading))
    
    def bl_pos(self):
        return self.pos.add(Vector(-self.size.x/2, -self.size.y/2).rotate(-self.heading))

    def br_pos(self):
        return self.pos.add(Vector(self.size.x/2, -self.size.y/2).rotate(-self.heading))

    def set_heading(self, heading):
        self.heading = normalize_angle(heading)

    def check_collision(self, map_image):
        for point in self.perimeter_points():
            color = map_image.get_at(point.to_int_tuple())
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
    
    def raycast(self, angle: float, course: pygame.Surface):
        start_range = 3
        max_range = 1200
        step = 1
        
        unit = Vector.from_angle(angle)
        for i in range(start_range, max_range, step):
            cast_pos = self.pos.add(unit.scale(i))
            if course.get_at(cast_pos.to_int_tuple()) == (0, 0, 0, 255):
                return (cast_pos, i)

        return (Vector(0, 0), max_range)


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
        self.scooter_surface = pygame.Surface(self.screen_size, pygame.SRCALPHA)
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
            scooter.speed = 60
            scooter.steering = 0
            scooter.steering_rate = 3
            scooter.heading = 0
            scooters.append(scooter)
        self.scooters = scooters

    def start(self):
        pygame.init()
        pygame.display.set_caption("AI Scooter!")
        clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.screen_size)

        while(self.carry_on):
            self.tran_surface.fill((0, 0, 0, 0))
            self.scooter_surface.fill((0, 0, 0, 0))

            delta = 1.0/60.0
            if self.frame_rate > 0:
                delta = clock.tick(self.frame_rate) / 1000

            self.user_input()
            self.handle_events()
            self.update_scooters(delta)
            self.screen.fill(WHITE)
            self.screen.blit(self.course_flipped, (0, 0))
            self.draw_checkpoints()
            self.draw_scooters()

            self.screen.blit(pygame.transform.flip(self.scooter_surface, False, True), (0, 0))
            self.screen.blit(self.tran_surface, (0, 0))
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
                
                self.get_state(scooter)

        self.carry_on = any_alive

    def draw_scooters(self):
        for scooter in self.scooters:
            scooter.draw(self.scooter_surface)
            next_point = self.checkpoints[scooter.next_checkpoint]
            pygame.draw.line(self.scooter_surface, TRAN_BLUE, scooter.pos.to_tuple(), next_point[0].to_tuple(), 2)

    def draw_checkpoints(self):
        for checkpoint in self.checkpoints:
            pygame.draw.circle(self.tran_surface, TRAN_BLUE, (checkpoint[0].x, self.screen_size[1] - checkpoint[0].y), checkpoint[1])

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
    
    def get_state(self, scooter: Scooter):
        # [ danger_fwd, danger_left, danger_right, heading_sin, heading_cos, checkpoint_up, checkpout_right, checkpoint_down, checkpoint_left ]
        danger_fwd = scooter.raycast(scooter.heading, self.course)
        danger_left = scooter.raycast(normalize_angle(scooter.heading - math.pi / 4.0), self.course)
        danger_right = scooter.raycast(normalize_angle(scooter.heading + math.pi / 4.0), self.course)
        heading_sin = math.sin(scooter.heading)
        heading_cos = math.cos(scooter.heading)
        checkpoint_diff = self.checkpoints[scooter.next_checkpoint][0].sub(scooter.pos)
        checkpoint_up = checkpoint_diff.y > 0
        checkpoint_right = checkpoint_diff.x > 0
        checkpoint_down = checkpoint_diff.y < 0
        checkpoint_left = checkpoint_diff.x < 0

        pygame.draw.line(self.scooter_surface, RED, scooter.pos.to_tuple(), danger_fwd[0].to_tuple(), 2)
        pygame.draw.circle(self.scooter_surface, RED, danger_fwd[0].to_int_tuple(), 3)
        pygame.draw.line(self.scooter_surface, RED, scooter.pos.to_tuple(), danger_left[0].to_tuple(), 2)
        pygame.draw.circle(self.scooter_surface, RED, danger_left[0].to_int_tuple(), 3)
        pygame.draw.line(self.scooter_surface, RED, scooter.pos.to_tuple(), danger_right[0].to_tuple(), 2)
        pygame.draw.circle(self.scooter_surface, RED, danger_right[0].to_int_tuple(), 3)

        return (danger_fwd[1], danger_left[1], danger_right[1], heading_sin, heading_cos, checkpoint_up, checkpoint_right, checkpoint_down, checkpoint_left)


Game().start()
