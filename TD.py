import pygame as pygame
import math
pygame.init()

width, height = 2000, 1000
screen = pygame.display.set_mode((width, height))#, pygame.FULLSCREEN, pygame.RESIZABLE)

clock = pygame.time.Clock()

sky = pygame.image.load("Images/20.png").convert()
color = (0, 0, 0)

font = pygame.font.Font("Fonts/SUBWT.ttf", 35)
font2 = pygame.font.Font("Fonts/Minecraft.ttf", 35)

#testtext = font.render("I am Kled! High Major Commodore of the First Legion Third Multiplication Double Admiral Artillery Vanguard Company! You will respect my authority!", False, "yellow")
#testtext2 = font2.render("I am Kled! High Major Commodore of the First Legion Third Multiplication Double Admiral Artillery Vanguard Company! You will respect my authority!", True, "red")

player_surf = pygame.image.load("Images/16.png").convert_alpha()
player_rect = player_surf.get_rect(bottomleft = (0, 1000))

enemy_surf = pygame.image.load("images/2.png").convert()
enemy_rect = enemy_surf.get_rect(midbottom = (1700, 1000))

pygame.display.set_caption("Display")
pygame.display.set_icon(pygame.image.load("Images/test.png").convert_alpha())

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #screen.blit(sky, (400, 200))
    #screen.blit(testtext, (0, 100))
    #screen.blit(testtext2, (0, 140))
    screen.fill(color)


    enemy_rect.x -= 4
    if enemy_rect.right <= 0: enemy_rect.left = 2000
    screen.blit(player_surf, player_rect)
    screen.blit(enemy_surf, enemy_rect)
   
    #player_rect.left += 1

    pygame.display.update()
    clock.tick(60)
pygame.quit()