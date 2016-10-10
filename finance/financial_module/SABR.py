import math


def haganLogNormalApprox(K, expiry, F_0, alpha_0, beta, nu, rho):
    """
    12 Mar 2016 : Y.H
   Function which returns the Black implied volatility,
   conputed using the Hagan et al. lognormal approximation.
   ( This formula can be utilized for both cap and swaption )
   :param K:option strike
   :param expiry:option expiry
   :param F_0:forward rate (e.g. forward interest rate, forward swaption rate)
   :param alpha_0:SABR alpha at t=0
   :param beta: SABR beta
   :param nu: SABR Nu
   :param rho: SABR Rho
   :return: Black implied volatility
   """
    one_beta = 1. - beta
    one_betasqr = one_beta * one_beta
    # ATM or not
    if F_0 != K:
        fK = F_0 * K
        fK_beta = math.pow(fK, one_beta / 2.)
        log_fK = math.log(F_0 / K)
        z = nu / alpha_0 * fK_beta * log_fK
        x = math.log((math.sqrt(1. - 2. * rho * z + z * z) + z - rho) / (1 - rho))
        sigma_l = alpha_0 / fK_beta / (1. +
                                       one_betasqr / 24. * log_fK * log_fK +
                                       math.pow(one_beta * log_fK, 4) / 1920.) * (z / x)
        sigma_exp = one_betasqr / 24. * alpha_0 * alpha_0 / fK_beta / fK_beta + \
                    0.25 * rho * beta * nu * alpha_0 / fK_beta + (2. - 3. * rho * rho) / 24. * nu * nu
        sigma = sigma_l * (1. + sigma_exp * expiry)
    else:
        f_beta = math.pow(F_0, one_beta)
        f_two_beta = math.pow(F_0, (2. - 2. * beta))
        sigma = alpha_0 / f_beta * (1. +
                                    ((one_betasqr / 24.) * (alpha_0 * alpha_0 / f_two_beta) +
                                     (0.25 * rho * beta * nu * alpha_0 / f_beta) +
                                     (2. - 3. * rho * rho) / 24. * nu * nu) * expiry)
    return sigma
