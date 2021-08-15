# Memory Puzzle
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import os, random, pathlib, pygame, sys
from pygame.locals import *
from glob import glob


FPS = 30
REVEALSPEED = 8 # speed boxes' sliding reveals and covers
BOXSIZE = 48 # size of box height & width in pixels
GAPSIZE = 10 # size of gap between boxes in pixels
BOARDWIDTH = 6 # number of columns of icons
BOARDHEIGHT = 5 # number of rows of icons
WINDOWWIDTH = (BOXSIZE * BOARDWIDTH) + (GAPSIZE * (BOARDWIDTH + 1)) + 20 # size of window's width in pixels
WINDOWHEIGHT = (BOXSIZE * BOARDHEIGHT) + (GAPSIZE * (BOARDHEIGHT + 1)) + 20 # size of window's height in pixels

assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.'
ICONSNUMB = int((BOARDWIDTH * BOARDHEIGHT)/2) # number of different icons being used

XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)

#            R    G    B
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)

BGCOLOR = NAVYBLUE
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE

def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    
    # --- adding background sound
    pygame.mixer.init()
    pygame.mixer.set_num_channels(32)
    music = [x for x in glob("sound/*.ogg")]

    pygame.mixer.music.load(random.choice(music))
    pygame.mixer.music.play(-1) # to play the music indefinitely
    # ------------------------------------------------
    
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    mousex = 0 # used to store x coordinate of mouse event
    mousey = 0 # used to store y coordinate of mouse event
    pygame.display.set_caption('Your Emoji Puzzle Game')

    main_board = randomized_board()
    revealed_boxes = generate_revealed_boxes_data(False)

    first_selection = None # stores the (x, y) of the first box clicked.

    DISPLAYSURF.fill(BGCOLOR)
    start_game_animation(main_board)

    while True: # main game loop
        mouse_clicked = False

        DISPLAYSURF.fill(BGCOLOR) # drawing the window
        draw_board(main_board, revealed_boxes)

        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouse_clicked = True
        
        boxx, boxy = get_box_at_pixel(mousex, mousey)
        if boxx != None and boxy != None:
            # The mouse is currently over a box.
            if not revealed_boxes[boxx][boxy]:
                draw_highlight_box(boxx, boxy)
            if not revealed_boxes[boxx][boxy] and mouse_clicked:
                reveal_boxes_animation(main_board, [(boxx, boxy)])
                revealed_boxes[boxx][boxy] = True # set the box as "revealed"
                if first_selection == None: # the current box was the first box clicked
                    first_selection = (boxx, boxy)
                else: # the current box was the second box clicked
                    # Check if there is a match between the two icons.
                    icon1 = get_icon(main_board, first_selection[0], first_selection[1])
                    icon2 = get_icon(main_board, boxx, boxy)

                    if icon1 != icon2:
                        # Icons don't match. Re-cover up both selections.
                        pygame.time.wait(1000) # 1000 milliseconds = 1 sec
                        cover_boxes_animation(main_board, [(first_selection[0], first_selection[1]), (boxx, boxy)])
                        revealed_boxes[first_selection[0]][first_selection[1]] = False
                        revealed_boxes[boxx][boxy] = False
                    elif has_won(revealed_boxes): # check if all pairs found
                        winning_animation(main_board)
                        pygame.time.wait(2000)

                        # Reset the board
                        main_board = randomized_board()
                        revealed_boxes = generate_revealed_boxes_data(False)

                        # Show the fully unrevealed board for a second.
                        draw_board(main_board, revealed_boxes)
                        pygame.display.update()
                        pygame.time.wait(1000)

                        # Replay the start game animation.
                        start_game_animation(main_board)
                    first_selection = None # reset firstSelection variable

        # Redraw the screen and wait a clock tick.
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def list_of_surfaces():
    dir_name = 'assets/';
    surfaces_list = []
    # get random images from assets as much as icons number
    for file in random.sample(os.listdir(dir_name), ICONSNUMB):
        a = os.path.join(dir_name, file)
        b = pathlib.Path(a)
        c = pygame.image.load(b)
        surfaces_list.append(c)
    return surfaces_list # get images list 

def generate_revealed_boxes_data(val):
    revealed_boxes = []
    for i in range(BOARDWIDTH):
        revealed_boxes.append([val] * BOARDHEIGHT)
    return revealed_boxes

def randomized_board():
    icons = list_of_surfaces() * 2 # make two of each
    random.shuffle(icons) # randomize the order of the icons list

    # Create the board data structure, with randomly placed icons.
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(icons[0])
            del icons[0] # remove the icons as we assign them
        board.append(column)
    return board

def split_into_groups_of(group_size, the_list):
    # splits a list into a list of lists, where the inner lists have at
    # most groupSize number of items.
    result = []
    for i in range(0, len(the_list), group_size):
        result.append(the_list[i:i + group_size])
    return result

def left_top_coords(boxx, boxy):
    # Convert board coordinates to pixel coordinates
    left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN
    top = boxy * (BOXSIZE + GAPSIZE) + YMARGIN
    return (left, top)

def get_box_at_pixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = left_top_coords(boxx, boxy)
            box_rect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if box_rect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)

def get_icon(board, boxx, boxy):
    return board[boxx][boxy]

def draw_icon(board, boxx, boxy):
    # get the coordinate of the box in pixel
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            x = (boxx * BOXSIZE) + ((boxx + 1) * GAPSIZE) + 5
            y = (boxy * BOXSIZE) + ((boxy + 1) * GAPSIZE) + 5
    # display the image by the coordinate
    return DISPLAYSURF.blit(board[boxx][boxy], (x, y))

def draw_box_covers(board, boxes, coverage):
    # Draws boxes being covered/revealed. "boxes" is a list
    # of two-item lists, which have the x & y spot of the box.
    for box in boxes:
        left, top = left_top_coords(box[0], box[1])
        pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
        draw_icon(board, box[0], box[1])
        if coverage > 0: # only draw the cover if there is an coverage
            pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, coverage, BOXSIZE))
    pygame.display.update()
    FPSCLOCK.tick(FPS)

def reveal_boxes_animation(board, boxes_to_reveal):
    # Do the "box reveal" animation.
    for coverage in range(BOXSIZE, (-REVEALSPEED) - 1, -REVEALSPEED):
        draw_box_covers(board, boxes_to_reveal, coverage)

def cover_boxes_animation(board, boxes_to_cover):
    # Do the "box cover" animation.
    for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
        draw_box_covers(board, boxes_to_cover, coverage)

def draw_board(board, revealed):
    # Draws all of the boxes in their covered or revealed state.
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = left_top_coords(boxx, boxy)
            if not revealed[boxx][boxy]:
                # Draw a covered box.
                pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
            else:
                # Draw the (revealed) icon.
                draw_icon(board, boxx, boxy)

def draw_highlight_box(boxx, boxy):
    left, top = left_top_coords(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 2)

def start_game_animation(board):
    # Randomly reveal the boxes 20% of icons number at a time.
    covered_boxes = generate_revealed_boxes_data(False)
    boxes = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            boxes.append( (x, y) )
    random.shuffle(boxes)
    nb = int(ICONSNUMB * 0.2) # get number of icons being displayed
    box_groups = split_into_groups_of(nb, boxes)

    draw_board(board, covered_boxes)
    for box_group in box_groups:
        reveal_boxes_animation(board, box_group)
        cover_boxes_animation(board, box_group)

def winning_animation(board):
    # flash the background color when the player has won
    covered_boxes = generate_revealed_boxes_data(True)
    color1 = LIGHTBGCOLOR
    color2 = BGCOLOR

    for i in range(13):
        color1, color2 = color2, color1 # swap colors
        DISPLAYSURF.fill(color1)
        draw_board(board, covered_boxes)
        pygame.display.update()
        pygame.time.wait(300)

def has_won(revealed_boxes):
    # Returns True if all the boxes have been revealed, otherwise False
    for i in revealed_boxes:
        if False in i:
            return False # return False if any boxes are covered.
    return True

if __name__ == '__main__':
    main()
