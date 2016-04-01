# todo 20 Dec 2015
# UWG, Expese, Loss method not implemented


import numpy as np
import pandas as pd


class YT(object):
    """
    Dec.2015 developed by Hirayu
    :arg1   Year Table name
    :arg2   number of year
    :arg3   alpha ( for percentile  )
    :arg4   beta ( for percentile in truncated TVaR )
    :arg5   peril dictionary ( year table should be numpy array )
    :name   YT name
    :n      number of year ( All peril must have same number )
    :alpha  e.g. 100yr VaR -> alpha = 0.99
    :beta   e.g. truncatedTVaR (100yr 200yr) -> alpha = 0.99, beta = 0.995
    :yt_dic
            dictionary type arg which can contain any type of year table
            ( year table value must be list or array. )
            e.g. Premium, any expense, any peril
            ***** NOTE *****
             if you use the dictionary key which will be '_P' for Premium,
                '_E' for Expense, '_nonCAT', and defined Loss Format ('USWS','USEQ',........) for all type of LOSS,
                you can use special method which can calculate
                Under Wrinting Gain, Aggregated Loss, and so on.

                defined Loss Format is as follows.
                USWS, USEQ, EUWS, EUEQ, JPWS, JPEQ, RoW
    """

    def __init__(self, name, n, alpha=0.99, beta=0.998, **yt_dic):
        self.name = name
        self.n = n
        self.YT_dic = yt_dic
        self.weight = [1.0] * len(self.YT_dic)
        self.YT_name = [i for i in yt_dic.keys()]
        self.YT_table = yt_dic.values()
        self.alpha = alpha  # default = 0.99 (100yr)
        self.alpha_n = np.int(np.floor(self.n * self.alpha))
        self.beta = beta  # default = 0.998 (500yr)
        self.beta_n = np.int(np.floor(self.n * self.beta))
        self.premium_dict = {}
        self.expense_dict = {}
        self.noncat_dict = {}
        self.all_peril_dict = {}
        self.peril_list = ['USWS', 'USEQ', 'EUWS', 'EUEQ', 'JPWS', 'JPEQ', 'RoW']

    def __add__(self, another):
        global new_yt_dic
        if another.n == self.n:
            dicts = [self.YT_dic, another.YT_dic]
            new_yt_df = pd.DataFrame(dicts[0]).add(pd.DataFrame(dicts[1]), fill_value=0)
            new_yt_dic = {k: list(new_yt_df[k]) for k in new_yt_df.columns}
        else:
            print('number of year error')
        add_obj = YT(self.name + '+' + another.name, self.n, alpha=self.alpha, beta=self.beta, **new_yt_dic)

        return add_obj

    @staticmethod
    def alpha_check(alpha):
        if alpha >= 1.:
            print('-' * 100 + '\n')
            print(' alpha >=1 \n alpha must be less than 1 \n')
            print('-' * 100 + '\n')
            exit(1)
        else:
            pass

    def stat(self):
        df = pd.DataFrame(self.YT_dic)
        return df.describe()

    def mean(self):
        return {k: np.mean(v) for k, v in zip(self.YT_name, self.YT_table)}

    def var(self, alpha):
        self.alpha_check(alpha)
        return {k: np.percentile(v, q=alpha * 100, interpolation='higher') for k, v in
                zip(self.YT_name, self.YT_table)}

    def xvar(self, alpha):
        self.alpha_check(alpha)
        return {k: np.percentile(v, q=alpha * 100, interpolation='higher') - np.mean(v) for k, v in
                zip(self.YT_name, self.YT_table)}

    def tvar(self, alpha):
        self.alpha_check(alpha)
        return {k: np.mean(np.sort(v)[self.alpha_n:]) for k, v in zip(self.YT_name, self.YT_table)}

    def xtvar(self, alpha):
        self.alpha_check(alpha)
        return {k: np.mean(np.sort(v)[self.alpha_n:]) - np.mean(v) for k, v in
                zip(self.YT_name, self.YT_table)}

    def truntvar(self, alpha, beta):
        self.alpha_check(alpha)
        self.alpha_check(beta)
        self.alpha_n = alpha * self.n
        self.beta_n = beta * self.n
        if self.alpha > self.beta or (self.beta_n - self.alpha_n) < 1:
            print('-' * 100 + '\n')
            print('Alpha must be smaller than beta  or  Between alpha percentile point and beta percentile point, there is no data.')
            print('-' * 100 + '\n')
            exit(1)
        else:
            return {k: np.mean(np.sort(v)[self.alpha_n:self.beta_n]) for k, v in zip(self.YT_name, self.YT_table)}

    def premium(self):
        self.premium_dict = {'empty': [0.] * self.n}
        for k, v in zip(self.YT_name, self.YT_table):
            if '_P' in k:
                self.premium_dict = {k: v}
        return self.premium_dict

    def expense(self):
        self.expense_dict = {'empty': [0.] * self.n}
        for k, v in zip(self.YT_name, self.YT_table):
            if '_E' in k:
                self.expense_dict = {k: v}
        return self.expense_dict

    def noncat(self):
        self.noncat_dict = {'empty': [0.] * self.n}
        for k, v in zip(self.YT_name, self.YT_table):
            if '_nonCAT' in k:
                self.noncat_dict = {k: v}
        return self.noncat_dict

    def all_peril(self):
        global p
        for p in self.peril_list:
            self.all_peril_dict.update({k: v for k, v in zip(self.YT_name, self.YT_table) if p in k})
        return self.all_peril_dict

    def uwg(self):
        P = pd.DataFrame(self.premium().values()[0], columns=['uwg'])
        E = pd.DataFrame(self.expense().values()[0], columns=['uwg'])
        # L1 = pd.DataFrame(list(np.array((self.all_peril().values())).sum(axis=0)), columns='uwg')
        # L2 = pd.DataFrame(self.noncat(), columns='uwg')
        UWG = P - E
        return {'uwg': list(UWG.ix[:, 0])}


# if __name__ == '__main__':
obj1 = YT('SJNK1', 10, _P=[10] * 10, _E=[2] * 10, USWS=range(10), USEQ=range(10))
obj2 = YT('SJNK2', 10, _P=[20] * 10, _E=[4] * 10, USWS=range(10), EUWS=range(10))
print obj1.stat()
print obj2.stat()
obj3 = obj1 + obj2
obj4 = obj1 + obj2 + obj3
print obj3.stat()
print obj4.stat()
