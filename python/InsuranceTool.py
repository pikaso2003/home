#
#
#
#
#


import numpy as np


#
#
#
#
class Peril:
    def __init__(self, yp, ylqt, yo):
        self.yp = np.array(yp)  # Premium in year table
        self.ylqt = np.array(ylqt)  # YLQT
        self.yo = np.array(yo)  # Other expenses in year table)
        self.alpha = 0.99  # default = 0.99 (100yr)
        self.var_n = 0  # VaR number
        self.indexer = 0  # event index of each peril's YLQT number after sorted
        if yp.shape[0] != ylqt.shape[0] or ylqt.shape[0] != yo.shape[0]:
            print(' Number of events does not much \n')
            exit(1)

    def get_yp(self):
        return self.yp

    def get_ylqt(self):
        return self.ylqt

    def get_yo(self):
        return self.yo

    def set_yp(self, yp):
        self.yp = yp

    def set_ylqt(self, ylqt):
        self.ylqt = ylqt

    def set_yo(self, yo):
        self.yo = yo

    yp = property(get_yp, set_yp)
    ylqt = property(get_ylqt, set_ylqt)
    yo = property(get_yo, set_yo)

    def uwg(self):
        return self.yp - self.ylqt - self.yo

    def alpha_check(self, alpha):
        if alpha >= 1.:
            print('-' * 100 + '\n')
            print(' alpha >=1 \n alpha must be less than 1 \n')
            print('-' * 100 + '\n')
            exit(1)
        else:
            self.alpha = alpha


class PerilLoss(Peril):
    def __init__(self, ylqt):
        self.ylqt = np.array(ylqt)  # YLQT
        self.temp = np.sort(self.ylqt, axis=0)  # sorted YLQT


    def var(self, alpha):
        self.alpha_check(alpha)
        self.var_n = np.int(np.floor(self.ylqt.shape[0] * alpha))
        return self.temp[self.var_n]

    def tvar(self, alpha):
        self.alpha_check(alpha)
        self.var_n = np.int(np.floor(self.ylqt.shape[0] * alpha))
        return np.mean(self.temp[self.var_n:self.ylqt.shape[0]], axis=0)

    def xtvar(self, alpha):
        self.alpha_check(alpha)
        return self.tvar(alpha) - np.mean(self.ylqt, axis=0)


i = PerilLoss(np.random.random(20).reshape(10, 2))  # instance method
print(i.var(0.75))
print(i.tvar(0.75))
print('-' * 100)
print(i.xtvar(0.75))
print('-' * 100)
print(i.temp)
print('-' * 100)
print(i.ylqt)
