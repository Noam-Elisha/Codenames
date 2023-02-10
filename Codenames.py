from random import *
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pygame
from board import *

b = Board()
board = b.board
colorBoard = b.colorBoard
starter = b.starter
b.createImage()


pygame.init()
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
done = False
receiver_email = []
quit = False
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
                    if text in ["done", '"done"', "Done", '"Done"']:
                    	done = True
                    	break
                    receiver_email.append(text)
                    text = ''
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

    screen.fill((255, 255, 255))
    # Render the current text.
    txt_surface = font.render(text, True, color)
    # Resize the box if the text is too long.
    width = max(400, txt_surface.get_width()+10)
    input_box.w = width
    # Blit the text.
    screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
    # Blit the input_box rect.
    pygame.draw.rect(screen, color, input_box, 2)

    textsurface = font.render("Enter hint-givers emails to send them the hidden board:", True, (0,0,0))
    text_rect = textsurface.get_rect(center = (500, 127//2*5 - 100))
    screen.blit(textsurface, text_rect)

    textsurface = font.render("note: the board can also be found", True, (0,0,0))
    text_rect = textsurface.get_rect(center = (500, 127//2*5 + 250))
    screen.blit(textsurface, text_rect)

    textsurface = font.render("in the folder from where the game was launched", True, (0,0,0))
    text_rect = textsurface.get_rect(center = (500, 127//2*5 + 280))
    screen.blit(textsurface, text_rect)

    font = pygame.font.SysFont('Helvetica', 20)
    textsurface = font.render('Enter "done" to continue', True, (0,0,0))
    text_rect = textsurface.get_rect(center = (500, 127//2*5 - 50))
    screen.blit(textsurface, text_rect)

    pygame.display.flip()
    clock.tick(30)

if quit:
	exit()


subject = "Codenames Hint-Giver Sheet"
body = "The grid is attached. " + starter + " goes first."
sender_email = "noam.codenames@gmail.com"
password = "codenames_gmail"
message = []
for i in range(len(receiver_email)):
	message.append(MIMEMultipart())
	message[i]["From"] = sender_email
	message[i]["To"] = receiver_email[i]
	message[i]["Subject"] = subject
	message[i].attach(MIMEText(body, "plain"))
filename = "codenames_board.png"
with open(filename, "rb") as attachment:
	part = MIMEBase("application", "octet-stream")
	part.set_payload(attachment.read())
encoders.encode_base64(part)
part.add_header(
    "Content-Disposition",
    "attachment; filename= codenames_board.png"
)
for x in message:
	x.attach(part)
	text = x.as_string()
# Log in to server using secure context and send email
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    for x in receiver_email:
    	server.sendmail(sender_email, x, text)


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

blueList = pygame.sprite.Group()
redList = pygame.sprite.Group()
blackList = pygame.sprite.Group()
blankList = pygame.sprite.Group()
cardList = pygame.sprite.Group()
allSprites = pygame.sprite.Group()
coverList = pygame.sprite.Group()

mouse = Block((255,0,0), 0, 0)

allSprites.add(mouse)
with open('word_list.txt') as f:
	words = f.readlines()
card = pygame.image.load('codenames_blank_temp.jpg').convert_alpha()
for i in range(5):
	for j in range(5):

		cardi = Card((100 + 200*i, 127//2 + 127*j), words.pop(randint(0,len(words)))[:-1])
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

done = False
 
# Used to manage how fast the screen updates
firstCollision = False
font = pygame.font.SysFont('Comic Sans MS', 20)
while not done:
    pos = pygame.mouse.get_pos()

    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            done = True

        if event.type == pygame.MOUSEBUTTONDOWN:
        	if len(pygame.sprite.spritecollide(mouse, coverList, False)) == 0:
        		temp = pygame.sprite.spritecollide(mouse, cardList, False)
        		cardx = temp[0].rect.x + 100
        		cardy = temp[0].rect.y + 127//2
        		boardi = (cardx - 100) // 200
        		boardj = (cardy - 127//2) // 127
        		tempCover = Cover((cardx, cardy), colorBoard[boardi][boardj])
        		coverList.add(tempCover)
        		firstCollision = True
        	#allSprites.add(tempCover)
 	
    # Clear the screen
    screen.fill((255,255,255))

    mouse.rect.x = pos[0]
    mouse.rect.y = pos[1]
    # Draw all the spites
    allSprites.draw(screen)

    for x in cardList:
    	textsurface = font.render(x.word, True, (0,0,0))
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
 
pygame.quit()