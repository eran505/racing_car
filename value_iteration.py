import numpy as np
from itertools import product
from itertools import product

from planner import construct_map_state

import state
from action import action_drive
class value_iteration_object:

    def __init__(self,grid):
        self.start_state=state.game_state(grid)
        self.matrix_v={}
        self.action_map =None
        self.ctr_state=0
        self.map_state={}
        self.state_absorbed_map = None
        self.players= ['B1','A1']
        self.transition_prob=0.9
        self.action_wind = (0,0)
        self.discount_factor=float(0.6)
        self.epsilon = 0.0001



    def get_action(self,state,id_agent,policy_eval):
        a = self.greedy_action(state,id_agent)
        #return [0,0]
        return a

    def greedy_action(self,state,id_agent):
        a_obl = action_drive(None,state)
        d={}
        state_reward, d_action, d_wall = a_obl.get_expected_reward(id_agent)
        for action_i in d_action:
            state_i = d_action[action_i]
            if d_wall[state_i] is True:
                continue
            entry_i =self.map_state[state_i]
            v_i = self.matrix_v[entry_i]
            d[action_i]=v_i
        return action_drive.keywithmaxval(d)

    def rest(self,dict_info=None):
        pass

    def update_table(self):
        '''
        V*(s) = max_a sigma{ T(s,a,s')[R(s,a,s')+discount_factor*V*(s')]}
        thsigma beacuse the probabilty of taking the max a action can lead us to diffrent state,
        we want the expecation of this number
        '''
        i=0
        print ("update_table....")
        action_a = action_drive(None,None)
        acc_diff=0
        size_states = len(self.map_state)
        for ky in self.map_state:
            #print (i)
            i += 1
            entry = self.map_state[ky]
            v = self.matrix_v[entry]

            # if we in the absorbed state
            if ky in self.state_absorbed_map['goal']:
                self.matrix_v[entry]=self.start_state.goal_reward
                continue
            if ky in self.state_absorbed_map['collusion']:
                self.matrix_v[entry] = self.start_state.coll_reward
                continue

            state_v = state.game_state.string_to_state(ky,self.start_state.grid)
            action_a.set_state(state_v)
            d_state,d_action,d_wall = action_a.get_expected_reward('B1')
            d_value={}
            d_action_vale={}
            for ky_i in d_state:
                if d_wall[ky_i]:
                    d_value[ky_i]=self.start_state.wall_reward
                    continue
                entry_i = self.map_state[ky_i]
                d_value[ky_i]=self.matrix_v[entry_i] * self.discount_factor

            state_fail_exe = d_action[self.action_wind]
            state_fail_exe_r = d_state[state_fail_exe]
            v_fail = d_value[state_fail_exe]
            reward_fail = v_fail+state_fail_exe_r

            for a in d_action:
                str_s = d_action[a]
                a_reward = d_state[str_s] + d_value[str_s]
                expected_reward = a_reward*self.transition_prob+(1.0-self.transition_prob)*reward_fail
                d_action_vale[a]=expected_reward

            a_max = action_drive.keywithmaxval(d_action_vale)
            acc_diff += abs(v - d_action_vale[a_max])
            self.matrix_v[entry] = d_action_vale[a_max]

        if acc_diff <= self.epsilon * size_states:
            return False
        return True



    def loop_update(self,max_update = 100):
        ctr=0
        for i in range(max_update):
            bol = self.update_table()
            print(ctr)
            ctr+=1
            if bol is False:
                break
        print ("done")



    def init_matrix(self,x,y,num_agents,action_size=9,speed_state=25,dead_state=1,max_b=30):
            state_size_overall = pow(((x*y)+dead_state)*speed_state*max_b,num_agents)
            self.matrix_v = np.zeros(state_size_overall)
            self.action_map = {'(0,0)': 0, '(0,1)': 1, '(0,-1)': 2, '(1,0)': 3
                , '(1,1)': 4, '(1,-1)': 5, '(-1,0)': 6, '(-1,1)': 7, '(-1,-1)': 8}


    def init_dict_state(self,x,y,max_speed=2,num_players=2):
        self.init_matrix(x,y,num_players)
        self.map_state= construct_map_state(x,y,max_speed,num_players,self.players)
        self.state_absorbed()

    def state_absorbed(self):
        d_goal={}
        d_coll={}
        for state_i in self.map_state:
            obj_state = state.game_state.string_to_state(state_i,self.start_state.grid)
            if obj_state.check_gaol() is not None:
                d_goal[state_i]=True
            elif obj_state.collusion() is not None:
                d_coll[state_i] = True
        self.state_absorbed_map={'goal':d_goal,'collusion':d_coll}

if __name__ == "__main__":
    pass
