
from random import choice,randint
from action import action_drive
from graph_policy import short_path_policy
from random_policy import rand_policy

from dog_policy import dog
class agent_player:

    def __init__(self,name,starting_budget,policy,team_symbol):
        self.name_id=name
        self.my_state=None
        self.starting_place_list=[]
        self.goalz=[] #?????
        self.team=team_symbol
        self.speed=None
        self.policy_name = policy
        self.budget=None
        self.start_budget=starting_budget
        self.starting_point=None
        self.policy_object=None
        self.reward=0
        self.ctr_move=0
        self.max_speed = None

    def update_reward(self,r):
        self.reward+=r
    def set_max_speed(self,s):
        self.max_speed=s
    def get_starting_points(self):
        return self.starting_place_list

    def __str__(self):
        string_str = "id={} | r={} | ctr={}".format(self.get_id(),self.reward,self.ctr_move)
        return string_str

    def get_id(self):
        return "{}".format(self.name_id)

    def get_team(self):
        return "{}".format(self.name_id[:-1])

    def reset_agent(self,info=None):
        self.choose_start_state()
        self.budget = int(self.start_budget)
        if self.policy_name=='value':
            self.policy_object.rest(info)
        else:
            self.policy_object.rest({'start': self.starting_point})
        self.reward=0
        self.ctr_move=0

    def set_state(self,s_state):
        self.my_state=s_state

    def get_state(self):
        return  self.my_state

    def set_staring_point_str(self,str_coord):
        arr_point = str(str_coord).split(':')
        for item in arr_point:
            arr = str(item).split(',')
            arr = [int(x) for x in arr]
            point_i = tuple(arr)
            self.set_staring_point(point_i)

    def set_staring_point(self,point):
        self.starting_place_list.append(point)

    def choose_start_state(self):
        if len(self.starting_place_list)>1:
            self.starting_point = choice(self.starting_place_list)
        elif len(self.starting_place_list) == 1:
            self.starting_point = self.starting_place_list[0]
        else:
            raise Exception('No starting point is set - agents class')


    def __eq__(self, other):
        if str(other)==self.get_id():
            return True
        return False

    def update(self,s_old,r,a,s_new,action_obj):
        self.policy_object.update_policy(s_old,r,a,s_new,action_obj)


    def init_policy(self,pathz=None,policy_name='',max_speed=None):
        if policy_name == 'random':
            self.policy_object = rand_policy()
        if policy_name == 'short':
            self.policy_object = short_path_policy(pathz,max_speed)
        if policy_name == 'dog':
            self.policy_object = dog()

    def play(self,state,policy_eval,action_obj):
        self.ctr_move+=1
        speed_addition = self.policy_object.get_action(state,self.name_id,policy_eval,action_obj)
        action_obj.setter(speed_addition ,state)
        r = action_obj.execute_action(self.name_id)
        self.reward+=r
        return speed_addition

    def random_policy(self):
        x_axis = randint(-1, 1)
        y_xias = randint(-1, 1)
        #return  [-1,-1]
        return [x_axis,y_xias]



