import math
import random
import pygame
import copy
import numpy as np

pygame.init()

size = (800, 800)
screen = pygame.display.set_mode(size)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

KM = 1
KD = 1
KA = 2

def f(x):
    return int((x * 0.9 + 1) * size[1] / 2.0)

class Point:
    def __init__(self, _x, _y):
        self.x = _x
        self.y = _y

    def init2(self, p):
        self.x = p.x
        self.y = p.y

    def dist(self, p):
        return ((self.x - p.x) ** 2 + (self.y - p.y) ** 2) ** 0.5

    def toLst(self):
        return [f(self.x), f(self.y)]

    def draw(self, col):
        pygame.draw.circle(screen, col, self.toLst(), int(size[1] *  0.014 / 2))

    def prod(self, b):
        return self.x * b.x + self.y * b.y

    def __mul__(self, a):
        return Point(self.x * a, self.y * a)

    def __sub__(self, b):
        return Point(self.x - b.x, self.y - b.y)
    
    def __add__(self, b):
        return Point(self.x + b.x, self.y + b.y)

    def iadd(self, b):
        self.x += b.x
        self.y += b.y
        return self

    def brown(self):
        C = float(np.sqrt(0.0005))
        self.x += float(np.random.randn()) * C
        self.y += float(np.random.randn()) * C
        
    def isub(self, b):
        self.x -= b.x
        self.y -= b.y
        return self

    def norm(self):
        d = self.dist(Point(0.0, 0.0))
        if d < 1e-2:
            return Point(0.0, 0.0)
        return Point(self.x / d, self.y / d)

    def rot(self):
        return Point(-self.y, self.x) 
    
    @staticmethod
    def get():
        p = Point(random.uniform(-1, 1), random.uniform(-1, 1))
        if (p.dist(Point(0, 0)) <= 1.0):
            return p;
        return Point.get()

class Node(Point): 
    def __init__(self, _x, _y):
        Point.__init__(self, _x, _y)
        self.a = Point(0, 0)
        self.m = 1

    def __mul__(self, a):
        return Node(self.x * a, self.y * a)
        
    def __sub__(self, b):
        return Node(self.x - b.x, self.y - b.y)
    
    def __add__(self, b):
        return Node(self.x + b.x, self.y + b.y)

    @staticmethod
    def get():
        p = Point.get()
        return Node(p.x, p.y)

    def upd(self):
        super(Node, self).init2(self + self.a)
        self.a = self.a * 0.5

    def coulomb(self, b, k):
        d = max(0.1, self.dist(b))
        A = (b - self) * (k / (d ** 3))
        self.a += A * (1.0 / self.m)
        b.a -= A * (1.0 / b.m)

class Spring2:
    def __init__(self, _a, _b, _c, _k = 0.2, _col = RED):
        self.l = _a.dist(_c)
        self.a = _a;
        self.b = _b;
        self.c = _c;
        self.col = _col
        self.k = _k
        
    def draw(self):
        if self.col != WHITE:
            pygame.draw.line(screen, self.col, self.a.toLst(), self.b.toLst(), 2)
            pygame.draw.line(screen, self.col, self.b.toLst(), self.c.toLst(), 2)

    def hook(self):
        dl = (self.a.dist(self.c) - self.l) * self.k
        v1 = (self.c - self.a).norm() * dl
        d2 = (self.b * 2.0 - self.a - self.c)
        v2 = d2 * d2.dist(Point(0.0, 0.0)) * self.k * 10
              
        self.a.a += (v1 * (1.0 / self.a.m))
        self.c.a -= (v1 * (1.0 / self.c.m))

        self.b.a -= v2
        self.a.a += v2 * 0.5
        self.c.a += v2 * 0.5
        
class Motor(Node):
    def __init__(self, _x, _y):
        Node.__init__(self, _x, _y)
        self.id = None

    @staticmethod
    def get():
        p = Point.get()
        return Motor(p.x, p.y)

    def move(self, ts):
        k = 0.002 / len(ms)
        min_dist = 0
        if len(ts):
            min_dist = 1.5 * ts[0].ps[-1].dist(ts[0].ps[0]) / len(ts[0].ps)

        km = k * KM
        ka = k * KA
        kd = k * KD
        if self.id != None:
            for t in ts:
                L = len(t.ps)
                if t is self.id:
                    ok = False
                    for i in range(L):
                        if self.dist(t.ps[i]) < min_dist:
                            if i >= 1:
                                self.coulomb(t.ps[i - 1], -km)
                            while i < L and t.ps[i].dist(self) < min_dist:
                                i += 1
                            if i + 1 < L:
                                self.coulomb(t.ps[i + 1], 2 * km)
                                
                            ok = True
                    if not ok:
                        self.id = None
                        for i in range(3):
                            self.coulomb(t.ps[-1 - i], -k)
                    return

        for t in ts:
            L = len(t.ps)
            self.coulomb(t.ps[L - 2], -kd)
            self.coulomb(t.ps[0], ka)
            if self.dist(t.ps[0]) < min_dist:
                self.id = t
        self.brown()
    

class Points:
    def __init__(self, _a = Node(0, 0), _b = Node(0, 0), L = 0):
        self.ps = []
        self.sps = []
        for i in range(L):
            self.ps.append((_a * ((L - i) / L)) + (_b * (i / L)))
            self.ps[i].m = 4
            if i >= 2:
                self.sps.append(Spring2(self.ps[i], self.ps[i - 1], self.ps[i - 2], 0.3, RED))
            if i >= 6:
                self.sps.append(Spring2(self.ps[i], self.ps[i - 3], self.ps[i - 6], 0.1, RED))
    def draw(self):
        for p in self.ps:
            p.draw(RED)
        for sp in self.sps:
            sp.draw()
        
    def hook(self):
        for x in self.sps:
            x.hook()

    def upd(self):
        for x in self.ps:
            x.upd()

class Tubule(Points):
    def __init__(self, _a, _b):
        Points.__init__(self, _a, _b, 30)
        
    def draw(self):
        L = len(self.ps)
        mx = 255
        for i in range(L):
            self.ps[i].draw((0, int((L - i) / L * mx), int(i / L * mx)))
        for x in self.sps:
            #if x.l < 0.05:
                x.draw()
            
    @staticmethod
    def get():
        p1 = Node.get()
        fi = random.uniform(0, math.pi)
        p2 = p1 + Node(math.cos(fi), math.sin(fi))
        if (p2.dist(Point(0, 0)) <= 1.0):
            if (random.random()):
                p1, p2 = p2, p1
            return Tubule(p1, p2)
        return Tubule.get()
            

class Border(Points):
    def __init__(self, N):
        Points.__init__(self)
        for i in range(N):
            fi = 2 * math.pi * i / N
            self.ps.append(Node(math.cos(fi), math.sin(fi)) * 1.014)
            self.ps[-1].m = 10
        for i in range(N):
            self.sps.append(Spring2(self.ps[i], self.ps[(i + 1) % N], self.ps[(i + 2) % N], 0.2))
            #self.sps.append(Spring2(self.ps[i], self.ps[(i + 3) % N], self.ps[(i + 6) % N], 0.4))
                
    def draw(self):
        Points.draw(self)

    def __move(self, p):
        k = 0.005 / len(ms)
        mn_dist = 2.0 * self.ps[1].dist(self.ps[0]) 
        for p1 in self.ps:
            if (p1.dist(p) < mn_dist):
                p1.coulomb(p, -k)

    def move(self, ts):
        for t in ts:
            self.__move(t.ps[0])
            self.__move(t.ps[1])
            self.__move(t.ps[-1])
            self.__move(t.ps[-2])

    def upd(self):
        for p in self.ps:
            p.a = Point(0, 0)

ms = []

def main_run():
    done = False
    clock = pygame.time.Clock()

    b = Border(100)

    ts = []
    N = 50

    images = []
    
    for _ in range(N):
        fi = random.uniform(0, 2 * math.pi)
        p = Node(math.cos(fi), math.sin(fi))
        t = Tubule.get()
        ts.append(t)

    j = 0
    M = 100
    for _ in range(M):
        m = Motor.get()
        ms.append(m)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                done = True

        if j > 3000:
            done = True

        screen.fill(WHITE)

        basicFont = pygame.font.SysFont(None, 20)
        text = basicFont.render("iter = " + str(j) + ", ka = " + str(KA) + ", kd = " + str(KD) + ", km = " + str(KM), True, WHITE, BLUE)
        textRect = text.get_rect()
        screen.blit(text, textRect)
        b.draw()
    
        for x in ts:
            x.draw()
        
        for x in ms:
            x.draw(RED)

        for m in ms:
            m.move(ts)
        for t in ts:
            t.hook()
        b.move(ts)
    
        for m in ms:
            m.upd()
        for t in ts:
            t.upd()
        b.upd()

        for i in range(len(ms)):
            if (ms[i].dist(Point(0, 0)) >= 1.0) or random.randint(0, 30) == 1:
                ms[i] = Motor.get()

        pygame.display.flip()
        if (j % 10 == 0):
            file_name = "screenshot" + str(j).rjust(5, '0') + ".png"
            pygame.image.save(screen, file_name);
            
        clock.tick(1000)
        j += 1
    pygame.quit()

main_run()
