

import numpy as np
from queue import Queue
from random import choice

class short_path_policy:

    def __init__(self,d_factor,lambda_val,eligibility,learning_rate):
        self.eligibility_traces_table={}
        self.eligibility_value=eligibility
        self.lambda_factor=lambda_val
        self.q_table = {}
        self.epslion=0
        self.ctr_state=0
        self.learning_rate = learning_rate
        self.discount_factor=d_factor
        self.state_dict={}
        self.time_seq=0
        self.matrix_q=None
        self.action_map=None
        self.eligibility_q=None

    def rest(self,dict_info=None):
        self.eligibility_q={}
        self.cum_reward = 0
        self.cum_td_error = 0
        self.ctr_num_update=0

    def get_action(self,state,id_agnet):
        a = self.e_greedy_policy(str(state))
        return a


    def init_matrix(self,size_grid,num_agents,action_size=9,speed_state=25,dead_state=1,max_b=30):
            state_size_overall = pow((size_grid+dead_state)*speed_state*max_b,num_agents)
            self.matrix_q = np.zeros((state_size_overall, action_size))
            self.action_map = {'(0,0)': 0, '(0,1)': 1, '(0,-1)': 2, '(1,0)': 3
                , '(1,1)': 4, '(1,-1)': 5, '(-1,0)': 6, '(-1,1)': 7, '(-1,-1)': 8}
            self.eligibility_q = Queue(maxsize=size_grid)

    def num_to_action(self,num):
        for k,v in self.action_map.items():
            if num == v:
                return k
        raise Exception('no value in the action map that is map to action a {} -> {}'
                        .format(num,self.action_map))


    def set_state_q_table(self,state_str):
        self.q_table[state_str]=self.ctr_state
        entry_val = self.ctr_state
        self.ctr_state+=1
        return entry_val


    def e_greedy_policy(self,state,exploration=True):
        """
        @:param state_str_s to_string of a state
        """
        state_str_s = str(state)
        # check that the state in the matrix
        if state_str_s not in self.q_table:
            entry_state_val = self.set_state_q_table(state_str_s)
        else:
            entry_state_val = self.q_table[state_str_s]

        # draw a number for the exploration
        if np.random.rand() < self.epslion and exploration:
            # exploration a new action
            l_action = list(self.action_map.values())
        else:
            # in case there is two or more max q values
            all_action = np.argwhere(self.matrix_q[entry_state_val, :] == np.amax(self.matrix_q[entry_state_val, :]))
            l_action = all_action.flatten().tolist()

        # choose one action randomly
        action = choice(l_action)
        #action = l_action[action_num]
        return self.num_to_action(action)


    def update_policy(self,state_old,state_new):
        if str(state_old) == str(state_new):
            self.rollback_update()
        else:
            self.q_update()


    def get_q_value(self,state_str,action_a):
        state_str = str(state_str)
        entry_val_action = self.action_map[action_a]
        if state_str in self.q_table:
            entry_val_state = self.q_table[state_str]
            return self.matrix_q[entry_val_state,entry_val_action],entry_val_state,entry_val_action
        else:
            entry_val_state = self.set_state_q_table(state_str)
            return self.matrix_q[entry_val_state,entry_val_action],entry_val_state,entry_val_action


    def update_q_table(self, stat_cur, action_cur, next_state, next_action, reward):
        q_val_cur, cur_state_entry, cur_action_entry = self.get_q_value(stat_cur, action_cur)
        q_val_next, next_state_entry, next_action_entry = self.get_q_value(next_state, next_action)

        # td_error = float(reward) + self.discount_factor * q_val_next - q_val_cur
        td_error = self.calc_td_error(reward, q_val_cur, q_val_next)
        self.update_eligibility(cur_state_entry, cur_action_entry)
        self.update_all_recent_state(td_error)


    def calc_td_error(self,reward,q_vale,q_value_next=None):
        # time ctr ++
        self.time_seq+=1
        # update the number of updates that done
        self.ctr_num_update+=1
        # up date the acc reward
        self.cum_reward+=reward

        if q_value_next is None:
            td_error =  float(reward) - q_vale
        else:
            td_error= float(reward) + (self.discount_factor * q_value_next) - q_vale
        # update the td_error acc
        self.cum_td_error+=td_error
        return td_error

    def update_eligibility(self, str_state, action_a):
        key_i = "{}_{}".format(str_state, action_a)
        if key_i not in self.eligibility_q:
            self.eligibility_q[key_i] = 0
        self.eligibility_q[key_i] += 1

    def lower_eligibility_trace(self):
        '''
        lower all the Eligibility Trace for each state-action pair #TODO:FIXXXX
        '''
        to_del = []
        for k in self.eligibility_q:
            if self.eligibility_q[k] <= self.epslion_eligibility:
                # to_del.append(k)
                self.eligibility_q[k] = self.eligibility_q[k] * self.lamda * self.discount_factor
            else:
                self.eligibility_q[k] = self.eligibility_q[k] * self.lamda * self.discount_factor
        for key_i in to_del:
            del self.eligibility_q[key_i]
