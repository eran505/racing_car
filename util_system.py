


def stdin_str_to_dict(str_in,splitby=' '):
    d={}
    split_str = str(str_in).split(splitby)
    i=0
    while i<len(split_str):
        if split_str[i].startswith('-'):
            key =split_str[i][1:]
            i+=1
            value = split_str[i]
            d[key]=value
        i+=1
    return d


def str_to_point(str_point,split_by=':'):
    array_point = str(str_point).split(split_by)
    array_pint =[]
    for item in array_point:
        arr = str(item).split(',')
        arr = [int(x) for x in arr]
        array_pint.append(tuple(arr))
    return array_pint



def make_speed_binary(tuple):
    res = []
    for i in range(len(tuple)):
        if tuple[i] > 1:
            res.append(1)
        elif tuple[i] < -1:
            res.append(-1)
        else:
            res.append(tuple[i])
    return res



def diff_tuple(small_t, big_t, minus=True):
    if minus:
        t3 = [big_t[i] - small_t[i] for i in range(len(small_t))]
    else:
        t3 = [small_t[i] + big_t[i] for i in range(len(small_t))]
    return t3

def getAvg(x, n, sum):
    sum = sum + x;
    return float(sum) / n;
import time
if __name__ == "__main__":
    print ('--util--')
    x=1000000
    arr= range(0, x)
    t1 = time.time()
    avg = 0;
    sum_ = 0;
    for i in range(x):
        avg = getAvg(arr[i], i + 1, sum_)
        sum_ = avg * (i + 1)
    print(avg)
    t2 = time.time()
    print (t2-t1)
    t1 = time.time()
    avg = sum(arr)/len(arr)
    print ( avg )
    t2 = time.time()
    print(t2 - t1)
    #std_in_string = '-x 10 -y 9 -G 0,0:0,8 -A 1:random -B 1:random -B_s 1,1 -A_s 8,0'
    #print (stdin_str_to_dict(std_in_string))


