

class Box:

    def __init__(self,size=2,exception=True):
        self.agents=[]
        self.size_space=size
        self.goal=False
        self.symbol=' '

    def set_symbol(self,char):
        self.symbol=char

    def del_all_player(self):
        del self.agents[:]

    def del_player(self,agnet_to_string):
        if agnet_to_string in self.agents:
            self.agents.remove(agnet_to_string)
        else:
            self.error_handling('trying to remove agent that is not in the box')

    def set_player(self,agnet_to_string):
        if agnet_to_string in self.agents:
            self.error_handling('try to set the same agent twice')
        self.agents.append(agnet_to_string)

    def error_handling(self, msg):
        if self.error_exception:
            raise Exception(msg)
        else:
            print("[warning] {}".format(msg))

    def __str__(self):
        str_res = '|'
        str_res+="{}".format(self.symbol)
        size = len(self.agents)
        diff = self.size_space - size
        str_res += ' ' * diff*2
        if diff < 0 :
            raise Exception("need to incrse the size space bar by {}".format(diff*-1))
        player_str=','.join(self.agents)
        str_res += player_str
        str_res += '|'
        return str_res


if __name__ == "__main__":
    print ("Box class")