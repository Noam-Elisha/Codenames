from random import *
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pygame
import re
import threading
from board import *
import socket
import pickle
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

global b
global done
global words
global click
click = False
action = False
done = False
quit = False
pygame.init()
pygame.display.set_caption('Codenames: Client')

screen_width = 1000
screen_height = 127 * 5
screen = pygame.display.set_mode([screen_width, screen_height])
clock = pygame.time.Clock()

input_box = pygame.Rect(500 - 200, 127//2*5 - 32, 500, 64)
color_inactive = (200,200,200)
color_active = (0,0,0)
color = color_inactive
active = False
text = ''
receiver_email = []
waiting_for_host = False
invalid_adress = False
failed_connection = False
i = 0
global firstCollision
def press(pos, send):
	global firstCollision
	global click
	mouse.rect.x = pos[0]
	mouse.rect.y = pos[1]
	temp = pygame.sprite.spritecollide(mouse, cardList, False)
	cardx = temp[0].rect.x + 100
	cardy = temp[0].rect.y + 127//2
	boardi = (cardx - 100) // 200
	boardj = (cardy - 127//2) // 127
	tempCover = Cover((cardx, cardy), colorBoard[boardi][boardj])
	coverList.add(tempCover)
	firstCollision = True
	click = True
	if send:
		s.send(pickle.dumps(pygame.mouse.get_pos()))
		s.recv(1024)

def socket_process(s):
	global words
	print('hi')
	msg = s.recv(1024)
	s.send(b"received continue")
	print("received whatever")
	global done
	done = True
	global b
	b = pickle.loads(s.recv(1024))
	s.send(b"received board")
	print(b.board)
	words = pickle.loads(s.recv(1024))
	s.send(b"received words")
	global click
	click = False
	while True:
		"""
		print(click)
		if click:
			click = False
			print(click)
			s.send(click)
			s.recv(1024)
		"""
		pos = s.recv(1024)
		pos = pickle.loads(pos)
		print(pos)
		s.send(b"received click")
		press(pos, False)


startThread = True
while not done:
    font = pygame.font.SysFont('Helvetica', 30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            quit = True
        if event.type == pygame.MOUSEBUTTONDOWN:

            # If the user clicked on the input_box rect.
            if input_box.collidepoint(event.pos):
                # Toggle the active variable.
                active = not active
            else:
                active = False
            # Change the current color of the input box.
            color = color_active if active else color_inactive
        if event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                	if not re.search("[0-9]+.[0-9]+.[0-9]+.[0-9]+", text):
                		invalid_adress = True
                		i = 1
                		text = ''
                		break

                	textsurface = font.render("Attempting to Connect to Host", False, (0,0,0))
                	text_rect = textsurface.get_rect(center = (500, 127*5 - 200))
                	screen.blit(textsurface, text_rect)

                	textsurface = font.render("This may take a little bit. Do not close the game", False, (0,0,0))
                	text_rect = textsurface.get_rect(center = (500, 127*5 - 150))
                	screen.blit(textsurface, text_rect)
                	pygame.display.flip()
                	
                	try:
                		s.connect((text, 12345))
                		x = threading.Thread(target = socket_process, args = (s,))
                		failed_connection = False
                	except:
                		i = 1
                		failed_connection = True
                	if not failed_connection:
                		#done = True
                		waiting_for_host = True
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

    screen.fill((255, 255, 255))

    if not waiting_for_host:
        # Render the current text.
        txt_surface = font.render(text, True, color)
    # Resize the box if the text is too long.
        width = max(400, txt_surface.get_width()+10)
        input_box.w = width
    # Blit the text.
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
    # Blit the input_box rect.
        pygame.draw.rect(screen, color, input_box, 2)

        textsurface = font.render("Enter your hosts IP adress:", False, (0,0,0))
        text_rect = textsurface.get_rect(center = (500, 127//2*5 - 100))
        screen.blit(textsurface, text_rect)

        if failed_connection:
        	if i > 0:
        		i += 1
        		textsurface = font.render("Connection failed. Try again", False, (0,0,0))
	        	text_rect = textsurface.get_rect(center = (500, 127*5 - 100))
	        	screen.blit(textsurface, text_rect)
	        if i > 30:
	        	i = 0
	        	failed_connection = False

        if invalid_adress:
        	if i > 0:
        		i += 1
	        	textsurface = font.render("Invalid IP adress", False, (0,0,0))
	        	text_rect = textsurface.get_rect(center = (500, 127*5 - 100))
	        	screen.blit(textsurface, text_rect)
        	if i > 30:
        		i = 0
        		invalid_adress = False
    
    else:
    	textsurface = font.render("Connection successfull", False, (0,0,0))
    	text_rect = textsurface.get_rect(center = (500, 127*5 - 100))
    	screen.blit(textsurface, text_rect)
    	textsurface = font.render("Waiting for the host to start the game", False, (0,0,0))
    	text_rect = textsurface.get_rect(center = (500, 127//2*5 - 100))
    	screen.blit(textsurface, text_rect)
    	pygame.display.flip()
    	if startThread:
    		x.start()
    		startThread = False

    pygame.display.flip()
    clock.tick(30)


if quit:
	sys.exit(0)

class Block(pygame.sprite.Sprite):

 
    def __init__(self, color, width, height):
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()

class Card(pygame.sprite.Sprite):
 	

    def __init__(self, pos, word):

        super().__init__()
        self.word = word
        self.image = card
        self.rect = self.image.get_rect(center = pos)
        

class Cover(pygame.sprite.Sprite):

	def __init__(self, pos, color):

		super().__init__()
		self.image = pygame.Surface([190, 117])
		self.image.fill(color)
		self.rect = self.image.get_rect(center = pos)

while True:
	try:
		words.keys()
		break
	except:
		pass



blueList = pygame.sprite.Group()
redList = pygame.sprite.Group()
blackList = pygame.sprite.Group()
blankList = pygame.sprite.Group()
cardList = pygame.sprite.Group()
allSprites = pygame.sprite.Group()
coverList = pygame.sprite.Group()
mouse = Block((255,0,0), 0, 0)
card = pygame.image.load('codenames_blank_temp.jpg').convert_alpha()
allSprites.add(mouse)
k = 0
board = b.board
colorBoard = b.colorBoard
for i in range(5):
	for j in range(5):
		cardi = Card(list(words.values())[k], list(words.keys())[k])
		if board[i][j] == 0:
			blankList.add(cardi)
		elif board[i][j] == 1:
			blackList.add(cardi)
		elif board[i][j] == 2:
			redList.add(cardi)
		elif board[i][j] ==3:
			blueList.add(cardi)
		allSprites.add(cardi)
		cardList.add(cardi)
		k += 1
firstCollision = False
font = pygame.font.SysFont('Comic Sans MS', 20)
done = False
def sendClick(pos):
	s.send(pickle.dumps(pos))

while not done:
    pos = pygame.mouse.get_pos()

    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            done = True
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
        	if len(pygame.sprite.spritecollide(mouse, coverList, False)) == 0:
        		click = [mouse.rect.x, mouse.rect.y]
        		s.send(pickle.dumps(click))
        		#threading.Thread(target = sendClick, args = (temp,)).start()

        	#allSprites.add(tempCover)
    # Clear the screen
    screen.fill((255,255,255))

    mouse.rect.x = pos[0]
    mouse.rect.y = pos[1]
    # Draw all the spites
    allSprites.draw(screen)

    for x in cardList:
    	textsurface = font.render(x.word, False, (0,0,0))
    	text_rect = textsurface.get_rect(center = (x.rect.x + 100, x.rect.y + 90))
    	screen.blit(textsurface, text_rect)

    reAddCover = False
    temp = pygame.sprite.spritecollide(mouse, coverList, False)
    if len(temp) == 1:
    	reAddCover = True
    	temp[0].image.set_alpha(100)

    coverList.draw(screen)
    if reAddCover:
    	temp[0].image.set_alpha(255)

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # Limit to 60 frames per second
    clock.tick(60)

s.close()
pygame.quit()
exit()