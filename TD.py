import pygame as pygame
import math
pygame.init()

width, height = 2560, 1440
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN, pygame.RESIZABLE)

clock = pygame.time.Clock()
test_surface = pygame.Surface((200,400))
test_surface.fill((100, 100, 100))
sky = pygame.image.load("Images/20.png").convert()
player = pygame.image.load("Images/16.png").convert_alpha()
font = pygame.font.Font("Fonts/SUBWT.ttf", 35)
font2 = pygame.font.Font("Fonts/Minecraft.ttf", 35)
testtext = font.render("I am Kled! High Major Commodore of the First Legion Third Multiplication Double Admiral Artillery Vanguard Company! You will respect my authority!", False, "yellow")
testtext2 = font2.render("I am Kled! High Major Commodore of the First Legion Third Multiplication Double Admiral Artillery Vanguard Company! You will respect my authority!", True, "red")
enemy = pygame.image.load("images/2.png").convert()
enemy_xposition = 1800

pygame.display.set_caption("Display")
pygame.display.set_icon(pygame.image.load("Images/test.png").convert_alpha())

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((255, 255, 255))
    screen.blit(test_surface, (200,100))
    screen.blit(sky, (400, 200))
    screen.blit(player, (0, 430))
    screen.blit(testtext, (0, 100))
    screen.blit(testtext2, (0, 140))
    enemy_xposition -= 4
    if enemy_xposition < 0: enemy_xposition = 1800
    screen.blit(enemy, (enemy_xposition, 800))

    pygame.display.update()
    clock.tick(60)
pygame.quit()