'''
This is a self-contained app for the chess game Tic-Tac-Toe. 
The game uses PyGame for GUI and decision tree for the game logic
which I built from scratch. The game offers two difficulties 
which corresponds to different depths of the decision tree. 

Have fun!

Written by Shing Chi Leung at 19 February 2021
'''

import pygame
from pygame.locals import *

import sys

from random import randint, choice

# geometry of the App
WINDOWWIDTH = 300
WINDOWHEIGHT = 400

BASICFONTSIZE = 20 

# frame update rate
FPS = 30

# grid size of the chess (O or X)
TILESIZE = 100

# game board size
GRIDSIZE = 300

# sizes of png files
IMGSIZE = (80, 80)
BUTTONSIZE = (100, 50)
TEXTSIZE = (300, 50)
MARGINSIZE = 10

# for a purple-ish colour for a pleasant look
BGCOLOR = (100, 100, 255)

# load all the image file at the front
GRIDIMG = pygame.image.load("tictactoe_grid.png")
CIRCLEIMG = pygame.image.load("tictactoe_circle.png")
CROSSIMG = pygame.image.load("tictactoe_cross.png")

# button image files
EASYBTN = pygame.image.load("tictactoe_easy_btn.png")
HARDBTN = pygame.image.load("tictactoe_hard_btn.png")
RESETBTN = pygame.image.load("tictactoe_reset_btn.png")

# the backend of the app. This includes the AI player and 
# contains the whole game flow
class Tictactoe():

    def __init__(self):
        self.grid = [[0 for i in range(3)] for j in range(3)]
        #self.grid[1][0] = 1

        # the player who has just done the move
        self.player = 0 #randint(0,1) 0 for player and 1 for AI

        # depth of the decision tree for the game difficulty
        self.decision_level = 3

        # check whether the game is finished
        self.end_game = False
        self.winner = None

        # count of win, lose and draw games for the score
        self.result = [0, 0, 0]

    # change player after one of the players' move
    def switch_player(self):
        self.player = (self.player+1)%2

    # change the decision tree depth, can be changed in game
    def set_decision_level(self, value):
        self.decision_level = value

    # restart the game 
    def reset_game(self):
        self.clean_grid()
        self.end_game = False

    # remove all the chess (O or X) on the board
    def clean_grid(self):
        for i in range(3):
            for j in range(3):
                self.grid[i][j] = 0

    # add the move to the game board
    def add_move(self, action):

        i, j = action
        added_move = False

        # player 0 --> 1
        # player 1 --> -1
        if self.player == 0:
            if self.grid[i][j] == 0:
                self.grid[i][j] = 1
                added_move = True
        else:
            if self.grid[i][j] == 0:
                self.grid[i][j] = -1
                added_move = True

        return added_move


    def check_end_game(self):
        score = self.check_score(self.grid)
        print("Score = {}, {}".format(score, self.check_full_grid(self.grid)))

        # end game by one player wins
        if score != 0:
            self.end_game = True
            if score == 1:
                self.winner = 0
                self.result[0] += 1
                print("Player 1 wins!")
            elif score == -1:
                self.winner = 1
                self.result[1] += 1
                print("Player 2 wins!")

        # end game by no more move
        if score==0 and self.check_full_grid(self.grid):
            self.end_game = True
            print("Game draw!")
            self.result[2] += 1

    # check if all the grids are filled
    def check_full_grid(self, grid):

        is_full_grid = True
        for i in range(3):
            for j in range(3):
                if grid[i][j] == 0:
                    is_full_grid = False
                    break

        return is_full_grid

    # a full move of the AI player
    def player_step(self):

        # the AI builds a decision based on the current grid
        action = self.decision_tree()
        added_move = self.add_move(action)

        # check if the AI's move lead to end game
        is_end_game = self.check_end_game()

        # for debug use
        print("Player {} added move {}.".format(self.player, action))

        # switch player
        self.switch_player()

    # build a decision tree 
    def decision_tree(self):

        # copy the global variables to local variables to avoid confusion
        player = self.player
        curr_grid = [[self.grid[j][i] for i in range(3)] for j in range(3)]

        # tree is newly built in every step
        tree = Tree(curr_grid, player, None, 0)

        # generate predictions by finding the best move from the tree
        tree = self.extend_tree(tree, player, 0)
        score = tree.pass_score(player)
        actions = tree.select_best_child()
        #tree.print_tree(0)

        # only one of the best moves is chosen
        return choice(actions)

    # a recursive function to extend the tree using depth-first approach
    def extend_tree(self, tree, curr_player, level):
        
        # make sure the loop does not repeat indefinitely
        if level == self.decision_level: return tree
        level += 1

        for i in range(3):
            for j in range(3):

                # there is no restriction which grid can be placed next, thus 
                # all empty grids must be checked
                if tree.grid[i][j] == 0:
                    action = (i, j)

                    # build the next step
                    player = curr_player

                    # build the new grid using the candidate action
                    if player == 0:
                        new_grid = [[tree.grid[j][i] for i in range(3)] for j in range(3)]
                        new_grid[i][j] = 1
                    else:
                        new_grid = [[tree.grid[j][i] for i in range(3)] for j in range(3)]
                        new_grid[i][j] = -1
                    
                    # check the score (i.e. the result of the board)
                    score = self.check_score(new_grid)

                    # build a new tree node using the new grid
                    child = Tree(new_grid, (player+1)%2, action, score)

                    if child.score != 0:    
                        print("Going to extend tree {} {} {}".format(new_grid, action, level))

                    # only extend the tree if the new_grid is not an end game
                    if child.score == 0:
                        child = self.extend_tree(child, (player+1)%2, level)

                    # add the fully developed child to the original tree
                    tree.add_child(child)
                
        return tree

    # check the total score based on the game board
    def check_score(self, grid):

        score = 0
        # horizontal
        for i in range(3):
            if grid[i][0] == 1 and grid[i][1] == 1 and grid[i][2] == 1:
                score = 1
            elif grid[i][0] == -1 and grid[i][1] == -1 and grid[i][2] == -1:
                score = -1

        # vertical
        for i in range(3):
            if grid[0][i] == 1 and grid[1][i] == 1 and grid[2][i] == 1:
                score = 1
            elif grid[0][i] == -1 and grid[1][i] == -1 and grid[2][i] == -1:
                score = -1

        # diagonal
        if grid[0][0] == 1 and grid[1][1] == 1 and grid[2][2] == 1:
            score = 1
        elif grid[0][0] == -1 and grid[1][1] == -1 and grid[2][2] == -1:
            score = -1

        if grid[2][0] == 1 and grid[1][1] == 1 and grid[0][2] == 1:
            score = 1
        elif grid[2][0] == -1 and grid[1][1] == -1 and grid[0][2] == -1:
            score = -1

        return score

# this is the backend supporting class for building the general abstract tree
# which I built from scratch. The data structure is fine tuned for Tic-Tac-Toe
class Tree():

    def __init__(self, grid, player, action, score):

        # the current grid
        self.grid = grid

        # the player that needs to move next
        self.player = player

        # the action that leads to this grid from the parent
        self.action = action

        # the implied score of the board
        self.score = score

        # its children for the next possible steps
        self.children = []

    # add a new child as a possible move
    def add_child(self, child):
        self.children.append(child)

    # pass the score from the bottom of the tree to the top 
    # based on the MinMax criteria. 
    def pass_score(self, player):

        # For player turn, take maximum
        # i.e. the AI tries to get the best move
        # For AI turn, take minimum
        # i.e. the AI wants the player get the worst move

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

    # from the top node, decides which child inherits the best moves from
    # its child, choose the action which leads to that child
    def select_best_child(self):

        # in general multiple best moves are possible
        action = []

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

# the frontend class for drawing the GUI and calling the backend class
# to allow interaction between the human player with the game
class TicTacToeApp():

    def __init__(self):

        pygame.init()

        # the general configuration of the game
        self.fps_clock = pygame.time.Clock()
        self.display_surf = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        self.basic_font = pygame.font.Font("freesansbold.ttf", BASICFONTSIZE)

        # global variable for storing mouse click
        self.mousex = 0
        self.mousey = 0

        # meta-information for the app
        pygame.display.set_caption("Tic Tac Toe")
        pygame.display.set_icon(pygame.image.load("tictactoe_circle.png"))

        # call the backend as its variable
        self.tictactoe = Tictactoe()

        while True:

            mouseClicked = False

            # draw the app screen 
            self.draw_game_board()

            # manage all user's input
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    mousex, mousey = event.pos
                    self.handle_mouse_click(mousex, mousey)
                    
            # after the other player move, the AI does its move
            if self.tictactoe.end_game == False and self.tictactoe.player == 1:
                self.tictactoe.player_step()

            # update the screen after the game board is updated
            pygame.display.update()
            self.fps_clock.tick(FPS)

    # classify the action from the mouse click and act accordingly
    def handle_mouse_click(self, mousex, mousey):

        # if the mouse click is in the gameboard
        if mousey < GRIDSIZE:
            if mousex<GRIDSIZE:
                clicked_grid_i = int(mousex / 100)
                clicked_grid_j = int(mousey / 100)

                # check if the click is valid, if so, add the step and update the game board
                if self.tictactoe.end_game == False and self.tictactoe.grid[clicked_grid_j][clicked_grid_i] == 0:
                    self.tictactoe.add_move((clicked_grid_j, clicked_grid_i))

                    # need to check if the finishes after the player's move
                    self.tictactoe.check_end_game()
                    self.tictactoe.switch_player()

        # if the mouse click one of the buttons
        elif mousey>GRIDSIZE and mousey<GRIDSIZE + BUTTONSIZE[1]:
            if mousex < BUTTONSIZE[0]:
                self.tictactoe.set_decision_level(1)
                print("Difficult reduced to 1")
            elif mousex > BUTTONSIZE[0] and mousex < 2*BUTTONSIZE[0]: 
                self.tictactoe.set_decision_level(3)
                print("Difficult reduced to 3")
            elif mousex > 2*BUTTONSIZE[0] and mousex < 3*BUTTONSIZE[0]:
                self.tictactoe.reset_game()

    # draw the game board and all the button for the GUI
    def draw_game_board(self):

        self.display_surf.fill(BGCOLOR)

        # draw the board
        grid_rect = pygame.Rect(0, 0, GRIDSIZE, GRIDSIZE)
        self.display_surf.blit(GRIDIMG, grid_rect)

        # draw all the chess
        for j in range(3):
            for i in range(3):
                if self.tictactoe.grid[j][i] == 1:
                    grid_rect = pygame.Rect(MARGINSIZE + i*TILESIZE, MARGINSIZE + j*TILESIZE, IMGSIZE[0], IMGSIZE[1])
                    self.display_surf.blit(CIRCLEIMG, grid_rect)
                elif self.tictactoe.grid[j][i] == -1:
                    grid_rect = pygame.Rect(MARGINSIZE + i*TILESIZE, MARGINSIZE + j*TILESIZE, IMGSIZE[0], IMGSIZE[1])
                    self.display_surf.blit(CROSSIMG, grid_rect)

        # draw all the buttons
        grid_rect = pygame.Rect(10, GRIDSIZE+10, BUTTONSIZE[0], BUTTONSIZE[1])
        self.display_surf.blit(EASYBTN, grid_rect)

        grid_rect = pygame.Rect(110, GRIDSIZE+10, BUTTONSIZE[0], BUTTONSIZE[1])
        self.display_surf.blit(HARDBTN, grid_rect)

        grid_rect = pygame.Rect(210, GRIDSIZE+10, BUTTONSIZE[0], BUTTONSIZE[1])
        self.display_surf.blit(RESETBTN, grid_rect)

        # draw the score
        score_text = "Win: {} Lose: {} Draw: {}".format(self.tictactoe.result[0], self.tictactoe.result[1], self.tictactoe.result[2])
        grid_surf, grid_rect = self.make_text(score_text, (0,0,0), BGCOLOR, 10, GRIDSIZE+60)
        self.display_surf.blit(grid_surf, grid_rect)
        #print(grid_rect.x)

    # a short method to trasnfer text into sprites
    def make_text(self, text, color, bgcolor, left, top):
        text_surf = self.basic_font.render(text, True, color, bgcolor)
        text_rect = text_surf.get_rect()
        text_rect.topleft = (left, top)
        return (text_surf, text_rect)

# by using the frontend, the app can be started easily by just calling it. The app will run 
# automatically. The backend is called inside the frontend
def main():

    tictaetoe_app = TicTacToeApp()

    '''
    tictactoe = Tictactoe()

    for i in range(9):
        tictactoe.player_step()
        if tictactoe.player == 0:
            tictactoe.decision_level = 3
        else:
            tictactoe.decision_level = 1
        if tictactoe.end_game == True:
            print("End game: {}".format(tictactoe.grid))
            break
    '''


if __name__=="__main__":
    main()





