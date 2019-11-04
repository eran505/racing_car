

import copy
from ast import literal_eval
class game_state:

    def __init__(self,gird=None):
        self.player_position={}
        #self.player_angle={}
        self.speed={}
        self.player_budget={}
        self.team_dict={'A':-1,'B':1}
        self.dead_state=('na','na')
        self.grid=gird
        self.goal_reward=  -10.0
        self.coll_reward=   10.0
        self.wall_reward=   -1.0

    @staticmethod
    def string_to_state(string_str,grid,split='|'):
        state_obj = game_state()
        agents=str(string_str).split(split)
        for agent_o in agents:
            info = str(agent_o).split('_')
            state_obj.player_position[info[0]]=literal_eval(info[1])
            state_obj.speed[info[0]] = literal_eval(info[2])
            state_obj.player_budget[info[0]] = int(info[3])
        state_obj.grid = grid
        return state_obj

    def dead_player_position(self,agent_id):
        self.player_position[agent_id]=self.dead_state
        self.speed[agent_id]=(0,0)
        self.player_budget[agent_id] = 0.0


    def is_wall_state(self):
        l_wall=[]
        for ky in self.player_position:
            if self.player_position[ky] == self.dead_state:
                l_wall.append(ky)
        if len(l_wall) == 0:
            return None
        return l_wall




    def get_agent_speed(self,agent_id):
        return self.speed[agent_id]

    def set_agent_speed(self,agent_id,speed):
        self.speed[agent_id]=speed

    def get_agent_position(self,agent_id):
        return self.player_position[agent_id]

    def set_agent_position(self,agent_id,new_pos):
        self.player_position[agent_id]=new_pos

    def get_agent_budget(self,agent_id):
        return self.player_budget[agent_id]

    def set_agent_budget(self,agent_id,new_budget):
        self.player_budget[agent_id] = new_budget

    def get_agent_team(self,agent_id):
        return self.team_dict[agent_id]

    def set_agent_team(self, agent_id,team_id):
        self.team_dict[agent_id]=team_id


    def state_rollback_exclude_budget(self,state_old):
        self.player_position = copy.deepcopy(state_old.player_position)
        self.speed = copy.deepcopy(state_old.speed)
        self.set_agent_speed('B1',(0,0))

    def budget_checking(self):
        out_of_budget_list=[]
        for p  in self.player_budget.keys():
            if self.player_budget[p]<= 0 and self.player_position[p]!=self.dead_state:
                out_of_budget_list.append(p)
        if len(out_of_budget_list)==0:
            return None
        return out_of_budget_list

    def check_gaol(self):
        in_goal=[]
        for p in self.player_position.keys():
            team = str(p)[:-1]
            if team == 'B':
                continue
            pos = self.player_position[p]
            for goal in self.grid.goals_box:
                same = True
                for i in range(len(goal)):
                    if pos[i] != goal[i]:
                        same=False
                        break
                if same:
                    in_goal.append(p)
        if len(in_goal)==0:
            return None
        return in_goal

    def collusion(self):
        d={}
        d_ctr={}
        l_ans = []
        for p in self.player_position.keys():
            team = str(p)[:-1]
            pos = self.player_position[p]
            tuple_pos=tuple(pos)

            if tuple_pos == self.dead_state:
                continue

            if tuple_pos not in d:
                d_ctr[tuple_pos]=0
                d[tuple_pos]=[]
            d[tuple_pos].append({'team':team,'p':p})
            d_ctr[tuple_pos]+=self.team_dict[team]
        for ky in d.keys():
            if len(d[ky])>1:
                if len(d[ky]) != d_ctr[ky]:
                    l_ans.append(d[ky])
        if len(l_ans)==0:
            return None
        return l_ans

    def __str__(self):
        keyz = self.player_position.keys()
        list_p = []
        for ky in keyz:
            p = self.player_position[ky]
            s = self.speed[ky]
            b = self.player_budget[ky]
            str_ky = "{}_{}_{}_{}".format(ky,tuple(p),tuple(s),10)
            list_p.append(str_ky)
        return "|".join(list_p)

    def get_deep_copy(self):
        return copy.deepcopy(self)

    def get_deep_copy_state(self):
        #copy.deepcopy =
        new_state = game_state()
        new_state.player_position = copy.deepcopy(self.player_position)
        new_state.speed = copy.deepcopy(self.speed)
        new_state.player_budget = copy.deepcopy(self.player_budget)
        new_state.grid= self.grid
        return new_state

    def is_wall_by_id(self,id_player):
        pos = self.player_position[id_player]
        if pos[0] == self.dead_state[0] and pos[1] == self.dead_state[1]:
            return False
        if self.grid.is_vaild_move(pos[0],pos[1]) is False:
            return True
        else:
            return False



    def is_wall_all(self):
        for ky in self.player_position:
            if self.is_wall_by_id(ky):
                return True
        return False

    def get_reward_by_id(self,id_player):
        results = self.check_gaol()
        if results is not None:
            return self.goal_reward
        results = self.collusion()
        if results is not None:
            return self.coll_reward
        if self.is_wall_by_id(id_player):
            return self.wall_reward
        return 0


    def get_reward_by_state(self):
        results = self.check_gaol()
        if results is not None:
            return self.goal_reward
        results = self.collusion()
        if results is not None:
            return self.coll_reward
        return 0

    def state_to_string_no_budget(self,budget=10):
        keyz = self.player_position.keys()
        list_p = []
        order_list = []
        for name in keyz:
            if str(name).__contains__('B'):
                order_list.append(name)

        for ky in keyz:
            p = self.player_position[ky]
            s = self.speed[ky]
            str_ky = "{}_{}_{}_{}".format(ky,tuple(p),tuple(s),budget)
            list_p.append(str_ky)
        return "|".join(list_p)

