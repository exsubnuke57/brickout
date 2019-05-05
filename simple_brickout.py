import numpy as np
import pygame as pg
import random
import sys

pg.mixer.pre_init(44100, -16, 1, 512)
pg.init()
pg.mixer.init()
screen = pg.display.set_mode((800,600))
pg.display.set_caption('Simple Brickout')
clock = pg.time.Clock()
click = pg.mixer.Sound('beep2.wav')
brick_bounce = pg.mixer.Sound('jab.wav')
fanfare = pg.mixer.Sound('fanfare.wav')
game_over = pg.mixer.Sound('game_over.wav')

WIDTH = 800
HEIGHT = 600
BRICK_WIDTH = 50 
BRICK_HEIGHT = 15
LINES_OF_BRICKS = 10
BALL_RADIUS = 5
GREEN = (0,255,0)
YELLOW = (255,255,0)
ORANGE = (255,165,0)
RED = (255,0,0)
BLUE = (0,0,255)
AQUA = (0,255,255)
PURPLE = (255,0,255)
GRAY = (128,128,128)
BLACK = (0,0,0)
FPS = 60
PADDLE_WIDTH = 50
PADDLE_HEIGHT = 5
colors = [GREEN, YELLOW, ORANGE, RED, BLUE, AQUA, PURPLE, GRAY]
total_bricks = LINES_OF_BRICKS * int((WIDTH / PADDLE_WIDTH))
paddle_x = WIDTH / 2
PADDLE_Y = 580 
ballx = random.randint(((WIDTH/2)-(WIDTH/4)), ((WIDTH/2)+(WIDTH/4)))
bally = int(HEIGHT/2)
ballx_mv = random.choice([-4, 4])
bally_mv = 4
level = 0
paused = False

def create_bricks():							# Makes assumption that bricks numeric array starts with all bricks present
	for line in range(LINES_OF_BRICKS):
		for brick in range(int(WIDTH / BRICK_WIDTH)):
			color = random.choice(colors)
			bricks_obj[line][brick] = pg.draw.rect(screen, color, (BRICK_WIDTH*brick,BRICK_HEIGHT* line,BRICK_WIDTH-3, BRICK_HEIGHT-2))
			bricks_color[line][brick] = color 

def draw_bricks(brick_array):					# Draws bricks based on numeric array
	for line in range(LINES_OF_BRICKS):
		for brick in range(int(WIDTH / BRICK_WIDTH)):
			if bricks[line][brick] == 0:
				bricks_obj[line][brick] = pg.draw.rect(screen, BLACK, (BRICK_WIDTH*brick,BRICK_HEIGHT* line,BRICK_WIDTH-3, BRICK_HEIGHT-2))
			else:
				bricks_obj[line][brick] = pg.draw.rect(screen, bricks_color[line][brick], (BRICK_WIDTH*brick,BRICK_HEIGHT* line,BRICK_WIDTH-3, BRICK_HEIGHT-2))

def check_bricks_left(bricks, PADDLE_WIDTH, ballx_mv, bally_mv):
	dir_x, dir_y = (1, 1)
	if ballx_mv < 0:
		dir_x = -1
	if bally_mv < 0:
		dir_y = -1
	brick_count = 0
	for line in range(LINES_OF_BRICKS):
		for brick in range(int(WIDTH / BRICK_WIDTH)):
			if bricks[line][brick] == 1:
				brick_count += 1
	ball_inc = [7, 7, 8, 9]
	paddle_size = [400, 150, 100, 50]
	level_inc = [total_bricks*0.75, total_bricks*0.5, total_bricks*0.25, 0] 
	for ix in range(len(ball_inc)):
		if brick_count >= level_inc[ix]:
			ballx_mv = ball_inc[ix] * dir_x
			bally_mv = ball_inc[ix] * dir_y
			PADDLE_WIDTH = paddle_size[ix]
			level = ix
			break
	return brick_count, PADDLE_WIDTH, ballx_mv, bally_mv, level 
                                                             
def draw_paddle(paddle_x):
	pg.draw.rect(screen, BLACK, (0, PADDLE_Y - BALL_RADIUS, WIDTH, PADDLE_Y + PADDLE_HEIGHT))
	pg.draw.rect(screen, BLUE, (paddle_x, PADDLE_Y, PADDLE_WIDTH, PADDLE_HEIGHT))

def move_paddle(paddle_x, move):
	paddle_x += move
	if paddle_x < 0:
		paddle_x = 0
	if paddle_x > WIDTH - PADDLE_WIDTH:
		paddle_x = WIDTH - PADDLE_WIDTH
	return paddle_x

def draw_ball(ballx, bally, color):
	ball = pg.draw.circle(screen,color,(ballx,bally),BALL_RADIUS*2)
	return ball

def move_ball(ballx, bally, ballx_mv, bally_mv):
	ballx += ballx_mv
	bally += bally_mv
	return (ballx, bally, ballx_mv, bally_mv)

def paddle_ball_coll(ballx, bally, bally_mv, paddle_x, PADDLE_Y):		# Check if paddle hit ball
	if paddle_x <= ballx + BALL_RADIUS and paddle_x + PADDLE_WIDTH >= ballx - BALL_RADIUS:
		if PADDLE_Y <= bally + BALL_RADIUS and PADDLE_Y + PADDLE_HEIGHT >= bally - BALL_RADIUS :
			bally = PADDLE_Y - (BALL_RADIUS + 1)
			bally_mv *= -1
			wait_sound(click.play())
	return bally, bally_mv

def ball_wall_coll(ballx, bally, ballx_mv, bally_mv):
	collision = False
	if ballx < int(BALL_RADIUS) or ballx > WIDTH-10:
		ballx_mv *= -1
	if bally < int(BALL_RADIUS) or bally > HEIGHT-10:
		bally_mv *= -1
	return ballx_mv, bally_mv

def ball_out_of_bounds(bally):
	out_of_bounds = False
	if bally + BALL_RADIUS * 2 > HEIGHT:
		out_of_bounds = True
	return out_of_bounds

def ball_brick_coll(ballx, bally, bally_mv):										# Check if ball hit brick
	for line in range(LINES_OF_BRICKS):
		for brick in range(int(WIDTH / BRICK_WIDTH)):
			if bricks_obj[line][brick].bottom >= bally - BALL_RADIUS*2 and bricks_obj[line][brick].left <= ballx-BALL_RADIUS and bricks_obj[line][brick].right >= ballx+BALL_RADIUS and bricks[line][brick] == 1:
				bricks[line][brick] = 0
				bricks_obj[line][brick] = pg.draw.rect(screen, BLACK, (BRICK_WIDTH*brick,BRICK_HEIGHT* line,BRICK_WIDTH-3, BRICK_HEIGHT-2))
				bally_mv *= -1
				wait_sound(brick_bounce.play())
				break
	draw_bricks(bricks)
	return bally_mv

def remove_brick(brick_array, row, column):					# Brick was hit.  Remove brick
	bricks[row][column] = 0

def win_check(bricks):										# Check if all bricks removed
	if 1 in bricks:
		return False
	else:
		return True

def wait_sound(channel):
	while channel.get_busy():
		pass

bricks = np.ones((LINES_OF_BRICKS, int(WIDTH / BRICK_WIDTH)), int)
bricks_obj = np.empty((LINES_OF_BRICKS, int(WIDTH / BRICK_WIDTH)),dtype=object)
bricks_color = np.empty((LINES_OF_BRICKS, int(WIDTH / BRICK_WIDTH)),dtype=object)
create_bricks()
draw_paddle(paddle_x)
draw_ball(ballx, bally, colors[level])
draw_bricks(bricks)
pg.display.update()
active = True
win = False

while active:
	clock.tick(FPS)
	for event in pg.event.get():
		if event.type == pg.QUIT:
			active = False
			sys.exit()
		if event.type == pg.KEYDOWN:
			if event.key == pg.K_SPACE:
				if paused == True:
					paused = False
				else:
					paused = True	
	keys = pg.key.get_pressed()
	if keys[pg.K_LEFT]:
		paddle_x = move_paddle(paddle_x, -10)
	if keys[pg.K_RIGHT]:
		paddle_x = move_paddle(paddle_x, 10)
	if not paused:
		draw_paddle(paddle_x)			
		draw_ball(ballx, bally, BLACK)
		ballx, bally, ballx_mv, bally_mv = move_ball(ballx, bally, ballx_mv, bally_mv)
		draw_ball(ballx, bally, colors[level])
		pg.display.update()
		ballx_mv, bally_mv = ball_wall_coll(ballx, bally, ballx_mv, bally_mv)
		if ball_out_of_bounds(bally):
			active = False
		bally, bally_mv = paddle_ball_coll(ballx, bally, bally_mv, paddle_x, PADDLE_Y)
		bally_mv = ball_brick_coll(ballx, bally, bally_mv)
		bricks_left, PADDLE_WIDTH, ballx_mv, bally_mv, level = check_bricks_left(bricks, PADDLE_WIDTH, ballx_mv, bally_mv)
		if bricks_left == 0:
			active = False
			win = True

if not win:
	print('Sorry.  You lose!')
	wait_sound(game_over.play())
else:
	print('Yay!  You win!!')
	wait_sound(fanfare.play())

pg.quit()