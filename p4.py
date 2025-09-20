import pygame
from random import *

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 500, 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Sprite Game')
clock = pygame.time.Clock()
score = 0
font = pygame.font.SysFont('Sans serif', 35)

bg_colors = [(0, 0, 0), (20, 40, 60), (60, 20, 40), (40, 60, 20)]
bg_index = randint(0, 3)

class Particle:
    def __init__(self, x, y, color, radius_range=(2, 5), lifetime=20):
        self.x = x
        self.y = y
        self.color = color
        self.radius = uniform(*radius_range)
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.vx = uniform(-1.5, 1.5)
        self.vy = uniform(-1.5, 1.5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.radius -= 0.1

    def draw(self, surface):
        if self.lifetime > 0 and self.radius > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            color = pygame.Color(self.color)
            color.a = alpha
            
            particle_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color, (self.radius, self.radius), self.radius)
            surface.blit(particle_surf, (self.x - self.radius, self.y - self.radius))

class Sprite(pygame.sprite.Sprite):
    def __init__(self, radius, color, glow_size=14):
        super().__init__()

        self.radius = radius
        self.color = color
        diameter = radius * 2

        self.image = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        try:
            draw_color = pygame.Color(color)
        except ValueError:
            draw_color = pygame.Color('white')
        pygame.draw.circle(self.image, draw_color, (radius, radius), radius)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.glow_margin = glow_size
        self.glow = self._make_glow_surface(color, glow_size)

    def _make_glow_surface(self, color, glow_size):
        try:
            c = pygame.Color(color)
        except ValueError:
            c = pygame.Color('white')
        diameter = self.radius * 2
        gw, gh = diameter + glow_size * 2, diameter + glow_size * 2
        surf = pygame.Surface((gw, gh), pygame.SRCALPHA)
        center = gw // 2

        for i in range(glow_size, 0, -1):
            alpha = int(180 * (i / glow_size) ** 2)
            col = (c.r, c.g, c.b, alpha)
            pygame.draw.circle(surf, col, (center, center), self.radius + i)
        return surf

    def player_control(self, x_change, y_change):
        max_x = SCREEN_WIDTH - self.rect.width
        max_y = SCREEN_HEIGHT - self.rect.height
        self.rect.x = max(min(self.rect.x + x_change, max_x), 0)
        self.rect.y = max(min(self.rect.y + y_change, max_y), 0)

all_sprites_list = pygame.sprite.Group()
sprites_color_list = ['red', 'green', 'yellow', 'blue', 'lightblue', 'orange']
sprite_colors = sample(sprites_color_list, 2)
sp1 = Sprite(25, sprite_colors[0], glow_size=16)
sp2 = Sprite(25, sprite_colors[1], glow_size=16)

sp1.rect.x, sp1.rect.y = randint(0, SCREEN_WIDTH - sp1.rect.width), randint(0, SCREEN_HEIGHT - sp1.rect.height)
sp2.rect.x, sp2.rect.y = randint(0, SCREEN_WIDTH - sp2.rect.width), randint(0, SCREEN_HEIGHT - sp2.rect.height)
sprite_speed = 5

all_sprites_list.add(sp1, sp2)
particles = []

running = True
text = font.render(f'Score: {score}', True, ('#f4f4f9'))
text_rect = text.get_rect(topleft=(10,10)) 

while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_x):
            running = False

    key = pygame.key.get_pressed()
    x_change = ((key[pygame.K_RIGHT] - key[pygame.K_LEFT]) + (key[pygame.K_d] - key[pygame.K_a])) * sprite_speed
    y_change = ((key[pygame.K_DOWN] - key[pygame.K_UP]) + (key[pygame.K_s] - key[pygame.K_w])) * sprite_speed
    sp1.player_control(x_change, y_change)

    if x_change != 0 or y_change != 0:
        for _ in range(2):
            particles.append(Particle(sp1.rect.centerx, sp1.rect.centery, sp1.color))

    screen.fill(bg_colors[bg_index])

    for p in particles[:]:
        p.update()
        p.draw(screen)
        if p.lifetime <= 0 or p.radius <= 0:
            particles.remove(p)

    for s in all_sprites_list:
        screen.blit(s.glow, (s.rect.x - s.glow_margin, s.rect.y - s.glow_margin))
        screen.blit(s.image, s.rect)

    if pygame.sprite.collide_mask(sp1, sp2):
        print("Boom!")
        score += 1
        text = font.render(f'Score: {score}', True, ('#f4f4f9'))
        bg_index = (bg_index + 1) % len(bg_colors)
        sp2.rect.x, sp2.rect.y = randint(0, SCREEN_WIDTH - sp2.rect.width), randint(0, SCREEN_HEIGHT - sp2.rect.height)
        while pygame.sprite.collide_mask(sp1, sp2):
             sp2.rect.x, sp2.rect.y = randint(0, SCREEN_WIDTH - sp2.rect.width), randint(0, SCREEN_HEIGHT - sp2.rect.height)

    screen.blit(text, text_rect)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
