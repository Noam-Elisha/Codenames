import socket
import sys
import threading
from board import *
import pygame
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pickle

global start
start = False
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 12345
address = ('0.0.0.0', 12345)
s.bind(address)
s.setblocking(0)
s.listen()
print("waiting for connection")

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

pygame.init()
IP = socket.gethostbyname(socket.gethostname())
pygame.display.set_caption('Codenames: Host')

screen_width = 1000
screen_height = 127 * 5
screen = pygame.display.set_mode([screen_width, screen_height])
clock = pygame.time.Clock()
font = pygame.font.SysFont('Helvetica', 30)
done = False

allSprites = pygame.sprite.Group()
advance = Button((500,127*3), (0,0,0))
allSprites.add(advance)
mouse = Mouse()
connCount = 0

b = Board()
board = b.board
colorBoard = b.colorBoard
starter = b.starter
b.createImage()

def on_new_client(clientSocket, address):
	global start
	clientSocket.setblocking(1)
	mouse = Mouse()
	while True:
		if start:
			clientSocket.send(b"continue")
			clientSocket.recv(1024)
			clientSocket.send(pickle.dumps(b))
			clientSocket.recv(1024)
			start = False
			break
	while True:
		if start:
			clientSocket.send(pickle.dumps(wordList))
			clientSocket.recv(1024)
			break
	threading.Thread(target = click_check, args = (clientSocket,)).start()
	global sendClick
	sendClick = None
	while True:
		#client will only send when clicking during the game
		#use pickle library
		print(sendClick)
		if sendClick != None:
			clientSocket.send(pickle.dumps(sendClick))
			sendClick = None

def click_check(s):
	i = 0
	while True:
		temp = s.recv(1024)
		print(i, temp)
		print()
		if temp == b'received click':
			continue
		pos = pickle.loads(temp)
		#s.send(b"received click")
		press(pos, True)
		i += 1

global firstCollision
global sendClick
def press(pos, send = True):
	global firstCollision
	global click
	global sendClick
	sendClick = False
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
		sendClick = pos
		print(sendClick)

connections = []
addresses = []
while not done:
	try:
		conn, address = s.accept()
		connections.append(conn)
		addresses.append(address)
		connCount += 1
	except BlockingIOError:
		pass
	screen.fill((255,255,255))
	allSprites.draw(screen)
	pos = pygame.mouse.get_pos()
	mouse.rect.x = pos[0]
	mouse.rect.y = pos[1]
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit(0)
		if event.type == pygame.MOUSEBUTTONDOWN:
			click = pygame.sprite.spritecollide(mouse, allSprites, False)
			if len(click) > 0 and click[0] == advance:
				done = True
				for i in range(len(connections)):
					x = threading.Thread(target = on_new_client, args = (connections[i], addresses[i]))
					x.start()
				break
	
	textsurface = font.render("Your ip is {}, give this to your friends to connect".format(IP), False, (0,0,0))
	text_rect = textsurface.get_rect(center = (500,250))
	screen.blit(textsurface, text_rect)

	textsurface = font.render("Hit continue when everyone has connected", False, (0,0,0))
	text_rect = textsurface.get_rect(center = (500,290))
	screen.blit(textsurface, text_rect)

	textsurface = font.render("Continue", False, (255,255,255))
	text_rect = textsurface.get_rect(center = advance.pos)
	screen.blit(textsurface, text_rect)

	textsurface = font.render("{} connection(s) so far".format(connCount), False, (0,0,0))
	text_rect = textsurface.get_rect(center = (500,500))
	screen.blit(textsurface, text_rect)

	pygame.display.flip()
	clock.tick(30)

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
            sys.exit(0)
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
                    	start = True
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

    textsurface = font.render("Enter hint-givers emails to send them the hidden board:", False, (0,0,0))
    text_rect = textsurface.get_rect(center = (500, 127//2*5 - 100))
    screen.blit(textsurface, text_rect)

    textsurface = font.render("note: the board can also be found", False, (0,0,0))
    text_rect = textsurface.get_rect(center = (500, 127//2*5 + 250))
    screen.blit(textsurface, text_rect)

    textsurface = font.render("in the folder from where the game was launched", False, (0,0,0))
    text_rect = textsurface.get_rect(center = (500, 127//2*5 + 280))
    screen.blit(textsurface, text_rect)

    font = pygame.font.SysFont('Helvetica', 20)
    textsurface = font.render('Enter "done" to continue', False, (0,0,0))
    text_rect = textsurface.get_rect(center = (500, 127//2*5 - 50))
    screen.blit(textsurface, text_rect)

    pygame.display.flip()
    clock.tick(30)


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
        self.pos = pos
        self.rect = self.image.get_rect(center = pos)
        

class Cover(pygame.sprite.Sprite):

	def __init__(self, pos, color):

		super().__init__()
		self.image = pygame.Surface([190, 117])
		self.image.fill(color)
		self.pos = pos
		self.rect = self.image.get_rect(center = pos)

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
wordList = {}
with open('word_list.txt') as f:
	words = f.readlines()
shuffle(words)
k = 0
for i in range(5):
	for j in range(5):
		cardi = Card((100 + 200*i, 127//2 + 127*j), words[k][:-1])
		wordList[cardi.word] = cardi.pos
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
start = True

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
        		press([mouse.rect.x, mouse.rect.y], True)
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

pygame.quit()
sys.exit(0)



"""
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 12345
address = ('0.0.0.0', 12345)
s.bind(address)
s.listen()
print("waiting for connection")
while True:
	conn, address = s.accept()
	print("got connection from ", address)

	while True:
		data = conn.recv(1024).decode()
		if not data:
			break
		data = "received" + data
		conn.send(data.encode())
		print("received ", data, " from ", address)

"""