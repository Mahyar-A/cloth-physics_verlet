import pygame as pg
from pygame.math import Vector2

import sys, math

# Constants
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
# Config
FPS = 30


def distance(p1, p2):
    # math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2) => slightly slower
    return math.sqrt((p2.x - p1.x) * (p2.x - p1.x) + (p2.y - p1.y) * (p2.y - p1.y))


class Point:
    def __init__(self, position):
        self.position = position
        self.prevPosition = position
        self.locked = False


class Stick:
    def __init__(self, pointA, pointB):
        self.pointA = pointA
        self.pointB = pointB
        self.length = distance(pointA.position, pointB.position)


class Cloth:
    def __init__(self, points, connections):
        self.points = points
        self.sticks = self.createSticks(connections)
        # the higher the iteration the stiffer the rope/cloth simulation
        self.numberOfIteration = 5
        self.gravity = Vector2(0, 25)

    def createSticks(self, connections):
        sticks = []
        for connection in connections:
            pointA = [point for point in self.points if point.position == connection[0]][0]
            pointB = [point for point in self.points if point.position == connection[1]][0]
            sticks.append(Stick(pointA, pointB))

        return sticks

    def verletIntegrate(self, dt):
        for point in self.points:
            if not point.locked:
                posBeforeUpdate = point.position
                point.position = 2 * point.position - point.prevPosition + self.gravity * dt
                point.prevPosition = posBeforeUpdate

    def applyConstraints(self):
        for stick in self.sticks:
            delta = stick.pointB.position - stick.pointA.position
            dist = distance(stick.pointA.position, stick.pointB.position)
            diff = (stick.length - dist) / dist / 2
            if not stick.pointA.locked:
                stick.pointA.position -= delta * diff
            if not stick.pointB.locked:
                stick.pointB.position += delta * diff

    def render(self):
        pass

    def drawDebugLines(self, surface):
        mousePress = pg.mouse.get_pressed()

        for i, stick in sorted(enumerate(self.sticks), reverse=True):
            rect = pg.draw.line(surface, WHITE, stick.pointA.position, stick.pointB.position)
            if rect.collidepoint(pg.mouse.get_pos()) and mousePress[2]:
                self.sticks.pop(i)

        for point in self.points:
            if point.locked:
                rect = pg.draw.circle(surface, RED, point.position, 5)
                if rect.collidepoint(pg.mouse.get_pos()) and mousePress[0]:
                    point.position = Vector2(pg.mouse.get_pos())

    def update(self, dt=1):
        self.verletIntegrate(dt)
        for _ in range(self.numberOfIteration):
            self.applyConstraints()


def main():
    pg.init()
    pg.display.set_caption("Cloth Physics??")

    window = pg.display.set_mode((800, 600))
    mainClock = pg.time.Clock()

    numOfPointsX = 30
    numOfPointsY = 20
    spaceBetweenPoints = 20
    offset = Vector2((window.get_width() / 2) - ((numOfPointsX / 2) * spaceBetweenPoints), 50)

    points = []
    connections = []

    for i in range(numOfPointsX):
        for j in range(numOfPointsY):
            x = offset.x + i * spaceBetweenPoints
            y = offset.y + j * spaceBetweenPoints
            points.append(Point(Vector2(x, y)))

            if j != numOfPointsY - 1:
                connections.append([Vector2(x, y), Vector2(x, y + spaceBetweenPoints)])

            if i != numOfPointsX - 1:
                connections.append([Vector2(x, y), Vector2(x + spaceBetweenPoints, y)])

    points[0].locked = True
    points[(numOfPointsX // 4) * numOfPointsY].locked = True
    points[(numOfPointsX // 2) * numOfPointsY].locked = True
    points[(3 * numOfPointsX // 4) * numOfPointsY].locked = True
    points[(numOfPointsX - 1) * numOfPointsY].locked = True

    myCloth = Cloth(points, connections)

    while True:
        dt = mainClock.tick(FPS) / 1000

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()

        window.fill(BLACK)

        myCloth.update(dt)
        myCloth.drawDebugLines(window)

        pg.display.set_caption(f"fps: {mainClock.get_fps()}")
        pg.display.update()


if __name__ == "__main__":
    main()
