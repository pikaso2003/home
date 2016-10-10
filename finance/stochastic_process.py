import matplotlib.pyplot as plt
import numpy as np
import numpy.random as npr

mklist = ['pink', 'darkviolet', 'slategrey',
          'moccasin', 'olivedrab', 'goldenrod',
          'dodgerblue', 'coral', 'yellowgreen',
          'skyblue', 'crimson']

plt.style.use('ggplot')

# B-S model
S0 = 100
r = 0.05
sigma = 0.25
T = 2.
I = 100000
M = 50
dt = T / M
S = np.zeros((M + 1, I))
S[0] = S0
for t in range(1, M + 1):
    S[t] = S[t - 1] * np.exp((r - 0.5 * sigma ** 2) * dt
                             + sigma * np.sqrt(dt) * npr.standard_normal(I))

x0 = 0.05
kappa = 3.
theta = 0.02
sigma_cir = 0.1


# CIR model
def cir_euler(T, M, I, x0, kappa, theta, sigma_cir):
    dt = T / M
    xh = np.zeros((M + 1, I))
    xh[0] = x0
    for t in range(1, M + 1):
        xh[t] = xh[t - 1] + kappa * (theta - np.maximum(xh[t - 1], 0)) * dt + sigma_cir * np.sqrt(
            np.maximum(xh[t - 1], 0)) * np.sqrt(dt) * npr.standard_normal(I)
    x1 = np.maximum(xh, 0)
    return x1


def cir_exact(T, M, I, x0, kappa, theta, sigma_cir):
    dt = T / M
    xh = np.zeros((M + 1, I))
    xh[0] = x0
    for t in range(1, M + 1):
        df = 4 * theta * kappa / sigma_cir ** 2
        c = sigma_cir ** 2 * (1 - np.exp(-kappa * dt)) / (4 * kappa)
        nc = np.exp(-kappa * dt) / c * xh[t - 1]
        xh[t - 1] = c * npr.noncentral_chisquare(df, nc, size=I)
    return xh


x1 = cir_euler(T, M, I, x0, kappa, theta, sigma_cir)
x2 = cir_exact(T, M, I, x0, kappa, theta, sigma_cir)

# Hegan SV model
s0 = 100.
r = 0.05
v0 = 0.1
kappa = 4.
theta = 0.35
sigma = 0.2
rho = 0.5
T = 1.

I = 10000
corr_mat = np.zeros((2, 2))
corr_mat[0, :] = [1., rho]
corr_mat[1, :] = [rho, 1.]
cho_mat = np.linalg.cholesky(corr_mat)
ran_num = npr.standard_normal((2, M + 1, I))

dt = T / M
v = np.zeros_like(ran_num[0])
vh = np.zeros_like(v)
v[0] = v0
vh[0] = v0
for t in range(1, M + 1):
    ran = np.dot(cho_mat, ran_num[:, t, :])
    vh[t] = (vh[t - 1] + kappa * (theta - np.maximum(vh[t - 1], 0)) * dt + sigma * np.sqrt(
        np.maximum(vh[t - 1], 0)) * np.sqrt(dt) * ran[1])
v = np.maximum(vh, 0.)
s = np.zeros_like(ran_num[0])
s[0] = s0
for t in range(1, M + 1):
    ran = np.dot(cho_mat, ran_num[:, t, :])
    s[t] = s[t - 1] * np.exp((r - 0.5 * v[t]) * dt + np.sqrt(v[t]) * ran[0] * np.sqrt(dt))

fig, ax = plt.subplots(4, 2, figsize=(8, 13))
ax[0, 0].hist(S[-1], bins=50)
ax[0, 0].set_xlabel('index level')
ax[0, 0].set_ylabel('Geometric Brownian Motion')
ax[0, 1].plot(S[:, :10], lw=1.5)
ax[0, 1].set_xlabel('time')
ax[0, 1].set_ylabel('index level')
ax[1, 0].hist(x1[-1], bins=50)
ax[1, 0].set_xlabel('index level')
ax[1, 0].set_ylabel('Euler CIR')
ax[1, 1].plot(x1[:, :10], lw=1.5)
ax[1, 1].set_xlabel('time')
ax[1, 1].set_ylabel('index level')
ax[2, 0].hist(x1[-1], bins=50)
ax[2, 0].set_xlabel('index level')
ax[2, 0].set_ylabel('Exact CIR (noncentral_chi_square)')
ax[2, 1].plot(x1[:, :10], lw=1.5)
ax[2, 1].set_xlabel('time')
ax[2, 1].set_ylabel('index level')
ax[3, 0].hist(s[-1], bins=50)
ax[3, 0].set_xlabel('index level')
ax[3, 0].set_ylabel('Heston Stochastic Volatility')
ax[3, 1].hist(v[-1], bins=50)
ax[3, 1].set_xlabel('volatility level')
ax[3, 1].set_ylabel('volatility')
ax[3, 1].text(theta + 0.1, 400, 'kappa=%.2f\ntheta=%.2f\nsigma=%.2f\nrho=%.2f' % (kappa, theta, sigma, rho), fontsize=8)
plt.grid(True)
plt.suptitle('Stochastic Processes (MC n=10000)', fontsize=15, color=mklist[5])
plt.tight_layout()
plt.savefig('MC_example.png')
plt.show()
