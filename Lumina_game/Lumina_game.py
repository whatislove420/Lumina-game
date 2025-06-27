import os
import pygame
import random
import time
game_music_volume = 1.0

class Settings:
    WINDOW = pygame.rect.Rect(400, 0, 1200, 700)
    FPS = 60
    FILE_PATH = os.path.dirname(os.path.abspath(__file__))
    IMAGE_PATH = os.path.join(FILE_PATH, "images")
    MUSIC_PATH = os.path.join(FILE_PATH, "music")


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        original_image = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "Baum.png")).convert_alpha()
        original_rect = original_image.get_rect()
        new_size = (original_rect.width // 2, original_rect.height // 2)
        self.image = pygame.transform.scale(original_image, new_size)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = [pygame.image.load(os.path.join(Settings.IMAGE_PATH, f"Rabe{i}.png")).convert_alpha() for i in range(1, 5)]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(0, Settings.WINDOW.width), random.randint(0, Settings.WINDOW.height // 2))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 1
        self.animation_timer = 0
        self.animation_speed = 150
        self.paused = False
        self.respawn_timer = 0
        self.respawn_interval = 5000

    def update(self, dt, player_rect):
        if not self.paused:
            self.respawn_timer += dt
            if self.respawn_timer >= self.respawn_interval:
                self.rect.center = (random.randint(0, Settings.WINDOW.width), random.randint(0, Settings.WINDOW.height // 2))
                self.respawn_timer = 0

            if self.rect.x < player_rect.x:
                self.rect.x += self.speed
            elif self.rect.x > player_rect.x:
                self.rect.x -= self.speed

            if self.rect.y < player_rect.y:
                self.rect.y += self.speed
            elif self.rect.y > player_rect.y:
                self.rect.y -= self.speed

            self.rect.clamp_ip(pygame.Rect(0, 0, Settings.WINDOW.width, Settings.WINDOW.height))

            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.index = (self.index + 1) % len(self.images)
                self.image = self.images[self.index]
                self.mask = pygame.mask.from_surface(self.image)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = [pygame.image.load(os.path.join(Settings.IMAGE_PATH, f"Gluewuermchen{i}.png")).convert_alpha() for i in range(1, 3)]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(Settings.WINDOW.centerx, Settings.WINDOW.bottom - 50))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed_x = 0
        self.speed_y = 0
        self.animation_timer = 0
        self.animation_speed = 200
        self.health = 4
        self.paused = False

    def update(self, dt):
        if not self.paused:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            self.rect.clamp_ip(pygame.Rect(0, 0, Settings.WINDOW.width, Settings.WINDOW.height))

            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.index = 1 - self.index
                self.image = self.images[self.index]
                self.mask = pygame.mask.from_surface(self.image)

    def handle_input(self, keys):
        self.speed_x = (-2 if keys[pygame.K_LEFT] else 2 if keys[pygame.K_RIGHT] else 0)
        self.speed_y = (-2 if keys[pygame.K_UP] else 2 if keys[pygame.K_DOWN] else 0)

    def draw_health_bar(self, screen):
        bar_width, bar_height = 200, 20
        x, y = 10, 10
        fill_width = bar_width * (self.health / 4)
        pygame.draw.rect(screen, (0, 0, 0), (x - 2, y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(screen, (169, 169, 169), (x, y, bar_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 0), (x, y, fill_width, bar_height))

        font = pygame.font.Font(None, 28)
        text = font.render("Lichtleiste", True, (255, 255, 0))
        text_rect = text.get_rect(topleft=(x, y + bar_height + 5))
        pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(6, 6))
        screen.blit(text, (x, y + bar_height + 5))

    def draw_glow(self, screen):
        glow_radius = max(self.rect.width, self.rect.height) + 1
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 255, 0), (glow_radius, glow_radius), glow_radius)
        glow_surface.set_alpha(90)
        screen.blit(glow_surface, (self.rect.centerx - glow_radius, self.rect.centery - glow_radius))


def load_music(file):
    pygame.mixer.music.load(os.path.join(Settings.MUSIC_PATH, file))
    pygame.mixer.music.play(-1)


def show_controls_menu(screen):
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 40)
    menu_bg = pygame.image.load("menu_background.png").convert()
    menu_bg = pygame.transform.scale(menu_bg, Settings.WINDOW.size)

    instructions = [
        "ESC: Spiel beenden",
        "Pfeiltasten: Spielerbewegung",
        "P: Pause"
    ]

    back_text = small_font.render("Zurück", True, (255, 255, 255))
    back_rect = back_text.get_rect(center=(Settings.WINDOW.width // 2, Settings.WINDOW.height - 100))

    while True:
        screen.blit(menu_bg, (0, 0))

        for i, line in enumerate(instructions):
            line_render = font.render(line, True, (255, 255, 255))
            line_rect = line_render.get_rect(center=(Settings.WINDOW.width // 2, 150 + i * 70))
            screen.blit(line_render, line_rect)

        pygame.draw.rect(screen, (80, 80, 80), back_rect.inflate(30, 20))
        screen.blit(back_text, back_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and back_rect.collidepoint(event.pos):
                return


def show_volume_menu(screen):
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 40)
    menu_bg = pygame.image.load("menu_background.png").convert()
    menu_bg = pygame.transform.scale(menu_bg, Settings.WINDOW.size)

    music_volume = pygame.mixer.music.get_volume()

    slider_rect = pygame.Rect(Settings.WINDOW.width // 2 - 100, 250, 200, 20)

    dragging_slider = False

    back_text = small_font.render("Zurück", True, (255, 255, 255))
    back_rect = back_text.get_rect(center=(Settings.WINDOW.width // 2, Settings.WINDOW.height - 100))

    while True:
        screen.blit(menu_bg, (0, 0))

        title = font.render("Musik-Lautstärke", True, (255, 255, 255))
        screen.blit(title, (Settings.WINDOW.width // 2 - title.get_width() // 2, 200))
        pygame.draw.rect(screen, (100, 100, 100), slider_rect)
        pygame.draw.circle(screen, (255, 255, 0), (int(slider_rect.left + music_volume * slider_rect.width), slider_rect.centery), 10)

        pygame.draw.rect(screen, (80, 80, 80), back_rect.inflate(30, 20))
        screen.blit(back_text, back_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(event.pos):
                    return
                if slider_rect.collidepoint(event.pos):
                    dragging_slider = True
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_slider = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging_slider:
                    rel_x = event.pos[0] - slider_rect.left
                    music_volume = max(0.0, min(1.0, rel_x / slider_rect.width))
                    pygame.mixer.music.set_volume(music_volume)




def show_main_menu(screen):
    font = pygame.font.Font(None, 80)
    menu_bg = pygame.image.load("menu_background.png").convert()
    menu_bg = pygame.transform.scale(menu_bg, Settings.WINDOW.size)
    load_music("menu_music.mp3")

    menu_items = [
    {"text": "Spiel starten", "action": "start"},
    {"text": "Steuerung", "action": "options"},
    {"text": "Spiel beenden", "action": "quit"},
]

    buttons = []
    for i, item in enumerate(menu_items):
        label = font.render(item["text"], True, (255, 255, 255))
        rect = label.get_rect(center=(Settings.WINDOW.width // 2, 200 + i * 100))
        buttons.append({"rect": rect, "label": label, "action": item["action"]})

    while True:
        screen.blit(menu_bg, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        if button["action"] == "start":
                            return
                        elif button["action"] == "quit":
                            pygame.quit()
                            exit()
                        elif button["action"] == "options":
                            
                            # Neues Untermenü für Optionen
                            sub_options = True
                            while sub_options:
  
                                screen.blit(menu_bg, (0, 0))

                                option_font = pygame.font.Font(None, 60)
                                ctrl_text = option_font.render("Steuerung", True, (255, 255, 255))
                                vol_text = option_font.render("Lautstärke", True, (255, 255, 255))
                                back_text = option_font.render("Zurück", True, (255, 255, 255))

                                ctrl_rect = ctrl_text.get_rect(center=(Settings.WINDOW.width // 2, 250))
                                vol_rect = vol_text.get_rect(center=(Settings.WINDOW.width // 2, 350))
                                back_rect = back_text.get_rect(center=(Settings.WINDOW.width // 2, 450))

                                pygame.draw.rect(screen, (70, 70, 70), ctrl_rect.inflate(30, 20))
                                pygame.draw.rect(screen, (70, 70, 70), vol_rect.inflate(30, 20))
                                pygame.draw.rect(screen, (70, 70, 70), back_rect.inflate(30, 20))

                                screen.blit(ctrl_text, ctrl_rect)
                                screen.blit(vol_text, vol_rect)
                                screen.blit(back_text, back_rect)

                                pygame.display.flip()

                                for sub_event in pygame.event.get():
                                    if sub_event.type == pygame.QUIT:
                                        pygame.quit()
                                        exit()
                                    if sub_event.type == pygame.MOUSEBUTTONDOWN:
                                        if ctrl_rect.collidepoint(sub_event.pos):
                                            show_controls_menu(screen)
                                        elif vol_rect.collidepoint(sub_event.pos):
                                            show_volume_menu(screen)
                                        elif back_rect.collidepoint(sub_event.pos):
                                            sub_options = False




        for button in buttons:
            pygame.draw.rect(screen, (70, 70, 70), button["rect"].inflate(30, 20))
            screen.blit(button["label"], button["rect"])

        pygame.display.flip()


def main():
    os.environ["SDL_VIDEO_WINDOW_POS"] = "10, 50"
    screen = pygame.display.set_mode(Settings.WINDOW.size)
    pygame.display.set_caption("Lumina")
    clock = pygame.time.Clock()
    background = pygame.image.load("Background.png").convert_alpha()
    background = pygame.transform.scale(background, Settings.WINDOW.size)
    font = pygame.font.Font(None, 100)
    small_font = pygame.font.Font(None, 50)
    load_music("game_music.mp3")
    pygame.mixer.music.set_volume(game_music_volume)

    def draw_game_over_buttons():
        retry_text = small_font.render("Retry", True, (255, 255, 255))
        retry_rect = retry_text.get_rect(center=(Settings.WINDOW.width // 2, Settings.WINDOW.height // 2 + 50))
        menu_text = small_font.render("Main Menu", True, (255, 255, 255))
        menu_rect = menu_text.get_rect(center=(Settings.WINDOW.width // 2, Settings.WINDOW.height // 2 + 120))

        pygame.draw.rect(screen, (100, 100, 100), retry_rect.inflate(40, 20))
        pygame.draw.rect(screen, (100, 100, 100), menu_rect.inflate(40, 20))
        screen.blit(retry_text, retry_rect)
        screen.blit(menu_text, menu_rect)

        return retry_rect, menu_rect

    while True:
        player = Player()
        enemy = Enemy()
        obstacles = pygame.sprite.Group()
        for _ in range(10):
            while True:
                x = random.randint(0, Settings.WINDOW.width - 64)
                y = random.randint(0, Settings.WINDOW.height - 64)
                new_obstacle = Obstacle(x, y)
                if new_obstacle.rect.colliderect(player.rect) or new_obstacle.rect.colliderect(enemy.rect):
                    continue
                if any(o.rect.colliderect(new_obstacle.rect) for o in obstacles):
                    continue
                obstacles.add(new_obstacle)
                break

        paused = False
        running = True
        game_over = False
        show_menu = False

        pause_text = font.render("Pause", True, (200, 200, 200))
        pause_text_rect = pause_text.get_rect(center=(Settings.WINDOW.width // 2, Settings.WINDOW.height // 2))
        game_over_text = font.render("Game Over", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(Settings.WINDOW.width // 2, Settings.WINDOW.height // 2 - 50))

        while running:
            dt = clock.tick(Settings.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                if game_over and event.type == pygame.MOUSEBUTTONDOWN:
                    if retry_rect.collidepoint(event.pos):
                        running = False
                    elif menu_rect.collidepoint(event.pos):
                        show_menu = True
                        running = False

            keys = pygame.key.get_pressed()
            if not game_over:
                if keys[pygame.K_p]:
                    paused = not paused
                    time.sleep(0.2)
                if not paused:
                    player.handle_input(keys)
                    old_rect = player.rect.copy()
                    player.update(dt)
                    if pygame.sprite.spritecollide(player, obstacles, False, pygame.sprite.collide_mask):
                        player.rect = old_rect
                    old_enemy_rect = enemy.rect.copy()
                    enemy.update(dt, player.rect)
                    if pygame.sprite.spritecollide(enemy, obstacles, False, pygame.sprite.collide_mask):
                        enemy.rect = old_enemy_rect
                    if pygame.sprite.collide_mask(player, enemy):
                        player.health -= 1
                        enemy.rect.center = (
                            random.randint(0, Settings.WINDOW.width),
                            random.randint(0, Settings.WINDOW.height // 2),
                        )
                        enemy.respawn_timer = 0
                        if player.health <= 0:
                            game_over = True
                            

            screen.blit(background, (0, 0))
            obstacles.draw(screen)
            player.draw_glow(screen)
            screen.blit(player.image, player.rect)
            screen.blit(enemy.image, enemy.rect)
            player.draw_health_bar(screen)

            if paused:
                overlay = pygame.Surface(Settings.WINDOW.size)
                overlay.set_alpha(100)
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (0, 0))
                screen.blit(pause_text, pause_text_rect)

            if game_over:
                overlay = pygame.Surface(Settings.WINDOW.size)
                overlay.set_alpha(150)
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (0, 0))
                screen.blit(game_over_text, game_over_rect)
                retry_rect, menu_rect = draw_game_over_buttons()

            pygame.display.flip()

        if show_menu:
            show_main_menu(screen)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(Settings.WINDOW.size)
    pygame.display.set_caption("Lumina Hauptmenü")
    show_main_menu(screen)
    main()
