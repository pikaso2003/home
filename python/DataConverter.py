#
#   Comments :      Containts
#                   pickle_write, pickle_read, datacontainer, datacleaner
#
#   Arguments :
#
#   Return :
#
# ---------------------------------------------------------------------------------
#   Date        Developer       Action
#   15/09/03    Hirayu
#   
#
import numpy as np
import pandas as pd
import os
import pickle
import InsuranceTools.YearTable as Ityt
from colorama import Fore, Back, Style


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


# separator checker of txt file
# ' \t ' -> 1
#  ', ' -> 0
def sep_checker(filename):
    output = open(filename)
    s = output.readlines()
    if '\t' in s[len(s) - 1]:
        return 1
    else:
        return 0


# data container : contains datas as pandas format by using pickle method
# arg : arg1 -> directory of raw datas
#       arg2 -> directory of onverted panda pkl datas
def datacontainer(data_loc_raw, data_loc_pkl):
    data_list = os.listdir(data_loc_raw)
    for i in range(len(data_list)):
        data_name = data_list[i].split('.')[0]
        if sep_checker(data_loc_raw + data_list[i]):
            data_pd = pd.read_table(data_loc_raw + data_list[i])
            pickle_write(data_pd, data_loc_pkl + data_name + '.pkl')
        else:
            data_pd = pd.read_csv(data_loc_raw + data_list[i])
            pickle_write(data_pd, data_loc_pkl + data_name + '.pkl')


# data cleaner : fillNA and other functions implemented
#
def datacleaner(data_loc_raw, data_loc_pkl, data_loc_cl, cycle):
    datacontainer(data_loc_raw, data_loc_pkl)
    data_pkl_list = os.listdir(data_loc_pkl)
    for i in data_pkl_list:
        data_name = i.split('.')[0]
        df = pickle_read(data_loc_pkl + i).reindex(range(0, cycle))
        df = df.fillna(0.)
        pickle_write(df, data_loc_cl + data_name + '.pkl')


# flag maker : e.g. Premium column [ 1, 1, 1, 1, 2, 1, 1, ... ] for each peril
#               by inspecting columns of each peril
# todo                          NOTE : argument is pickle list  e.g ) [ x1.pkl, x2.pkl, ... ]
def column_expression(df):  # Column Viewer
    for i in range(len(df.columns)):
        print('%d : %s' % (i, df.columns[i]))


def key_word_checker(df, key_word):  # Return column number arg : df(Dataframe checked)   key_word(String)
    target_column = []
    for i in range(len(df.columns)):
        if key_word in df.columns[i]:
            target_column.append(i)
        else:
            pass
    print('%d datas added ...' % len(target_column))
    return target_column


def flag_maker(cleaned_data_dir, pd_pkl_list):
    flag_list = []
    for i in pd_pkl_list:
        print(Fore.LIGHTRED_EX + 'following data name -> ' + i + Fore.RESET)
        df = pickle_read(cleaned_data_dir + i)
        column_expression(df)
        print('-' * 100)
        print(
            'Choose \n 1) \t \t Key Word Selection e.g. Loss... \n 2) \t \t Select all \n Others) \t Self Number Specification or pass e.g. 1 2 3 \n')
        selector = raw_input()
        if selector == '1':
            print('Input Key Word :'),
            key_word = raw_input()
            flag_list.append(key_word_checker(df, key_word))
            print('*' * 100)
            print('*' * 100)
        elif selector == '2':
            print('All dataframe were selected. ')
            flag_list = range(len(df.columns))
        else:
            print('-' * 100)
            print('input target column numbers. \n If there is no target, then press RETURN . \n Input : '),
            target_column = raw_input()
            flag_list.append(target_column.split())
            print('%d datas added ...' % len(target_column.split()))
            print('*' * 100)
            print('*' * 100)
    print('input has finished.')
    print('-' * 100)
    return flag_list


# accumulator : accumulator of YearTable data
# output is DataFrame that has 1 column sumed by muti columns.
# write DataFrame into current directory
def accumulator(cycle, flag_list, cleaned_data_dir, pd_pkl_list, df_name):
    df = pd.DataFrame(np.zeros(cycle))
    for i in range(len(flag_list)):
        print('%d / %d   processing ...' % (i, len(flag_list)))
        if len(flag_list[i]) == 0:
            pass
        else:
            for j in flag_list[i]:
                j = int(j)
                df = pd.concat([df, pickle_read(cleaned_data_dir + pd_pkl_list[i]).ix[:, j]], axis=1)
    pickle_write(df.sum(axis=1), df_name)


# Making YearTable class
# pickle YearTable class into YearTable_class directry 'YearTable_class'
# making CSV DataFrame from pickled DataFrame 'YearTable_csv/raw_csv'
def yt_class_maker(accumulated_dir, df_name):
    pd_pkl_list = os.listdir(accumulated_dir)

    if 'YearTable_class' in pd_pkl_list:
        pass
    else:
        os.mkdir(accumulated_dir + 'YearTable_class')
    if 'YearTable_csv' in pd_pkl_list:
        pass
    else:
        os.mkdir(accumulated_dir + 'YearTable_csv')

    pd_pkl_list_raw = os.listdir(accumulated_dir + 'YearTable_csv')
    if 'raw_csv' in pd_pkl_list_raw:
        pass
    else:
        os.mkdir(accumulated_dir + 'YearTable_csv/raw_csv')

    if df_name + '.pkl' in pd_pkl_list:
        temp = pickle_read(accumulated_dir + df_name + '.pkl')
        # making pickle object of YearTable class
        pickle_write(Ityt.YearTable(np.array(temp), df_name), accumulated_dir + 'YearTable_class/' + df_name + '.pkl')
        # making CSV data from pandas DataFrame
        temp.to_csv(accumulated_dir + 'YearTable_csv/raw_csv/' + df_name + '.csv', sep='\t', index=False)
    else:
        pass


# This function is altenate for above function in case of using raw CSV datas
# read from CSV file in 'YearTable_csv/raw_csv'
# and write pickled CSV into accumulated_dir
# and write YearTable class into 'YearTable_class'
def csv_to_df_YTclass(accumulated_dir):
    temp_list = os.listdir(accumulated_dir + 'YearTable_csv/raw_csv')
    for i in temp_list:
        df = pd.read_csv(accumulated_dir + 'YearTable_csv/raw_csv/' + i)
        j = i.replace('.csv', '.pkl')
        pickle_write(df, accumulated_dir + j)
        pickle_write(Ityt.YearTable(np.array(df), df.name), accumulated_dir + 'YearTable_class/' + j)
