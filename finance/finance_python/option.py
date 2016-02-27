__author__ = 'Maxwell'
from math import log, sqrt, erf, exp


def bcall(f, k, r, t, vol):
    d1 = log(f / k) / (vol * sqrt(t)) + vol * sqrt(t) / 2
    d2 = d1 - vol * sqrt(t)
    n1 = erf(d1 / sqrt(2)) / 2 + 0.5
    n2 = erf(d2 / sqrt(2)) / 2 + 0.5
    bcall = f * exp(-r * t) * n1 - k * exp(-r * t) * n2
    return bcall


class Caplet:
    def __init__(self, f_int, cap, t, vol, d, r, l):
        self.f_int = f_int
        self.cap = cap
        self.t = t
        self.vol = vol
        self.d = d
        self.r = r
        self.l = l

    def calc_d1(self):
        self.d1 = log(self.f_int / self.cap) / (self.vol * sqrt(self.t)) + self.vol * sqrt(self.t) / 2
        return self.d1

    def calc_d2(self):
        self.d2 = self.d1 - self.vol * sqrt(self.t)
        return self.d2

    def calc(self):
        self.n1 = erf(self.d1 / sqrt(2)) / 2 + 0.5
        self.n2 = erf(self.d2 / sqrt(2)) / 2 + 0.5
        self.pv = self.l * self.d * exp(-(self.t + self.d) * self.r) * (self.f_int * self.n1 - self.cap * self.n2)
        return self.pv


a = Caplet(0.07, 0.08, 1, 0.2, 0.25, 0.069395, 10)
print(a.calc_d1())
print(a.calc_d2())
# print(a.pv)
print(a.calc())
