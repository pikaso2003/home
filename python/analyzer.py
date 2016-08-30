#
#   Comments :
#
#   Arguments :
#
#   Return :
#
# ---------------------------------------------------------------------------------
#   Date        Developer       Action
#   
#   
#
import pandas as pd
import pickle
import InsuranceTools
from InsuranceTools.YearTable import YearTable


# pickle writer
def pickle_write(data, filename):
    print('pickle write :', data)
    with open(filename, 'w+') as fw:
        pickle.dump(data, fw)


# pickle reader
def pickle_read(filename):
    with open(filename, 'r') as fw:
        data = pickle.load(fw)
    return data


# todo Note : data_list is singlular.
#  pandas -> Peril class -> Peril class attribute
def analyzer(accumulated_dir, data_list, alpha, beta):
    data_name = data_list.split('.')[0]
    peril_class = pickle_read(accumulated_dir + data_list)
    return [peril_class.name, peril_class.mean(), peril_class.var(alpha), peril_class.xvar(alpha),
            peril_class.tvar(alpha),
            peril_class.xtvar(alpha), peril_class.truntvar(alpha, beta)]


# todo Note :  data_list is prural
def acum_analyzer(accumulated_dir, data_list, alpha, beta):
    ret_array = []
    for i in data_list:
        ret_array.append(analyzer(accumulated_dir, i, alpha, beta))
    return pd.DataFrame(ret_array, columns=['name', 'mean', 'VaR', 'xVaR', 'TVaR', 'xTVaR', 'trun_TVaR'])

# todo Note : Return stats  of data_list name reflecting share value
def analyzer_opt(accumulated_dir, data_list, alpha, beta, opt_w_list, weight_list):
    global peril_class
    data_name = data_list.split('.')[0]
    df = pickle_read(accumulated_dir + data_list)
    for (i, j) in zip(weight_list, opt_w_list):
        if i in data_name:
            peril_class = YearTable(df.yt * j, df.name)
        else:
            pass
    return [peril_class.name, peril_class.mean(), peril_class.var(alpha), peril_class.xvar(alpha),
            peril_class.tvar(alpha),
            peril_class.xtvar(alpha), peril_class.truntvar(alpha, beta)]

# todo Note :
def acum_analyzer_opt(accumulated_dir, data_lists, alpha, beta, opt_w_file, weight_list):
    opt_w_list = pickle_read(opt_w_file)
    ret_array = []
    for i in data_lists:
        ret_array.append(analyzer_opt(accumulated_dir, i, alpha, beta, opt_w_list, weight_list))
    return pd.DataFrame(ret_array, columns=['name', 'mean', 'VaR', 'xVaR', 'TVaR', 'xTVaR', 'trun_TVaR'])
