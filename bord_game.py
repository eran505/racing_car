
from box import Box

class grid_puzzle:

    def __init__(self ,name, x ,y):
        self.name = name
        self.x_size = x
        self.y_size = y
        self.grid=[]
        self.goals_box = []
        #self.start_box = []
        self.build_grid()

    def set_gaol(self,coordinate):
        box = self.get_box(coordinate)
        box.set_symbol('G')
        self.goals_box.append(coordinate)


    def get_box(self,coordinates):
        x = coordinates[0]
        y = coordinates[1]
        return self.grid[x][y]

    def remove_agent(self,coordinates,id_agent):
        box = self.get_box(coordinates)
        box.del_player(id_agent)

    def set_agent(self, coordinates, id_agent):
        box = self.get_box(coordinates)
        box.set_player(id_agent)

    def set_starting_point(self,coordinate,team):
        x = coordinate[0]
        y = coordinate[1]
        box = self.grid[x][y].set_symbol(team)

    def build_grid(self):
        for i in range(self.x_size):
            tmp_list = []
            for j in range(self.y_size ):
                tmp_list.append(Box())
            self.grid.append(tmp_list)


    def is_vaild_move(self,x,y):
        if x<0 or x>=self.x_size:
            return False
        if y<0 or y>=self.y_size:
            return False
        return True

    def print_state(self,agents_list,dead):
        change_box=[]
        for ky,val in agents_list.items():
            if val == dead:
                continue
            b_box = self.get_box(val)
            b_box.set_player(ky)
            change_box.append(b_box)
        print (self.__str__())
        for b in change_box:
            b.del_all_player()




    def __str__(self):
        str_grid=''
        for x in self.grid:
            str_grid+='\n'
            for y in x:
                str_grid+="{}".format(str(y))
        return str_grid



if __name__ == "__main__":


    exit()
    g = grid_puzzle('grid',7,7)
    g.build_grid()
    g.set_gaol((1,2))
    g.set_starting_point((0, 0),'A')
    g.set_agent((3,3),'a')
    print (str(g))
    g.remove_agent((3, 3), 'a')
    g.set_agent((6, 6), 'a')
    print (str(g))

    print ("gird class")