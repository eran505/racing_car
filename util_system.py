


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

if __name__ == "__main__":
    print ('--util--')
    #std_in_string = '-x 10 -y 9 -G 0,0:0,8 -A 1:random -B 1:random -B_s 1,1 -A_s 8,0'
    #print (stdin_str_to_dict(std_in_string))


