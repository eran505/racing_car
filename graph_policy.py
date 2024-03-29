
import random
import networkx as nx
import util_system as util
from numpy import round
import numpy as np


def shortest_path(G,strat_point,end_point,max_path=100000):
    paths = nx.all_shortest_paths(G,source=strat_point,target=end_point)
    all_paths =[]
    for p in paths:
        all_paths.append(p)
    if len(all_paths)>max_path:
        print ('ALL PATH:\t',intWithCommas(len(all_paths)))
        return random.sample(all_paths , k=max_path)
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

    def __init__(self,paths,absolut_max_speed):
        self.optional_pathz = paths
        self.name_policy='shortest path'
        self.policy_path=None
        self.starting_p = None
        self.all_path_number=0
        self.d_policy=None
        self.max_look_head=2
        self.max_speed=absolut_max_speed
        self.d_pos_t_step=None
        self.action_set={}
        self.pos_goal=set()
        self.action_list_a=None
        self.pre_function()
        self.uniform_policy()
        self.dead_end_state={}
        self.memo_save=None






    def pre_function(self):
        self.action_list_a = [(0, 0), (0, 1), (0, -1), (1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1)]


    def loader(self,path):

        with open(path[0], 'rb') as handle:
            self.d_pos_t_step = pickle.load(handle)

    def uniform_policy(self):
        self.rearrange_data()


    def probabily_entries(self):
        for ky in self.d_policy:
            l_action = self.d_policy[ky]
            prob = counter_method(l_action)
            self.d_policy[ky]=prob



    def rest(self,dict_info):
        self.memo_save=None

    def update_policy(self,s_old,r,a,s_new,action_obj):
        pass

    def update_end(self,state,reward):
        pass

    def get_action(self,state,id_agnet,action_obj,policy_eval):
        '''
        [pos, speed, action, uni_probability]
        '''
        res = self.get_transition(state,id_agnet,take_action=True)
        prob_l = [item[-1] for item in res]
        action_l = [item[-2] for item in res]

        ch = random.choices(action_l,prob_l)

        #ch = random.randrange(0, len(res), 1)
        #return res[ch][-2]
        return ch[0]

    def get_transition(self,state,id_agnet,take_action=False):
        cur_pos = tuple(state.get_agent_position(id_agnet))
        speed_cur = tuple(state.get_agent_speed(id_agnet))

        tran = self.get_action_move(speed_cur,cur_pos,take_action)
        tran = self.stochastic_move(tran)
        if len(tran)==0:
            self.dead_end_state[(speed_cur,cur_pos)]=True
            tran=[[cur_pos,(0,0),(0,0),1]]
            state.set_agent_speed(id_agnet,(0,0))

        return tran

    def stochastic_move(self,list_tran):
        p_max = 0.6
        l_moves={}
        l_tran_prob=[]
        for item in list_tran:
            pos= item[0]
            t_i = self.d_pos_t_step[pos]
            if t_i not in l_moves:
                l_moves[t_i]=[]
            l_moves[t_i].append(item)
        k_y = l_moves.keys()
        items_list = l_moves.values()
        size = len(k_y)
        if size>1:
            max_key =max(list(k_y))
            size_max = len(l_moves[max_key])
            for item_i in l_moves[max_key]:
                item_i[-1]=round(p_max/float(size_max),6)
            p_left_over = (1.0-p_max)/(size-1)
            for key in k_y:
                if key==max_key:
                    continue
                size_list = len(l_moves[key])
                for item_i in l_moves[key]:
                    item_i[-1]=round(p_left_over/float(size_list),6)
        fin_l=[]
        for ky_i in l_moves:
            fin_l.extend(l_moves[ky_i])

        return fin_l




    def hurstic(self,state,id_agnet='A1'):
        cur_pos = tuple(state.get_agent_position(id_agnet))
        speed_cur = tuple(state.get_agent_speed(id_agnet))


        l_moves = self.get_next_state(speed_cur, cur_pos)

        if l_moves is None:
            l_moves = [[cur_pos,(0,0),(0,0)]]
            #print(state)
        return l_moves

    def rearrange_data(self):
        '''
        make data set for shortest dist
        pos : <time_step>
        '''
        d={}
        for ky_start in self.optional_pathz:
            for ky_goal in self.optional_pathz[ky_start]:
                for path_i in self.optional_pathz[ky_start][ky_goal]:
                    self.all_path_number+=1
                    for i in range(len(path_i)):
                        if i == len(path_i)-1:
                            self.pos_goal.add(path_i[i])
                        if path_i[i] not in d:
                            d[path_i[i]] = i
                        elif d[path_i[i]] == i:
                            continue
                        else:
                            raise Exception('error in short path in function rearrange_data ')
        self.d_pos_t_step=d



    def get_next_pos_mover(self,state,id_player):
        cur_pos = tuple(state.get_agent_position(id_player))
        speed_cur = tuple(state.get_agent_speed(id_player))

    def get_memo_state(self,speed,pos):
        tup = (pos,speed)
        if tup in self.memo_save:
            return self.memo_save[tup]

    def get_action_move(self,speed,pos,take_action=True):
        l_op=[]
        if self.memo_save is not None and take_action:
            return self.memo_save
        else:
            l_moves = self.get_next_state(speed,pos)
        if l_moves is None:
            return l_op
        for item in l_moves:
            # if the its a goal pos
            if item[0] in self.pos_goal:
                l_op.append(item)
                continue
            # else check if there any possible move head
            res = self.get_next_state(item[1],item[0])
            if res is not None:
                l_op.append(item)



        size =float(len(l_op))
        for x in l_op:
            x.append(1/size)
        if take_action is False:
            self.memo_save=l_op
        return l_op

    def get_next_state(self,speed,pos):
        l=[]
        t= self.d_pos_t_step[pos]
        for action_a in self.action_list_a:
            skip=False
            speed_a = [action_a[i] + speed[i] for i in range(len(speed))]
            speed_a = tuple(speed_a)
            # if the speed is over the MAX_SPEED
            for i in range(len(speed_a)):
                if abs(speed_a[i]) > self.max_speed:
                    skip=True
            if skip:
                continue

            pos_a = [speed_a[i] + pos[i] for i in range(len(speed_a))]
            pos_a = tuple(pos_a)
            if pos_a  in self.d_pos_t_step:
                if t<self.d_pos_t_step[pos_a]:
                    if (speed_a,pos_a) in self.dead_end_state:
                        continue
                    l.append([pos_a,speed_a,action_a])
        if len(l)==0:
            return None
        return l

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
        return self



    @staticmethod
    def get_expected_action(state,id_agnet,policy):
        cur_pos = tuple(state.get_agent_position(id_agnet))
        speed_cur = state.get_agent_speed(id_agnet)
        return short_path_policy.optional_next_action(policy,cur_pos,speed_cur)

    @staticmethod
    def optional_next_action(policy,cur_pos,cur_speed):
        l_next_move = policy[cur_pos]
        optional_moves_action = []
        for next_move in l_next_move:
            tup_res = short_path_policy.diff_tuple(cur_pos, next_move[0])
            diff_speed = short_path_policy.diff_tuple(cur_speed, tup_res)
            if short_path_policy.if_binary_speed(diff_speed):
                optional_moves_action.append((tuple(diff_speed),next_move[1]))
        return optional_moves_action

    @staticmethod
    def if_binary_speed(speed):
        for i in range(len(speed)):
            if speed[i]>1 or speed[i]<-1:
                return False
        return True

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

    def policy_data(self,info):
        f = open("{}_sp.pkl".format(info), "wb")
        pickle.dump(self.d_pos_t_step, f)
        f.close()
        return "path: {}".format((self.all_path_number))


    def pre_calc_tran_dict(self):
        pass



from collections import Counter
import pickle


def counter_method(l):
    size = float(len(l))
    res = Counter(l)
    return [(k,v/size) for k,v in res.items()]


def intWithCommas(x):
    if type(x) not in [type(0)]:
        raise TypeError("Parameter must be an integer.")
    if x < 0:
        return '-' + intWithCommas(-x)
    result = ''
    while x >= 1000:
        x, r = divmod(x, 1000)
        result = ",%03d%s" % (r, result)
    return "%d%s" % (x, result)

class GGrid:

    def __init__(self,x,y):
        self.x_size=x
        self.y_size = y


if __name__ == "__main__":
    print ("-----MY--------")
    s=5
    gird_i = GGrid(s,s)
    res = get_short_path_from_grid(gird_i,(0,0),(s-1,s-1))
    print (intWithCommas(len(res)))
    print('end')
    exit()
    for i in range(3,20):
        print ('n=',i,end='\t')
        speed_state = pow((abs(2) * 2) + 1, 2)
        size = pow(((i * i) + 1) * speed_state * 1, 2)
        print (intWithCommas(size))
