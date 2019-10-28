import pandas as pd
import os,re
import numpy as np


def walk_rec(root, list_res, rec="", file_t=True, lv=-800, full=True):
    if root[-1]=='/':
        root=root[:-1]
    size = 0
    ctr = 0
    class_list = list_res
    if lv == 0:
        return list_res
    lv += 1
    for path, subdirs, files in os.walk(root):
        ctr += 1
        if file_t:
            for name in files:
                tmp = re.compile(rec).search(name)
                if tmp == None:
                    continue
                size += 1
                if full:
                    class_list.append(os.path.join(path, name))
                else:
                    class_list.append(str(name))
        else:
            for name in subdirs:
                tmp = re.compile(rec).search(name)
                if tmp == None:
                    continue
                size += 1
                if full:
                    class_list.append(os.path.join(path, name))
                else:
                    class_list.append(str(name))
        for d_dir in subdirs:
            walk_rec("{}/{}".format(path, d_dir), class_list, rec, file_t, lv, full)
        break
    return class_list


def mkdir_system(path_root, name, is_del=True):
    if path_root is None:
        raise Exception("[Error] passing a None path --> {}".format(path_root))
    if path_root[-1] != '/':
        path_root = path_root + '/'
    if os.path.isdir("{}{}".format(path_root, name)):
        if is_del:
            os.system('rm -r {}{}'.format(path_root, name))
        else:
            #print "{}{} is already exist".format(path_root, name)
            return '{}{}'.format(path_root, name)
    print('[OS] mkdir {}{}'.format(path_root, name))
    os.system('mkdir {}{}'.format(path_root, name))
    return '{}{}'.format(path_root, name)


def make_fin_csv(path_dir='/home/ise/car_model',file_name='fin.csv'):
    csv_files = walk_rec(path_dir,[],'N_',lv=-1)
    d = {'Iter': [i for i in range(1000,2000000,1000)]}
    df = pd.DataFrame(d)
    for item in csv_files:
        if str(item).__contains__('G') is False:
            continue
        print (item)

        pd_df = pd.read_csv(item,sep='\t',index_col=0)
        print ('name:\t',list(pd_df))

        name_array = str(item).split('/')[-1].split('.')[0].split('_')
        n=name_array[1]
        goalz = '_'.join(name_array[-3:])
        df['N_{}_{}'.format(n,goalz)]=pd_df['Avg Rerward']
    df.to_csv('{}/{}'.format(path_dir,file_name),sep='\t')


if __name__ == "__main__":
    make_fin_csv()