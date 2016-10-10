import math

from scipy.stats import norm


def black(F_0, y, expiry, vol, isCall):
    """
    Black formula
    :param F_0: forward rate at time 0
    :param y: strike price
    :param expiry: option expiry
    :param vol: Black implied volatility
    :param isCall: True or False
    :return:
    """

    option_value = 0

    if expiry * vol == 0.:
        if isCall:
            option_value = max(F_0 - y, 0.)
        else:
            option_value = max(y - F_0, 0.)
    else:
        d1 = dPlusBlack(F_0, y, expiry, vol)
        d2 = dMinusBlack(F_0, y, expiry, vol)
        if isCall:
            option_value = F_0 * norm.cdf(d1) - y * norm.cdf(d2)
        else:
            option_value = -F_0 * norm.cdf(-d1) + y * norm.cdf(d2)

    return option_value


def dPlusBlack(F_0, y, expiry, vol):
    """
    d+ term in Black formula
    :param F_0: forward rate at time 0
    :param y: strike price
    :param expiry: option expiry
    :param vol: Black implied volatility
    :return: d+ term
    """
    d_plus = (math.log(F_0 / y) + 0.5 * vol * vol * expiry) / vol / math.sqrt(expiry)
    return d_plus


def dMinusBlack(F_0, y, expiry, vol):
    """
    d- term in Black fromula
    :param F_0: forward rate at time 0
    :param y: strike price
    :param expiry: option expiry
    :param vol: Black implied volatility
    :return: d- term
    """
    d_minus = dPlusBlack(F_0, y, expiry, vol) - vol * math.sqrt(expiry)

    return d_minus
