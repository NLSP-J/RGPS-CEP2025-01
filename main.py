import pygame as pg
import random
import asyncio
# import os

pg.init()
clock = pg.time.Clock()

# Window
WIN_WIDTH, WIN_HEIGHT = 800, 600
screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pg.display.set_caption("Falling Debris")

# Colors
BLACK = (0, 0, 0)
RED = (200, 0, 0)
WHITE = (255, 255, 255)

# Fonts
font = pg.font.Font(None, 36)
live_font = pg.font.Font(None, 48)
input_font = pg.font.Font(None, 48)

# Load images
player_image_original = pg.image.load("./assets/images/mario.png")
obj_img_original = pg.image.load("./assets/images/Thing.png")
bg_image = pg.image.load("./assets/images/background.png")
bg_image = pg.transform.scale(bg_image, (WIN_WIDTH, WIN_HEIGHT))

LEADERBOARD_FILE = "leaderboard.txt"


# ---------------- PLAYER ----------------
class Player:
    def __init__(self):
        self.size = 40
        self.speed = 20
        self.image = pg.transform.scale(player_image_original, (self.size, self.size))
        self.pos = [WIN_WIDTH // 2 - self.size // 2, WIN_HEIGHT - self.size]
        self.lives = 3

    def draw(self):
        screen.blit(self.image, self.pos)

    def move(self, dx):
        self.pos[0] += dx
        self.pos[0] = max(0, min(self.pos[0], WIN_WIDTH - self.size))

    def grow(self, amount=10):
        old_center_x = self.pos[0] + self.size // 2
        self.size += amount
        self.image = pg.transform.scale(player_image_original, (self.size, self.size))
        self.pos = [old_center_x - self.size // 2, WIN_HEIGHT - self.size]

    def get_rect(self):
        return pg.Rect(self.pos[0], self.pos[1], self.size, self.size)


# ---------------- FALLING OBJECT ----------------
class FallingObject:
    def __init__(self, kind="normal"):
        self.size = 100
        self.x = random.randint(0, WIN_WIDTH - self.size)
        self.y = 0
        self.kind = kind
        if kind == "normal":
            self.image = pg.transform.scale(obj_img_original, (self.size, self.size))
        elif kind == "live":
            self.image = live_font.render("LIVE", True, RED)

    def update(self, speed):
        self.y += speed
        screen.blit(self.image, (self.x, self.y))

    def off_screen(self):
        return self.y > WIN_HEIGHT

    def get_rect(self):
        if self.kind == "normal":
            return pg.Rect(self.x, self.y, self.size, self.size)
        else:
            return self.image.get_rect(topleft=(self.x, self.y))


# ---------------- GAME ----------------
def reset_game():
    return {
        "player": Player(),
        "objects": [],
        "score": 0,
        "fall_speed": 8,
        "game_over": False,
    }


# def load_leaderboard():
#     # if not os.path.exists(LEADERBOARD_FILE):
#     #     return []
#     with open(LEADERBOARD_FILE, "r") as f:
#         lines = f.readlines()
#     leaderboard = []
#     for line in lines:
#         name, score = line.strip().split(",")
#         leaderboard.append((name, int(score)))
#     leaderboard.sort(key=lambda x: x[1], reverse=True)
#     return leaderboard[:5]  # top 5


# def save_leaderboard(name, score):
#     leaderboard = load_leaderboard()
#     leaderboard.append((name, score))
#     leaderboard.sort(key=lambda x: x[1], reverse=True)
#     leaderboard = leaderboard[:5]
#     with open(LEADERBOARD_FILE, "w") as f:
#         for n, s in leaderboard:
#             f.write(f"{n},{s}\n")


# ---------------- GET PLAYER NAME ----------------
# def get_player_name():
#     name = ""
#     entering = True
#     while entering:
#         screen.fill(WHITE)
#         text = input_font.render("Enter Your Name: " + name, True, BLACK)
#         screen.blit(text, (WIN_WIDTH // 2 - 200, WIN_HEIGHT // 2))
#         pg.display.flip()
#         for event in pg.event.get():
#             if event.type == pg.QUIT:
#                 pg.quit()
#                 exit()
#             if event.type == pg.KEYDOWN:
#                 if event.key == pg.K_RETURN and name.strip() != "":
#                     entering = False
#                     break
#                 elif event.key == pg.K_BACKSPACE:
#                     name = name[:-1]
#                 else:
#                     if len(name) < 10:
#                         name += event.unicode
#     return name


# ---------------- MAIN ----------------
running = True

async def main():
    # player_name = get_player_name()
    game = reset_game()
    
    global running
    
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif game["game_over"] and event.type == pg.KEYDOWN:
                running = False

        # Draw background
        screen.blit(bg_image, (0, 0))

        if not game["game_over"]:
            player = game["player"]
            player.draw()

            # Smooth movement
            keys = pg.key.get_pressed()
            if keys[pg.K_LEFT]:
                player.move(-player.speed // 2)
            if keys[pg.K_RIGHT]:
                player.move(player.speed // 2)

            # Score + lives display
            score_text = font.render(f"Score: {game['score']}", True, BLACK)
            lives_text = font.render(f"Lives: {player.lives}", True, RED)
            screen.blit(score_text, (20, 20))
            screen.blit(lives_text, (20, 60))

            # Spawn objects
            if len(game["objects"]) < 10 and random.random() < 0.05:
                if random.random() < 0.1:
                    game["objects"].append(FallingObject("live"))
                else:
                    game["objects"].append(FallingObject("normal"))

            # Update objects
            for obj in game["objects"][:]:
                obj.update(game["fall_speed"])
                if obj.off_screen():
                    game["objects"].remove(obj)
                    game["score"] += 1
                    game["fall_speed"] += 0.15
                    if game["score"] % 5 == 0:
                        player.grow(10)

            # Collision
            for obj in game["objects"][:]:
                if player.get_rect().colliderect(obj.get_rect()):
                    if obj.kind == "normal":
                        player.lives -= 1
                    elif obj.kind == "live":
                        player.lives += 1
                    game["objects"].remove(obj)
                    if player.lives <= 0:
                        game["game_over"] = True
                        # save_leaderboard(player_name, game["score"])

        else:
            text = font.render(f"GAME OVER! Final Score: {game['score']}", True, BLACK)
            screen.blit(text, (WIN_WIDTH // 2 - 150, WIN_HEIGHT // 2))

            # Show top scores
            # leaderboard = load_leaderboard()
            # for i, (n, s) in enumerate(leaderboard):
            #     lb_text = font.render(f"{i+1}. {n}: {s}", True, RED)
            #     screen.blit(lb_text, (WIN_WIDTH // 2 - 100, WIN_HEIGHT // 2 + 40 + i*30))

            text2 = font.render("Press any key to exit", True, RED)
            screen.blit(text2, (WIN_WIDTH // 2 - 140, WIN_HEIGHT // 2 + 200))

        pg.display.flip()
        clock.tick(30)
        await asyncio.sleep(0)

    pg.quit()


asyncio.run(main())


