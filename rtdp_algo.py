
from time import time
from planner import init_dict_state_helper,construct_map_state
import numpy as np
import state
from math import ceil,floor
from random import choice
import pickle
import util_system
from action import action_drive
class rtdp:

    def __init__(self,grid,max_speed_agant):
        self.history=[]
        self.name='RTDP'
        self.max_speed=max_speed_agant
        self.matrix_q=None
        self.players = ['A1','B1']
        self.num_of_epsiode=None
        self.state_absorbed_map=None
        self.action_object=None
        self.dynamic_alloction=True
        self.discounted_factor=0.985
        self.ctr_insert_state=0
        self.grid=grid
        self.ctr_state=0
        self.map_state=None
        self.heuristic_value_upper_bound = 0.0
        self.transaction_action=None
        self.action_map=None
        self.sum_tran_p=None
        self.size_action=-1
        self.transitions=None
        self.action_map_rev=None
        self.tmp_d = None
        self.stack_states=[]
        self.default_actions=[]
        self.init_action_map()
        self.dynamic_state_map={}

    def policy_data(self,info):
        np.save("{}_Q".format(info),self.matrix_q)
        f = open("{}_dict.pkl".format(info), "wb")
        pickle.dump(self.dynamic_state_map, f)
        f.close()
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


    def full_init(self,x,y,num_agents,arr_max_speed,full,max_b=1,frac_mem=3.5):
        state_size_overall=1
        for max_speed in arr_max_speed:
            speed_state = pow((abs(max_speed)*2)+1,2)
            state_size_overall*= ((x * y) + 1) * speed_state * max_b
        print ("state_size_overall: ",state_size_overall )
        #state_size_overall = round(state_size_overall * (float(1)/float(frac_mem)))
        print ("modify size: ",state_size_overall)
        #state_size_overall = 100
        if full is False:
            self.matrix_q = np.full((state_size_overall, len(self.action_map)), self.heuristic_value_upper_bound)
        else:
            self.matrix_q = np.full((state_size_overall, len(self.action_map)),self.heuristic_value_upper_bound)
            if self.dynamic_alloction is False:
                self.map_state= construct_map_state(x,y,max_speed,num_agents,self.players)
                self.state_absorbed()
        print ('done')



    def init_policy(self,x,y,arr_max_speed,player_number=2,full=True):
        self.full_init(x,y,player_number,arr_max_speed,full)



    def rest(self,obj):
        self.action_object=obj
        if len(self.stack_states)>0:
            # Do Backup update
            #print (self.stack_states)
            #tmp_stack = self.stack_states
            #tmp_stack.reverse()
            size = len(self.stack_states)
            for i in range(size-2,-1,-1):
                item = self.stack_states[i]
                obj.set_state(item[0])
                str_state = item[0].state_to_string_no_budget()
                self.up_date_action_stae(item[-1], str_state, obj, 'B1', True)
        self.stack_states=[]


    def get_tran(self):
        return None

    def up_date_q_observing(self,string_i,reward):
        for state_i in self.state_absorbed_map[string_i]:
            entry_q = self.map_state[state_i]
            self.matrix_q[entry_q, :]=np.full((self.size_action),reward)


    def print_matrix(self):
        print(self.action_map)
        print(self.matrix_q[:self.ctr_state,:])

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



    def get_action_all(self,state,player_id,policy_eval,action_object):
        action_a = action_object
        dict_action_info = action_a.get_expected_reward(player_id)
        a = self.greedy_action_taking(state,dict_action_info,policy_eval)
        return a

    def get_max_action(self,state_cur):
        cur_str_state = state_cur.state_to_string_no_budget()
        entry_q = self.get_state_entry(cur_str_state)

        arg_max_list = np.argwhere(self.matrix_q[entry_q, :]  == np.amax(self.matrix_q[entry_q, :]))
        winner = arg_max_list.flatten().tolist()
        if len(winner)==1:
            return self.action_map_rev[winner[0]]

        a_entry = choice(winner)
        return self.action_map_rev[a_entry]



    def get_action(self,state, player_id,policy_eval,action_a):
        action_a_ch = self.get_max_action(state)
        ##action_a_ch=(1,0)
        if policy_eval is False:
            self.up_date_action_stae(action_a_ch,state.state_to_string_no_budget(),action_a,player_id)

            # inset to stack
            self.stack_states.append((state.get_deep_copy(),action_a_ch))

        return action_a_ch

    def get_action_od(self,state, player_id,policy_eval,action_a):
        action_a.set_state(state)
        dict_action_info = action_a.get_expected_reward(player_id)
        if self.dynamic_alloction is False:
            a = self.greedy_action_taking(state,dict_action_info,policy_eval)
        else:
            a = self.greedy_action_taking_on_fly(state, dict_action_info, policy_eval)
        return a



    def get_state_entry(self,state_str):
        ##print(state_str,'\t\t',self.ctr_state)
        if state_str not in self.dynamic_state_map:
            self.dynamic_state_map[state_str]=self.ctr_state
            self.ctr_state= self.ctr_state + 1


            self.func_heuristic_value_upper_bound(state_str,self.ctr_state-1)

            return self.ctr_state-1
        return self.dynamic_state_map[state_str]




    def up_date_action_stae(self,action_a,s_state,action_obj,player_id,backup=False):
        entry_q= self.get_state_entry(s_state)
        d_res = action_obj.get_expected_reward_by_action(player_id,action_a)
        d_expected_value = self.bellman_eq(d_res,s_state)
        for key_i,v_i  in d_expected_value.items():
            #b = self.matrix_q[entry_q , self.action_map[key_i]]
            #if b<v_i:
            #    print("before={}_after={}".format(b,v_i))
            #    print()
            self.matrix_q[entry_q , self.action_map[key_i]] = v_i


    def func_heuristic_value_upper_bound(self,state_s,entry_q,reward=10.0):
        state_obj_new = state.game_state.string_to_state(state_s, None)
        l = self.action_object.tran['A1'].hurstic(state_obj_new, 'A1')
        for action_a in self.action_map:
            str_new_state = util_system.string_change_by_action_id(action_a, 'B1', state_s, self.max_speed)
            list_stepz = []
            for item in l:
                cur_pos, spped_cur = util_system.get_spped_pos(str_new_state, 'B1')
                steps = util_system.distance_max(cur_pos, item[0])
                steps = floor(steps / float(self.max_speed))
                list_stepz.append(steps)
            step = min(list_stepz) #TODO: fix it
            h = pow(self.discounted_factor,step)*reward
            self.matrix_q[entry_q, self.action_map[action_a]] = h




    def bellman_eq(self,d_action,state_old_str):
        #state_old_str = state_cur.state_to_string_no_budget()
        entry_q = self.get_state_entry(state_old_str)
        d_expected_value = {}
        vector = np.zeros((self.size_action))
        for action_a in d_action:
            action_entry = self.action_map[action_a]
            state_s_list = d_action[action_a][0]
            is_wall = d_action[action_a][-1]
            size_l = len(state_s_list)
            cur_reward = d_action[action_a][1]
            if cur_reward!=0:
                continue
            vector_i = np.zeros((size_l))
            tran_vec = np.zeros((size_l))
            ctr = 0
            for item in state_s_list:
                state_s = item[0]
                transition_probability = item[-1]
                r = item[1]
                tran_vec[ctr] = transition_probability
                if r != 0:
                    q_value = 0 + r
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

                ctr += 1
            vector[action_entry] = np.dot(vector_i, tran_vec)

        vector = vector * self.discounted_factor
        # print(vector)
        # print()
        for ky in d_action:
            action_entry = self.action_map[ky]
            self.transaction_action[action_entry] += (1.0 - self.sum_tran_p)

            d_expected_value[ky] = np.round(np.dot(vector, self.transaction_action), 6) +cur_reward
            self.transaction_action[action_entry] -= (1.0 - self.sum_tran_p)

        return d_expected_value

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
                    q_value=0
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
        #print(vector)
        #print()
        for ky in d_action:
            action_entry = self.action_map[ky]
            self.transaction_action[action_entry]+=(1.0-self.sum_tran_p)

            d_expected_value[ky]= np.round(np.dot(vector,self.transaction_action),6) + d_action[ky][1]
            self.transaction_action[action_entry] -= (1.0 - self.sum_tran_p)

        arg_max_action = action_drive.keywithmaxval(d_expected_value)


        # inset to stack
        self.stack_states.append((state_cur.state_to_string_no_budget(),arg_max_action))


        if policy_eval:
            return arg_max_action

        # Update
        #print (self.matrix_q[entry_q, :])

        for key_i,v_i  in d_expected_value.items():
         #   print(self.matrix_q[entry_q , :] )
            self.matrix_q[entry_q , self.action_map[key_i]] = v_i
         #   print(self.matrix_q[entry_q, :])

        #print ('\n\n')

        #print(self.matrix_q[entry_q,:])

        return arg_max_action

    def update_back(self):
        pass



if __name__ == "__main__":
    #print ('RTDP')


    arr2D = np.array(   [[11, 12, 13,11, 12, 13],
                         [14, 15, 16,11, 12, 13],
                         [17, 15, 11,11, 12, 13],
                         [15, 14, 15,11, 12, 15]])


    print (np.round((1/float(3)*7+1/float(3)*7+1/float(3)*7),5))
    print ( np.amax(arr2D[3,:]))