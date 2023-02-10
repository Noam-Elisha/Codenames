import pygame
import sys
import socket

IP = socket.gethostbyname(socket.gethostname())
print(IP)

pygame.init()
screen_width = 1000
screen_height = 127 * 5
screen = pygame.display.set_mode([screen_width, screen_height])
clock = pygame.time.Clock()
font = pygame.font.SysFont('Helvetica', 30)
done = False

class Button(pygame.sprite.Sprite):

	pos = None

	def __init__(self, pos, color):

		super().__init__()
		self.pos = pos
		self.image = pygame.Surface([200, 75])
		self.image.fill(color)
		self.rect = self.image.get_rect(center = pos)

class Mouse(pygame.sprite.Sprite):

	def __init__(self):

		super().__init__()
		self.image = pygame.Surface([0, 0])
		self.image.fill((0,0,0))
		self.rect = self.image.get_rect(center = (0,0))



allSprites = pygame.sprite.Group()
local = Button((350,screen_height//2), (255,0,0))
multiplayer = Button((650, screen_height//2), (0,0,255))
allSprites.add(local, multiplayer)
mouse = Mouse()
gametype = ''
while not done:
	pos = pygame.mouse.get_pos()
	mouse.rect.x = pos[0]
	mouse.rect.y = pos[1]
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit(0)
		if event.type == pygame.MOUSEBUTTONDOWN:
			click = pygame.sprite.spritecollide(mouse, allSprites, False)
			if len(click) == 0:
				continue
			if click[0] == local:
				gametype = "local"
			if click[0] == multiplayer:
				gametype = "multiplayer"
			done = True
	
	screen.fill((255,255,255))
	allSprites.draw(screen)
	textsurface = font.render("How would you like to play?", False, (0,0,0))
	text_rect = textsurface.get_rect(center = (500, 127//2*5 - 100))
	screen.blit(textsurface, text_rect)

	textsurface = font.render("Local", False, (0,0,0))
	text_rect = textsurface.get_rect(center = local.pos)
	screen.blit(textsurface, text_rect)

	textsurface = font.render("Multiplayer", False, (0,0,0))
	text_rect = textsurface.get_rect(center = multiplayer.pos)
	screen.blit(textsurface, text_rect)

	pygame.display.flip()
	clock.tick(30)


if gametype == 'local':
	from Codenames import *
	sys.exit(0)

done = False

allSprites = pygame.sprite.Group()
host = Button((350,screen_height//2), (255,0,0))
connect = Button((650, screen_height//2), (0,0,255))
allSprites.add(host, connect)
while not done:
	pos = pygame.mouse.get_pos()
	mouse.rect.x = pos[0]
	mouse.rect.y = pos[1]
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit(0)
		if event.type == pygame.MOUSEBUTTONDOWN:
			click = pygame.sprite.spritecollide(mouse, allSprites, False)
			if len(click) == 0:
				continue
			if click[0] == host:
				gametype = "host"
			if click[0] == multiplayer:
				gametype = "connect"
			done = True
	
	screen.fill((255,255,255))
	allSprites.draw(screen)
	textsurface = font.render("Would you like to host or connect", False, (0,0,0))
	text_rect = textsurface.get_rect(center = (500, 127//2*5 - 100))
	screen.blit(textsurface, text_rect)

	textsurface = font.render("Host", False, (0,0,0))
	text_rect = textsurface.get_rect(center = local.pos)
	screen.blit(textsurface, text_rect)

	textsurface = font.render("Connect", False, (0,0,0))
	text_rect = textsurface.get_rect(center = multiplayer.pos)
	screen.blit(textsurface, text_rect)

	pygame.display.flip()
	clock.tick(30)	

if gametype == "host":
	from Codenames_server import *
else:
	from Codenames_client import *


pygame.quit()