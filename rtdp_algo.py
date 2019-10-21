
from time import time
from planner import init_dict_state_helper,construct_map_state
import numpy as np
import state
from random import choice

from action import action_drive
class rtdp:

    def __init__(self,grid):
        self.history=[]
        self.name='RTDP'
        self.matrix_q=None
        self.players = ['A1','B1']
        self.num_of_epsiode=None
        self.state_absorbed_map=None
        self.action_object=None
        self.dynamic_alloction=True
        self.discounted_factor=0.8
        self.ctr_insert_state=0
        self.grid=grid
        self.ctr_state=0
        self.map_state=None
        self.heuristic_value_upper_bound = 10.1
        self.transaction_action=None
        self.action_map=None
        self.sum_tran_p=None
        self.size_action=-1
        self.transitions=None
        self.action_map_rev=None
        self.tmp_d = None
        self.default_actions=[]
        self.init_action_map()
        self.dynamic_state_map={}

    def policy_data(self):
        return "state: {}".format((self.ctr_state))

    def init_action_map(self):
        self.action_map =\
            {(0,0): 0, (0,1): 1, (0,-1): 2, (1,0): 3
            , (1,1): 4, (1,-1): 5, (-1,0): 6, (-1,1): 7, (-1,-1): 8}

        self.action_map_rev = {v: k for k, v in self.action_map .items()}
        self.transaction_action=np.zeros(len(self.action_map))
        self.transaction_action[self.action_map[(0,0)]]=0.1
        self.sum_tran_p = np.sum(self.transaction_action)
        self.size_action = len(self.action_map)
        self.default_actions = [(0,0)]


    def full_init(self,x,y,num_agents,max_speed,full,max_b=1,frac_mem=5):
        speed_state = pow((abs(max_speed)*2)+1,2)
        state_size_overall = pow(((x * y) + 1) * speed_state * max_b, num_agents)
        print ("state_size_overall: ",state_size_overall )
        state_size_overall = round(state_size_overall * (float(1)/float(frac_mem)))
        if full is False:
            self.matrix_q = np.full((state_size_overall, len(self.action_map)), self.heuristic_value_upper_bound)
        else:
            self.matrix_q = np.full((state_size_overall, len(self.action_map)),self.heuristic_value_upper_bound)
            if self.dynamic_alloction is False:
                self.map_state= construct_map_state(x,y,max_speed,num_agents,self.players)
                self.state_absorbed()
        print ('done')



    def init_policy(self,x,y,max_speed=2,player_number=2,full=True):
        self.full_init(x,y,player_number,max_speed,full)



    def rest(self,obj):
        pass


    def get_tran(self):
        return None

    def up_date_q_observing(self,string_i,reward):
        for state_i in self.state_absorbed_map[string_i]:
            entry_q = self.map_state[state_i]
            self.matrix_q[entry_q, :]=np.full((self.size_action),reward)




    def state_absorbed(self):
        d_goal={}
        d_coll={}
        obj_state=None
        for state_i in self.map_state:
            obj_state = state.game_state.string_to_state(state_i,self.grid)
            if obj_state.check_gaol() is not None:
                d_goal[state_i]=True
            elif obj_state.collusion() is not None:
                d_coll[state_i] = True
        self.state_absorbed_map={'goal':d_goal,'collusion':d_coll}
        self.up_date_q_observing('goal',obj_state.goal_reward)
        self.up_date_q_observing('collusion', obj_state.coll_reward)



    # def update_q_value(self,action_object,s_state):
    #     expected_retrun_value = action_object.expected_return_reward(s_state)
    #     acc=0.0
    #     for tuple in expected_retrun_value :
    #         q_val = np.amax(self.matrix_q[self.map_state[tuple[1]],:])
    #         acc+=tuple[0]*q_val
    #     return acc


    def update_policy(self,s_old,r,a,r_new,action_obj):
        # print("update_policy")
        # print (s_old)
        # print(a)
        # old_state_entry = self.map_state[s_old.state_to_string_no_budget()]
        # action_entry = self.action_map[a]
        # print(self.matrix_q[old_state_entry ,:])
        # for a_i in self.action_map:
        #     self.matrix_q[old_state_entry , self.action_map[a_i]] = self.tmp_d[a_i]
        # print(self.matrix_q[old_state_entry, :])

        #self.history.append((s_old.state_to_string_no_budget(),a,self.tmp_d[a]))

        return True

    def get_action_all(self,state,player_id,policy_eval,action_object):
        action_a = action_object
        dict_action_info = action_a.get_expected_reward(player_id)
        a = self.greedy_action_taking(state,dict_action_info,policy_eval)
        return a

    # def get_max_action(self,state_cur):
    #     cur_str_state = state_cur.state_to_string_no_budget()
    #     entry_q = self.map_state[cur_str_state]
    #     ## TODO:
    #     #c = [np.random.choice(np.flatnonzero(b == b.max())) for i in range(100000)]
    #     #action_entry = np.argmax()
    #
    #     arg_max_list = np.argwhere(self.matrix_q[entry_q, :]  == np.amax(self.matrix_q[entry_q, :]))
    #     winner = arg_max_list.flatten().tolist()
    #     if len(winner)==1:
    #         return self.action_map_rev[winner[0]]
    #
    #     a_entry = choice(winner)
    #     return self.action_map_rev[a_entry]
    #


    def get_action(self,state, player_id,policy_eval,action_a):
        action_a.set_state(state)
        dict_action_info = action_a.get_expected_reward(player_id)
        if self.dynamic_alloction is False:
            a = self.greedy_action_taking(state,dict_action_info,policy_eval)
        else:
            a = self.greedy_action_taking_on_fly(state, dict_action_info, policy_eval)
        return a

    def greedy_action_taking(self, state_cur, d_action ,policy_eval):
        '''
        Q(S,A) = R(S,A)+ discount*T(S'|S,A)*V(S')
        V(S)=max_a{Q(S,A)}
        '''

        state_old_str = state_cur.state_to_string_no_budget()
        entry_q = self.map_state[state_old_str]
        d_expected_value={}
        vector = np.zeros((self.size_action))
        for action_a in d_action:
            action_entry = self.action_map[action_a]
            state_s_list = d_action[action_a][0]
            is_wall = d_action[action_a][-1]
            size_l = len(state_s_list)
            vector_i = np.zeros((size_l))
            tran_vec = np.zeros((size_l))
            ctr=0
            for item in state_s_list:

                state_s=item[0]
                transition_probability=item[-1]
                tran_vec[ctr]=transition_probability
                if is_wall:
                    q_value=state_cur.wall_reward
                else:
                    next_state_entry = self.map_state[state_s]
                    q_value = np.amax(self.matrix_q[next_state_entry, :])

                vector_i[ctr] = q_value

                # if state_s in self.state_absorbed_map['collusion']:
                #     vector_i[ctr] = d_action[action_a][1] + q_value * self.discounted_factor
                # elif state_s in self.state_absorbed_map['goal']:
                #     vector_i[ctr] = d_action[action_a][1] + q_value * self.discounted_factor
                # else:
                #     vector_i[ctr] = q_value*self.discounted_factor + d_action[action_a][1]

                ctr+=1
            vector[action_entry]=np.dot(vector_i,tran_vec)


        vector = vector*self.discounted_factor


        for ky in d_action:
            action_entry = self.action_map[ky]
            self.transaction_action[action_entry]+=(1.0-self.sum_tran_p)

            d_expected_value[ky]= np.round(np.dot(vector,self.transaction_action),6) \
                                   + d_action[ky][1]
            self.transaction_action[action_entry] -= (1.0 - self.sum_tran_p)

        arg_max_action = action_drive.keywithmaxval(d_expected_value)

        if policy_eval:
            return arg_max_action


        for key_i,v_i  in d_expected_value.items():
            self.matrix_q[entry_q , self.action_map[key_i]] = v_i



        return arg_max_action



    def get_state_entry(self,state_str):
        if state_str not in self.dynamic_state_map:
            self.dynamic_state_map[state_str]=self.ctr_state
            self.ctr_state= self.ctr_state + 1
            return self.ctr_state-1
        return self.dynamic_state_map[state_str]

    def greedy_action_taking_on_fly(self, state_cur, d_action ,policy_eval):
        '''
        Q(S,A) = R(S,A)+ discount*T(S'|S,A)*V(S')
        V(S)=max_a{Q(S,A)}
        '''

        state_old_str = state_cur.state_to_string_no_budget()
        entry_q= self.get_state_entry(state_old_str)
        d_expected_value={}
        vector = np.zeros((self.size_action))
        for action_a in d_action:
            action_entry = self.action_map[action_a]
            state_s_list = d_action[action_a][0]
            is_wall = d_action[action_a][-1]
            size_l = len(state_s_list)
            vector_i = np.zeros((size_l))
            tran_vec = np.zeros((size_l))
            ctr=0
            for item in state_s_list:
                state_s=item[0]
                transition_probability=item[-1]
                r =  item[1]
                tran_vec[ctr]=transition_probability
                if r != 0 :
                    q_value=r
                else:
                    next_state_entry = self.get_state_entry(state_s)
                    q_value = np.amax(self.matrix_q[next_state_entry, :])

                vector_i[ctr] = q_value

                # if state_s in self.state_absorbed_map['collusion']:
                #     vector_i[ctr] = d_action[action_a][1] + q_value * self.discounted_factor
                # elif state_s in self.state_absorbed_map['goal']:
                #     vector_i[ctr] = d_action[action_a][1] + q_value * self.discounted_factor
                # else:
                #     vector_i[ctr] = q_value*self.discounted_factor + d_action[action_a][1]

                ctr+=1
            vector[action_entry]=np.dot(vector_i,tran_vec)


        vector = vector*self.discounted_factor


        for ky in d_action:
            action_entry = self.action_map[ky]
            self.transaction_action[action_entry]+=(1.0-self.sum_tran_p)

            d_expected_value[ky]= np.round(np.dot(vector,self.transaction_action),6) \
                                   + d_action[ky][1]
            self.transaction_action[action_entry] -= (1.0 - self.sum_tran_p)

        arg_max_action = action_drive.keywithmaxval(d_expected_value)

        if policy_eval:
            return arg_max_action

        # Update
        #print (self.matrix_q[entry_q, :])

        for key_i,v_i  in d_expected_value.items():
            self.matrix_q[entry_q , self.action_map[key_i]] = v_i

        #print(self.matrix_q[entry_q,:])

        return arg_max_action



if __name__ == "__main__":
    #print ('RTDP')

    arr2D = np.array(   [[11, 12, 13,11, 12, 13],
                         [14, 15, 16,11, 12, 13],
                         [17, 15, 11,11, 12, 13],
                         [15, 14, 15,11, 12, 15]])

    print (np.round((1/float(3)*7+1/float(3)*7+1/float(3)*7),5))
    print ( np.amax(arr2D[3,:]))