'''
This is a self-contained app for the chess game Othello. 
The game uses PyGame for GUI and decision tree for the game logic
which I built from scratch. The game offers three difficulties 
which corresponds to different depths of the decision tree. 

Have fun!

Written by Shing Chi Leung at 20 February 2021
'''

import pygame
from pygame.locals import *

import sys

from random import randint, choice

# Parameter setup of the game
WINDOWWIDTH = 400
WINDOWHEIGHT = 500

BASICFONTSIZE = 20 

# screen update rate
FPS = 30

# Chess size
TILESIZE = 50

# the board size
GRIDSIZE = 400

# the png file size (width*height)
IMGSIZE = (40, 40)
BUTTONSIZE = (100, 50)
TEXTSIZE = (300, 50)

# use this so that the chess is not stuck at
# the upped left corner of the grid
MARGINSIZE = 5

# purple-ish colour for a pleasant outlook
BGCOLOR = (100, 100, 255)

# load all the image files
GRIDIMG = pygame.image.load("othello_grid.png")
WHITEIMG = pygame.image.load("othello_white.png")
BLACKIMG = pygame.image.load("othello_black.png")

# For the toolbar use
BLACKIMG2 = pygame.image.load("othello_black_dis.png")

# button image files for difficulties
EASYBTN = pygame.image.load("tictactoe_easy_btn.png")
MEDIUMBTN = pygame.image.load("tictactoe_medium_btn.png")
HARDBTN = pygame.image.load("tictactoe_hard_btn.png")
RESETBTN = pygame.image.load("tictactoe_reset_btn.png")

# the backend class for the Othello app. It contains the game 
# logic and rely on the Tree class for building the decision tree
class Othello():

    def __init__(self):

        # default is 8x8, and a buffer one row/column to prevent overflow
        self.grid = [[0 for i in range(10)] for j in range(10)]

        # standard starting setup for Othello
        self.grid[4][4] = 1
        self.grid[4][5] = -1
        self.grid[5][4] = -1
        self.grid[5][5] = 1
        #self.grid[1][0] = 1

        # the player who has just done the move
        self.player = 0 #randint(0,1) 0 for player and 1 for AI

        # the difficulty level, can be changed during game
        self.decision_level = 1

        # flag for end game
        self.end_game = False
        self.winner = None

        # count of win, lose and draw games
        self.result = [0, 0, 0]
        self.score = 0

    # change the current player after each player move
    def switch_player(self):
        self.player = (self.player+1)%2

    # update decision-tree depth
    def set_decision_level(self, value):
        self.decision_level = value

    # reset the game board and restarts
    def reset_game(self):
        self.clean_grid()
        self.end_game = False

    # reset the game board
    def clean_grid(self):
        for i in range(10):
            for j in range(10):
                self.grid[i][j] = 0

        # initial setting
        self.grid[4][4] = 1
        self.grid[4][5] = -1
        self.grid[5][4] = -1
        self.grid[5][5] = 1

    # use the given action and place on the board
    def add_move(self, action):

        i, j = action
        added_move = False

        # the board value depends on the player
        # player 0 --> 1
        # player 1 --> -1
        #
        # they are chosen so that their sum is the net win/lose
        # of the chess for player 1 against player 2
        if self.player == 0:
            if self.grid[i][j] == 0:
                self.grid[i][j] = 1
                added_move = True
        else:
            if self.grid[i][j] == 0:
                self.grid[i][j] = -1
                added_move = True

        return added_move

    # check whether the game board is full
    # if yes, calculate which player has the higher score
    def check_end_game(self):
        
        # calculate the score and update the global var.
        score = self.check_score(self.grid)
        self.score = score

        # for debug use
        print("Score = {}, {}".format(score, self.check_full_grid(self.grid)))

        # end game by one player wins and no more move
        if self.check_full_grid(self.grid):
            self.end_game = True
            if score > 0:
                self.winner = 0
                self.result[0] += 1
                print("Player 1 wins!")
            elif score < 0:
                self.winner = 1
                self.result[1] += 1
                print("Player 2 wins!")
            else:
                self.result[2] += 1
                print("Game Draw")

    # check if the board is already fully placed
    def check_full_grid(self, grid):
        is_full_grid = True
        for i in range(1,9,1):
            for j in range(1,9,1):
                if grid[i][j] == 0:
                    is_full_grid = False
                    break
        return is_full_grid

    # do one full step for the AI player
    def player_step(self):

        # the AI player build a decision tree from the current board
        # then choose the best move, then sends the decision to the 
        # grid and update the board. (Need to overwrite the original one)
        action = self.decision_tree()
        new_grid = self.update_grid(self.grid, self.player, action)
        self.overwrite_grid(new_grid)

        # check if the AI's move is already the end game
        is_end_game = self.check_end_game()

        # for debug use
        print("Player {} added move {}.".format(self.player, action))

        # switch player
        self.switch_player()

    # copy the new grid to the global grid variables
    def overwrite_grid(self, grid):
        for i in range(10):
            for j in range(10):
                self.grid[i][j] = grid[i][j]

    # build the decision tree by the Tree class
    def decision_tree(self):

        # copy global variable for local variable to avoid overwrite
        player = self.player
        curr_grid = [[self.grid[j][i] for i in range(10)] for j in range(10)]

        # every step a new tree is built 
        tree = Tree(curr_grid, player, None, 0)

        # generate decision tree and get the best move(s)
        tree = self.extend_tree(tree, player, 0)
        score = tree.pass_score(player)
        actions = tree.select_best_child()

        #tree.print_tree(0)

        # only one move is chosen by random
        return choice(actions)

    # from the current configuration, build the extension of the tree by listing
    # all possible configurations of the next steps
    def extend_tree(self, tree, curr_player, level):
        
        # make sure the loop does not repeat indefinitely and only up to desired level
        if level == self.decision_level: return tree
        level += 1

        # get all the valid moves on the grid
        # i.e. the step will eat at least one opponent player's chess
        valid_actions = self.get_valid_actions(tree.grid, curr_player)

        for action in valid_actions:
            
            # simplify the notation
            i, j = action

            # build the next step
            player = curr_player

            # copy the local board and add one extra step
            if player == 0:
                new_grid = [[tree.grid[j][i] for i in range(10)] for j in range(10)]
                new_grid[i][j] = 1
            else:
                new_grid = [[tree.grid[j][i] for i in range(10)] for j in range(10)]
                new_grid[i][j] = -1
                    
            # update the board to flip the chess accordingly and then calculate score
            new_grid = self.update_grid(new_grid, player, action)
            score = self.check_score(new_grid)

            # set a child node based on the new_grid
            child = Tree(new_grid, (player+1)%2, action, score)

            # for debug use
            if child.score != 0:    
                print("Going to extend tree {} {} {}".format(new_grid, action, level))

            # extend the tree by the child node using depth-first search
            child = self.extend_tree(child, (player+1)%2, level)

            # add the fully developed child as one child of the parent node
            tree.add_child(child)
                
        return tree

    # check if the action is valid for a given grid and the player turn
    def is_valid_action(self, grid, player, action):

        i, j = action 

        if player == 0:
            host = 1
            opp = -1
        else:
            host = -1
            opp = 1

        has_action = False

        # span all the eight directions
        if grid[i][j] == 0:
                    
            # down direction
            if grid[i+1][j] == opp:
                for i2 in range(i+1,10,1):
                    if grid[i2][j] == host: 
                        has_action = True

            # up direction
            if grid[i-1][j] == opp:
                for i2 in range(i-1):
                    if grid[i2][j] == host: 
                        has_action = True

            # right direction
            if grid[i][j+1] == opp:
                i2min = 10 - j
                for i2 in range(i2min):
                    if grid[i][j+i2] == host: 
                        has_action = True

            # left direction
            if grid[i][j-1] == opp:
                i2min = j
                for i2 in range(i2min):
                    if grid[i][j-i2] == host: 
                        has_action = True


            # up-left direction
            if grid[i-1][j-1] == opp:
                i2min = min(i-1,j-1)
                for i2 in range(i2min):
                    if grid[i-i2][j-i2] == host: 
                        has_action = True

            # up-right direction
            if grid[i-1][j+1] == opp:
                i2min = min(i-1, 10-j)
                for i2 in range(i2min):
                    if grid[i-i2][j+i2] == host: 
                        has_action = True

            # down-right direction
            if grid[i+1][j+1] == opp:
                i2min = min(10-i, 10-j)
                for i2 in range(i2min):
                    if grid[i+i2][j+i2] == host: 
                        has_action = True

            # down-left direction
            if grid[i+1][j-1] == opp:
                i2min = min(10-i, j-1)
                for i2 in range(i2min):
                    if grid[i+i2][j-i2] == host: 
                        has_action = True

        return has_action

    # for the given grid and player turn, determines all the possible moves
    def get_valid_actions(self, grid, player):

        moves = []
        if player == 0:
            host = 1
            opp = -1
        else:
            host = -1
            opp = 1

        # if the move is valid, add to the candidate list
        for i in range(1,9,1):
            for j in range(1,9,1):
                has_action = self.is_valid_action(grid, player, (i,j))
                if has_action == True:
                    moves.append((i,j))

        return moves

    # for a given grid and player turn, use the action to update the grid
    # and then flip the chess accordingly
    def update_grid(self, grid, player, action):

        if player == 0:
            host = 1
            opp = -1
        else:
            host = -1
            opp = 1

        i, j = action

        # add the move 
        grid[i][j] = host
        print("in update grid", grid)

        # then do all the 8 direction search to check if chesses needed to be flipped
        # down direction
        if grid[i+1][j] == opp:
            i2min = 10 - i
            for i2 in range(1,i2min):
                if grid[i+i2][j] == host: 
                    print("reversing down direction")
                    for j2 in range(i2):
                        grid[i+j2][j] = host        
                    break

        # up direction
        if grid[i-1][j] == opp:
            i2min = i
            for i2 in range(1,i2min):
                if grid[i-i2][j] == host: 
                    print("reversing up direction")
                    for j2 in range(i2):
                        grid[i-j2][j] = host        
                    break


        # right direction
        if grid[i][j+1] == opp:
            i2min = 10 - j
            for i2 in range(1,i2min):
                if grid[i][j+i2] == host: 
                    print("reversing right direction")
                    for j2 in range(i2):
                        grid[i][j+j2] = host        
                    break

        # left direction
        if grid[i][j-1] == opp:
            i2min = j
            for i2 in range(1,i2min):
                if grid[i][j-i2] == host: 
                    print("reversing left direction")
                    for j2 in range(i2):
                        grid[i][j-j2] = host        
                    break

        # down right direction
        if grid[i+1][j+1] == opp:
            i2min = min(10-i, 10-j)
            for i2 in range(1,i2min):
                if grid[i+i2][j+i2] == host: 
                    for j2 in range(i2):
                        grid[i+j2][j+j2] = host        
                    break
        
        # down left direction
        if grid[i+1][j-1] == opp:
            i2min = min(10-i, j)
            for i2 in range(1,i2min):
                if grid[i+i2][j-i2] == host: 
                    for j2 in range(i2):
                        grid[i+j2][j-j2] = host        
                    break

        # up right direction
        if grid[i-1][j+1] == opp:
            i2min = min(i, 10-j)
            for i2 in range(1,i2min):
                if grid[i-i2][j+i2] == host: 
                    for j2 in range(i2):
                        grid[i-j2][j+j2] = host        
                    break

        # up left direction
        if grid[i-1][j-1] == opp:
            i2min = min(10-i, 10-j)
            for i2 in range(1,i2min):
                if grid[i-i2][j-i2] == host: 
                    for j2 in range(i2):
                        grid[i-j2][j-j2] = host        
                    break

        return grid

    # calculate the total score of the board
    # +1 for a chess of Player 0
    # -1 for a chess of Player 1
    def check_score(self, grid):

        score = 0
        # horizontal
        for i in range(10):
            for j in range(10):
                score += grid[i][j]
        return score

# this is the backend supporting class. The Tree class is a general data
# structure for storing the decision tree with methods to determines the 
# best node for a given criteria. Specially designed for Othello Chess
class Tree():

    def __init__(self, grid, player, action, score):

        # the game board
        self.grid = grid

        # the player turn for the next move
        self.player = player

        # the previous action that leads to this board
        self.action = action

        # the corresponding score of this board
        self.score = score

        # any offspring children 
        self.children = []

    # add a Tree node as its child
    def add_child(self, child):
        self.children.append(child)

    # pass the score from the bottom of the tree to the top
    # and update the local score using MinMax Algorithm
    def pass_score(self, player):

        # For player turn, take maximum
        # i.e. the AI assumes the player gets the best move
        # For AI turn, take minimum
        # i.e. the AI wants the best move for itself

        if player == 1: 
            for child in self.children:
                score = child.pass_score((player+1)%2)
                if score < self.score:
                    self.score = score
        else:    
            for child in self.children:
                score = child.pass_score((player+1)%2)
                if score > self.score:
                    self.score = score
       
        return self.score

    # do the scan of the root node to see which child has the 
    # best decision (based on score), then add the decision
    # which leads to that child's configuration as a possible move
    def select_best_child(self):

        # there can be more than one
        action = []

        # span the child 
        for child in self.children:
            #print(child.grid, child.score, self.score)
            if child.score == self.score:
                action.append(child.action)

        # random sample if no action taken by MinMax
        if action == []:
            action.append(choice(self.children).action)

        return action

    # for debug use
    def print_tree(self, level):
        print("At level {}".format(level))
        print("grid={}, player={}, action={}, score={}".format(self.grid, self.player, self.action, self.score))
        for child in self.children:
            child.print_tree(level+1)

# this is the frontend of the App. It draws the GUI using PyGame library and 
# calls the backend for its background logic.
class OthelloApp():

    def __init__(self):

        pygame.init()

        # set up configuration parameters 
        self.fps_clock = pygame.time.Clock()
        self.display_surf = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        self.basic_font = pygame.font.Font("freesansbold.ttf", BASICFONTSIZE)

        # for checking where the mouse has clicked
        self.mousex = 0
        self.mousey = 0

        # meta-data for decoration
        pygame.display.set_caption("Othello")
        pygame.display.set_icon(pygame.image.load("othello_black.png"))

        # call the backend app
        self.othello = Othello()

        while True:

            mouseClicked = False

            # update the whole app screen
            self.draw_game_board()

            # check the keyboard and mouse input
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    mousex, mousey = event.pos
                    self.handle_mouse_click(mousex, mousey)
                    
            # the AI player waits for the other player to finish 
            # and add its move if the game is ongoing
            if self.othello.end_game == False and self.othello.player == 1:
                pygame.time.wait(1000)
                self.othello.player_step()

            # put all the screen data online
            pygame.display.update()
            self.fps_clock.tick(FPS)

    # check where the mouse clicked and acts accordingly to it
    def handle_mouse_click(self, mousex, mousey):

        # the mouse clicked the game board
        if mousey < GRIDSIZE:
            if mousex<GRIDSIZE:
                clicked_grid_i = int(mousex / TILESIZE) + 1
                clicked_grid_j = int(mousey / TILESIZE) + 1

                # first check the player's move is valid
                is_valid_action = self.othello.is_valid_action(
                    self.othello.grid, self.othello.player, (clicked_grid_j, clicked_grid_i)
                )

                # for debug use
                print("Player attempt move {} {}, valid? {}".format(clicked_grid_j, clicked_grid_i, is_valid_action))

                # if yes, then update the board according to the move
                if self.othello.end_game == False and is_valid_action == True:
                    print("Player add move {} {}".format(clicked_grid_j, clicked_grid_i))
                    self.othello.update_grid(self.othello.grid, self.othello.player, (clicked_grid_j, clicked_grid_i))
                    self.othello.check_end_game()

                    # switch the current player so that it becomes the other player's (AI) turn
                    self.othello.switch_player()

        # the mouse clicked one of the button
        elif mousey>GRIDSIZE and mousey<GRIDSIZE + BUTTONSIZE[1]:

            # EASY buttonn
            if mousex < BUTTONSIZE[0]:
                self.othello.set_decision_level(1)
                print("Difficult set to 1")

            # MEDIUM button
            elif mousex > BUTTONSIZE[0] and mousex < 2*BUTTONSIZE[0]: 
                self.othello.set_decision_level(3)
                print("Difficult set to 3")

            # HARD button
            elif mousex > 2*BUTTONSIZE[0] and mousex < 3*BUTTONSIZE[0]: 
                self.othello.set_decision_level(5)
                print("Difficult set to 5")

            # RESET button
            elif mousex > 3*BUTTONSIZE[0] and mousex < 4*BUTTONSIZE[0]:
                self.othello.reset_game()

    # draw the game board according to the game board, and add all the 
    # buttons and scores to the screen
    def draw_game_board(self):

        self.display_surf.fill(BGCOLOR)

        # draw the game board
        grid_rect = pygame.Rect(0, 0, GRIDSIZE, GRIDSIZE)
        self.display_surf.blit(GRIDIMG, grid_rect)

        # put all the chesses on the board
        for j in range(1,9,1):
            for i in range(1,9,1):
                if self.othello.grid[j][i] == 1:
                    grid_rect = pygame.Rect(MARGINSIZE + (i-1)*TILESIZE, MARGINSIZE + (j-1)*TILESIZE, IMGSIZE[0], IMGSIZE[1])
                    self.display_surf.blit(BLACKIMG, grid_rect)
                elif self.othello.grid[j][i] == -1:
                    grid_rect = pygame.Rect(MARGINSIZE + (i-1)*TILESIZE, MARGINSIZE + (j-1)*TILESIZE, IMGSIZE[0], IMGSIZE[1])
                    self.display_surf.blit(WHITEIMG, grid_rect)

        # draw all buttons 
        grid_rect = pygame.Rect(10, GRIDSIZE+10, BUTTONSIZE[0], BUTTONSIZE[1])
        self.display_surf.blit(EASYBTN, grid_rect)

        grid_rect = pygame.Rect(110, GRIDSIZE+10, BUTTONSIZE[0], BUTTONSIZE[1])
        self.display_surf.blit(MEDIUMBTN, grid_rect)

        grid_rect = pygame.Rect(210, GRIDSIZE+10, BUTTONSIZE[0], BUTTONSIZE[1])
        self.display_surf.blit(HARDBTN, grid_rect)

        grid_rect = pygame.Rect(310, GRIDSIZE+10, BUTTONSIZE[0], BUTTONSIZE[1])
        self.display_surf.blit(RESETBTN, grid_rect)

        # draw the score text for GUI
        score_text = "Win: {} Lose: {} Draw: {}".format(self.othello.result[0], self.othello.result[1], self.othello.result[2])
        score_surf, score_rect = self.make_text(score_text, (0,0,0), BGCOLOR, 10, GRIDSIZE+60)
        self.display_surf.blit(score_surf, score_rect)
        #print(grid_rect.x)

        # remind the player which color the player is
        player_text = "You: {}".format(self.othello.score)
        player_surf, player_rect = self.make_text(player_text, (0,0,0), BGCOLOR, 250, GRIDSIZE+60)
        self.display_surf.blit(player_surf, player_rect)

        # chess colour
        grid_rect = pygame.Rect(335, GRIDSIZE+60, IMGSIZE[0]/2, IMGSIZE[1]/2)
        self.display_surf.blit(BLACKIMG2, grid_rect)

    # a method for generating sprite of the text
    def make_text(self, text, color, bgcolor, left, top):
        text_surf = self.basic_font.render(text, True, color, bgcolor)
        text_rect = text_surf.get_rect()
        text_rect.topleft = (left, top)
        return (text_surf, text_rect)


# with the frontend and backend, calling the app is simple which just need
# to call the frontend.
def main():

    othello_app = OthelloApp()

    #othello = Othello()

    #for i in range(2):
    #    othello.player_step()

    #print("End game: {}".format(othello.grid))

if __name__=="__main__":
    main()





