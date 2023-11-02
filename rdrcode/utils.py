def read_param_file(param_file_dir):
    meta = open(param_file_dir)
    meta_dict = {}
    for i in meta.readlines():
        if (i[0]!='%'):
            j=i[:-1].split('=') # removing \n's from end of the line
            if (len(j)>1):
                if (j[1].find('%')>0):
                    j[1]=j[1][:j[1].index('%')]  #trim further after
                if (j[1][1]=="'"):
                    j[1]=j[1][2:-1]
                j=[str.strip(k) for k in j] #trimming
                meta_dict[j[0]]=j[1]
    return meta_dict


if __name__=='__main__':
    pass
