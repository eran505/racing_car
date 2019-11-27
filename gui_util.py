import math
import random
import pygame
import tkinter as tk
from tkinter import messagebox
import pygame.freetype
from util_system import get_spped_pos


class game_gui(object):

    def __init__(self,x,y,window_size,wait_key=False,sleep_t=1000):
        self.surface=None
        self.x_axis=x
        self.y_axis=y
        self.wait_ky=wait_key
        self.score_size=100
        self.window_size=window_size
        self.player_dico={}
        self.cube_end_list=[]
        self.sleep_time=sleep_t
        self.ctr_coll=0
        self.ctr_at_goal=0
        self.ctr_wall=0
        self.change_color=False
        self.constructor()
        self.GAME_FONT = None

    def constructor(self):
        if self.wait_ky:
            self.sleep_time=1
        pygame.init()
        score_size=self.score_size
        self.surface = pygame.display.set_mode((self.window_size + score_size, self.window_size + score_size))
        self.GAME_FONT = pygame.font.Font(pygame.font.get_default_font(), 36)


    def add_player(self,id,pos,color=(138,43,226)):
        if id not in self.player_dico:
            self.player_dico[id]=cube(pos,color)

    def set_goalz(self,list_end_point):
        for point in list_end_point:
            self.cube_end_list.append(cube(point,(240,250,245)))

    def draw_end_point(self):
        for item in self.cube_end_list:
            item.draw(self.surface,self.window_size // self.x_axis,self.window_size // self.y_axis)

    def change_speed(self,id,speed):
        if speed is not None:
            self.player_dico[id].move(speed[0],speed[1])

    def change_pos(self,id,pos):
        if pos is not None:
            self.player_dico[id].pos(pos[0], pos[1])

    def draw_players(self,surface):
        for ky in self.player_dico:
            self.player_dico[ky].draw(surface,self.window_size // self.x_axis,self.window_size // self.y_axis,self.is_end)

    def wait_for_key(self):
        while self.wait_ky:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit(0)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    exit(0)
                if (keys[pygame.K_RIGHT]):
                    return

                if (keys[pygame.K_LEFT]):
                    return

                if (keys[pygame.K_UP]):
                    return

                if keys[pygame.K_DOWN]:
                    return


    def draw_game(self):
        self.score()
        self.draw_end_point()
        self.draw_players(self.surface)

        margin_size=1
        sizeBtwn = self.window_size // self.y_axis
        sizeBtwn_x = self.window_size // self.x_axis

        max_x = sizeBtwn_x*self.x_axis
        max_y = sizeBtwn*self.y_axis
        x = margin_size
        y = margin_size
        for l in range(self.x_axis+1):
            pygame.draw.line(self.surface, (255, 255, 255), (x, margin_size), (x, max_y+margin_size))
            x = x + sizeBtwn_x

        for l in range(self.y_axis+1):
            pygame.draw.line(self.surface, (255, 255, 255), (margin_size, y), (max_x+margin_size, y))
            y = y + sizeBtwn

    def redraw_Window(self):
        self.surface.fill((0, 0, 0))
        pygame.time.delay(self.sleep_time)
        self.draw_game()
        pygame.display.update()


    def score(self):
        # use a (r, g, b) tuple for color
        yellow = (255, 255, 0)

        myfont = pygame.font.SysFont("Comic Sans MS", 30)
        # apply it to text on a label
        label_1 = myfont.render("Collusion: {}".format(self.ctr_coll), 1, yellow)
        label_2 = myfont.render(" At Goal: {}".format(self.ctr_at_goal), 1, yellow)
        label_3 = myfont.render("Wall: {}".format(self.ctr_wall), 1, yellow)

        self.surface.blit(label_1, (0*self.window_size/3+10, self.window_size+self.score_size/2))
        self.surface.blit(label_2, (1*self.window_size/3+10, self.window_size+self.score_size/2))
        self.surface.blit(label_3, (2*self.window_size/3+10, self.window_size+self.score_size/2))

        # show the whole thing


    def update(self,state,info):
        self.is_end = False
        if info == 'Wall':
            self.ctr_wall+=1
            return
        if info=='collusion':
            self.ctr_coll+=1
        if info == 'goal':
            self.ctr_at_goal+=1

        if info is not None:
            self.is_end = True
        for id_name in self.player_dico:
            pos_i,speed_i= get_spped_pos(state,id_name)
            self.player_dico[id_name].pos_change(pos_i)
        self.redraw_Window()

        self.wait_for_key()

class cube(object):

    def __init__(self, start, color=(255,192,203)):

        self.dead_color=(255,255,0)
        self.pos = start
        self.dirnx = 0
        self.dirny = 0
        self.color = color

    def move(self, dirnx, dirny):

        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)

    def pos_change(self,pos):
        self.pos=pos

    def draw(self, surface, dis_x,dis_y,is_dead=False):
        mergin=0
        j = self.pos[0]
        i = self.pos[1]

        # print(self.pos)
        # print("{}:{} {}:{}".format(i * dis_y  , j * dis_x , dis_x , dis_y ))
        paint_color = self.color
        if is_dead:
            paint_color=self.dead_color

        pygame.draw.rect(surface, paint_color, (i * dis_x + mergin , j * dis_y + mergin , dis_x -mergin , dis_y - mergin ))



def main():

    g= game_gui(15,13,600)

    g.add_player('a',(3,3),(75,0,130))
    g.add_player('b', (8, 7), (70,130,180))
    g.redraw_Window()

#    g.change_speed('a',(-1,-1))
#    g.redraw_Window()

    flag = True

    clock = pygame.time.Clock()
    while flag:
        f=g.event_key()
        g.change_speed('a', f)
        g.redraw_Window()
        clock.tick(20)



if __name__ == "__main__":
    main()