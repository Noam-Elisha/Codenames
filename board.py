from PIL import Image
from PIL import ImageDraw
from random import *

class Board():
	board = None
	colorBoard = None
	starter = None

	def __init__(self):
		bluenum = 0
		rednum = 0
		blanknum = 7

		if randint(0,1) == 1:
			bluenum = 8
			rednum = 9
			starter = "red"
		else:
			bluenum = 9
			rednum = 8
			starter = "blue"
		deathCard = False

		board = [[None]*5 for x in range(5)]
		colorBoard = [[None]*5 for x in range(5)]

		i = randint(0,4)
		j = randint(0,4)
		board[i][j] = 1


		while rednum > 0:
			while True:
				i = randint(0,4)
				j = randint(0,4)
				if board[i][j] == None:
					board[i][j] = 2
					break
			rednum -= 1

		while bluenum > 0:
			while True:
				i = randint(0,4)
				j = randint(0,4)
				if board[i][j] == None:
					board[i][j] = 3
					break
			bluenum -= 1

		for i in range(5):
			for j in range(5):
				temp = board[i][j]
				if temp == None:
					board[i][j] = 0
				temp = board[i][j]
				if temp == 0:
					colorBoard[i][j] = (225, 198, 153)
				elif temp == 1:
					colorBoard[i][j] = (0,0,0)
				elif temp == 2:
					colorBoard[i][j] = (255,0,0)
				elif temp == 3:
					colorBoard[i][j] = (0,0,255)
		self.board = board
		self.colorBoard = colorBoard
		self.starter = starter

	def createImage(self):
		img = Image.new("RGB", [1200, 1200], (181, 64, 50))
		data = img.load()
		y = -1
		for i in range(100, 1100):
			i_1 = i - 100
			x = -1
			for j in range(100, 1100):
				j_1 = j - 100
				if i_1%200 in [0,1,2,3,4,5] and i_1 > 5:
					data[i,j] = (255,255,255)
					continue
				if j_1%200 == 0:
					x += 1
				if j_1%200 in [0,1,2,3,4,5] and j_1 > 5:
					data[i,j] = (255,255,255)
					continue
				data[i,j] = self.colorBoard[y][x]
			if i_1%200 == 0:
				y += 1


		img.save("codenames_board.png")

