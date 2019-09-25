
import random
import networkx as nx

def shortest_path(G,strat_point,end_point):
    paths = nx.all_shortest_paths(G,source=strat_point,target=end_point)
    all_paths =[]
    for p in paths:
        all_paths.append(p)

    return all_paths

def shortest_path_plus(G,start,end,plus=1):
    path_gen = shortest_path(G,start,end)
    res = []
    for p in path_gen:
        res.append(add_detour_to_path(G,p,detour_len=plus+1))
    return res

def add_detour_to_path(G,path_p,detour_len):
    all_paths_gen=[]
    for j in range(len(path_p)):
        if j+1==len(path_p):
            break
        start_p = path_p[j]
        end_p = path_p[j+1]
        res = nx.all_simple_paths(G,start_p,end_p,detour_len)
        for x in res:
            combain_p = path_p[:j] + x + path_p[j+2:]
            all_paths_gen.append(combain_p)
    return all_paths_gen

def add_diagonal_edges(graph_g,x,y):
    list_node = graph_g.nodes()
    for node_i in list_node:
        x_i = node_i[0]
        y_i = node_i[1]
        if x_i + 1 < x and y_i + 1 < y:
            graph_g.add_edge((x_i, y_i), (x_i+1, y_i+1))

        if x_i-1 >= 0 and y_i - 1>=0:
            graph_g.add_edge((x_i, y_i), (x_i -1, y_i -1))

        if x_i + 1 < x and y_i - 1>=0:
            graph_g.add_edge((x_i, y_i), (x_i + 1, y_i -1))

        if x_i-1 >= 0 and y_i + 1 < y:
            graph_g.add_edge((x_i, y_i), (x_i -1, y_i + 1))

def grid_to_graph(gird,is_diagonal=False):
    x=gird.x_size
    y=gird.y_size
    G = nx.grid_2d_graph(x,y)
    if is_diagonal:
        add_diagonal_edges(G,x,y)
    return G



def get_short_path_from_grid(grid,s,e):
    G = grid_to_graph(grid)
    res = shortest_path(G,s,e)
    return res




class dog:

    def __init__(self):
        self.graph=None

    def rest(self,info):
        pass

    def get_action(self,state,id_agnet,action_obj,policy_eval):
        pass

    def get_tran(self):
        return None





class short_path_policy:

    def __init__(self,paths):
        self.optional_pathz = paths
        self.name_policy='shortest path'
        self.policy_path=None
        self.starting_p = None

    def rest(self,dict_info):
        self.starting_p = dict_info['start']
        self.choose_policy_path()

    def get_action(self,state,id_agnet,action_obj,policy_eval):
        cur_pos = state.get_agent_position(id_agnet)
        speed_cur = state.get_agent_speed(id_agnet)
        return short_path_policy.policy_next_step_shortest_path\
            (self.policy_path,cur_pos,speed_cur)

    def choose_policy_path(self):
        '''
        choose one path out of the short_paths
        '''
        pathz = self.optional_pathz[self.starting_p]
        list_of_goal = list(pathz.keys())
        size_goalz = len(list_of_goal)
        ky_number_goal = random.randint(0,size_goalz-1)
        all_path = pathz[list_of_goal[ky_number_goal]]
        randomindex = random.randint(0, len(all_path) - 1)
        #randomindex=0
        choosen = all_path[randomindex]
        self.policy_path=choosen

    def get_tran(self):
        return self.policy_path

    @staticmethod
    def policy_next_step_shortest_path(path,cur_pos,speed):
        cur_pos_t = tuple(cur_pos)
        for i in range(len(path)):
            if path[i] == cur_pos_t :
                if i+1 < len(path):
                    tup_res = short_path_policy.diff_tuple(cur_pos,path[i+1])
                    diff_speed = short_path_policy.diff_tuple(speed,tup_res)
                    action_cur = short_path_policy.make_speed_binary(diff_speed)
                    return action_cur
        raise Exception('The current position: {} is not on the given path \n path:{}'.format(cur_pos,path))

    @staticmethod
    def make_speed_binary(tuple):
        res=[]
        for i in range(len(tuple)):
            if tuple[i]>1:
                res.append(1)
            elif tuple[i]<-1:
                res.append(-1)
            else:
                res.append(tuple[i])
        return res

    @staticmethod
    def diff_tuple(small_t,big_t,minus=True):
        if minus:
            t3 = [big_t[i] - small_t[i] for i in range(len(small_t))]
        else:
            t3 = [small_t[i] + big_t[i] for i in range(len(small_t))]
        return t3





if __name__ == "__main__":
    path = [(0, 0), (1, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
    cur= (4, 5)
    speed = (1,0)
    while cur != [0,0]:
        a = policy_next_step_shortest_path(path,cur,speed)
        print ('action: {}'.format(a))
        speed = diff_tuple(speed,a,False)
        new_cur = (diff_tuple(cur,speed,False))
        print ("new_cur: {}".format(new_cur))
        cur = new_cur
    print('policy_script')
