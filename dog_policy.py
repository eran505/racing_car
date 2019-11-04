

import util_system
class dog:

    def __init__(self):
        self.name = 'Dog'
        self.chase_on='A1'

    def get_action(self,state,id_agnet,policy_eval,action_obj):
        cur_pos = tuple(state.get_agent_position(id_agnet))
        speed_cur = tuple(state.get_agent_speed(id_agnet))

        cur_pos_op   = tuple(state.get_agent_position(self.chase_on))

        diff_pos = util_system.diff_tuple(cur_pos,cur_pos_op)
        a  = util_system.make_speed_binary(diff_pos)

        return a


    def rest(self,dict_info=None):
        pass

    def get_tran(self):
        return None

    def policy_data(self,info):
        return "dog"
