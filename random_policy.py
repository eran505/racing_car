from random import randint
class rand_policy:

    def __init__(self):
        self.name = 'Random'

    def get_action(self,pos=None,s=None,bol=False,action_object=None):
        x_axis = randint(-1, 1)
        y_xias = randint(-1, 1)
        #return [0,0]
        return [x_axis,y_xias]

    def rest(self,dict_info=None):
        pass

    def get_tran(self):
        return None