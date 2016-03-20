import numpy as np
from scipy import interpolate
from scipy.optimize import minimize
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from financial_module.SABR import haganLogNormalApprox

mklist = ['deeppink', 'darkviolet', 'slategrey', 'moccasin', 'olivedrab', 'goldenrod',
          'dodgerblue', 'coral', 'yellowgreen', 'skyblue', 'crimson']

# reading csv data
swaption_black_vol = pd.read_csv('swaption_vol.csv')
df = pd.read_csv('Df.csv', header=0)

######################################################################################################################
# market df and cubic spline glaph drawing
fig1, ax1 = plt.subplots(1, 1, figsize=(8, 8))
ax1.plot(df.ix[:, 0].values, df.ix[:, 1].values, '.', ms=6, color=mklist[1])
ax1.set_xlabel('Year')
ax1.set_xlim(0, 55)
ax1.set_ylabel('Discount factor')
ax1.set_title('Market discount factors and Cubic splined one : ref Brigo')

# DF cubic spline yr=[0,30]
cs1 = interpolate.interp1d(df.ix[:, 0].values[:-2], df.ix[:, 1].values[:-2], kind='cubic')
x_yr = np.arange(0, df.ix[:, 0].values[-3], 0.1)
y_df = cs1(x_yr)
ax1.plot(x_yr, y_df, '-', color=mklist[0])

# DF cubic spline yr=[30,50]
cs2 = interpolate.interp1d(df.ix[:, 0].values[40:], df.ix[:, 1].values[40:], kind='quadratic')
xx_yr = np.arange(df.ix[:, 0].values[-3], df.ix[:, 0].values[-1], 0.1)
yy_df = cs2(xx_yr)
ax1.plot(xx_yr, yy_df, '-', color=mklist[6])

plt.grid(True)
plt.show()
######################################################################################################################

yr_1to30 = np.arange(0, 30.5, 0.5)
df_1to30 = cs1(yr_1to30)
yr_30to50 = np.arange(30.5, 50.5, 0.5)
df_30to50 = cs2(yr_30to50)

YR = np.hstack((yr_1to30, yr_30to50))
DF = np.hstack((df_1to30, df_30to50))

fig2, ax2 = plt.subplots(1, 1, figsize=(8, 8))
ax2.plot(YR, DF, '.', ms=4, color=mklist[10])
ax2.set_xlabel('Year')
ax2.set_xlim(0, 55)
ax2.set_ylabel('Discount factor')
ax2.set_title('Discount factor from spline curve')
plt.grid(True)
plt.show()

######################################################################################################################
# swap_rate = (1-v(t,t+N*delta)/( delta * Sigma{v(t,t+i*delta)} )

swaption_black_vol = swaption_black_vol.ix[swaption_black_vol.ix[:, 0] + swaption_black_vol.ix[:, 1] < 60]
Ex_plus_Tenor = swaption_black_vol.ix[:, 0] + swaption_black_vol.ix[:, 1]
ATM = []
for i in range(len(swaption_black_vol)):
	payment = np.arange(swaption_black_vol.ix[i, 0], Ex_plus_Tenor[i] + 0.5, 0.5)
	DF_temp = np.array([DF[YR == j] for j in payment]).flatten()
	DF_forward = DF_temp[1:] / DF_temp[0]
	swap_rate = (1 - DF_forward[-1]) / (0.5 * DF_forward.sum())
	ATM.append(swap_rate)
swaption_df = pd.concat([swaption_black_vol, pd.DataFrame({'ATM': ATM})], axis=1)

# x : array-like [[alpha_1,nu_1,rho_1],[alpha_2,nu_2,rho_2],...[alpha_N,nu_N,rho_N]]
# beta : beta (common coefficient for each expiry and tenor)
delta_K = swaption_df.ix[:, 2:11].columns.astype(np.float).values / 100.


def obj_func1(x, beta, swaption_df, delta_K):
	vol_array = []
	for i in range(len(swaption_df)):
		vol_seq = [haganLogNormalApprox(swaption_df.ix[i, :]['ATM'] * 100 + j, swaption_df.ix[i, :]['Expiry'],
		                                swaption_df.ix[i, :]['ATM'] * 100, x[i, 0], beta, x[i, 1], x[i, 2])
		           for j in delta_K]
		vol_array.append(vol_seq)
	return np.array(vol_array) * 100.


def obj_func2(x, beta, swaption_df, delta_K):
	# x : array-like [[alpha_1,nu_1,rho_1],[alpha_2,nu_2,rho_2],...[alpha_N,nu_N,rho_N]]
	vol_array = []
	for i in range(len(swaption_df)):
		vol_seq = [haganLogNormalApprox(swaption_df.ix[i, :]['ATM'] * 100 + j, swaption_df.ix[i, :]['Expiry'],
		                                swaption_df.ix[i, :]['ATM'] * 100, x[i, 0], beta, x[i, 1], x[i, 2])
		           for j in delta_K]
		vol_array.append(vol_seq)
	ret = np.array(vol_array) * 100. - market_vol.values
	return (ret * ret).sum()


def obj_func3_0(x, beta, swaption_df, delta_K):
	# x : array-like [alpha_1,nu_1,rho_1]
	vol_array = []
	vol_seq = [haganLogNormalApprox(swaption_df.ix[0, :]['ATM'] * 100. + j, swaption_df.ix[0, :]['Expiry'],
	                                swaption_df.ix[0, :]['ATM'] * 100., x[0], beta, x[1], x[2])
	           for j in delta_K]
	vol_array.append(vol_seq)
	ret = np.array(vol_array) * 100. - market_vol.values[0]
	return (ret * ret).sum()


######################################################################################################################
# comparing Market Vol and Hagan approximate Vol

market_vol = swaption_df.ix[:, 2:11]
initial_anr = [0.3, 0.4, 0]
initial_x = np.array(initial_anr * 19).reshape(19, 3)
initial_beta = 0.5
initial_obj_return = obj_func1(initial_x, initial_beta, swaption_df, delta_K)

fig3, ax3 = plt.subplots(5, 4, figsize=(14, 12))
count = 0
for i in ax3:
	for j in i:
		if count == 19:
			break
		else:
			j.plot(delta_K, market_vol.ix[count, :].values, 'o', ms=4, color='purple')
			j.plot(delta_K, initial_obj_return[count], '-', color='deeppink')
			j.set_title('Expiry : %d   Tenor : %d' % (swaption_df.ix[count, 0], swaption_df.ix[count, 1]), fontsize=12)
			j.set_xlim(-2.5, 2.5)
			j.set_ylim(5, 30)
			j.grid(True)
			count += 1

ax3[0, 0].set_xlabel('delta strike to ATM (%)')
ax3[0, 0].set_ylabel('Vol (%)')
ax3[4, 3].text(0.1, 0.4, 'Market Implied Volatility \n vs (Expiry,Tenor) \n\n SABR Beta : %1.2f' % initial_beta,
               fontsize=13)
plt.tight_layout()
plt.show()

######################################################################################################################
######################################################################################################################
# Calibration
# cons =({'type':'ineq','fun'})
# initial_x_opt = np.vstack((initial_x, [0, 0, initial_beta]))
# opt = minimize(obj_func2, initial_x_opt, args=(swaption_df, delta_K), method='SLSQP')

optimized_iter_vol = []


def optimized_x_to_vol(x):
	global optimized_iter_vol
	opt_vol_seq = np.array([haganLogNormalApprox(swaption_df.ix[0, :]['ATM'] * 100. + j, swaption_df.ix[0, :]['Expiry'],
	                                             swaption_df.ix[0, :]['ATM'] * 100., x[0], initial_beta, x[1],
	                                             x[2]) for j in delta_K]) * 100.
	optimized_iter_vol.append(opt_vol_seq)


# initial 0.5, 0.5, 0., initial_beta
opt = minimize(obj_func3_0, initial_anr, args=(initial_beta, swaption_df, delta_K), method='SLSQP',
               bounds=[[0, 1], [0, 1], [-1, 1]], options={'disp': True, 'ftol': 1e-8}, callback=optimized_x_to_vol)


def update_plot(i, ax, optimized_iter_vol):
	ax.clear()
	ax.set_xlim([-2.5, 2.5])
	ax.set_xlabel('delta strike to ATM (%)')
	# ax.set_ylim([15., 30.])
	ax.set_ylabel('Vol (%)')
	ax.plot(delta_K, market_vol.ix[0, :].values, 'o', ms=4, color='purple')
	ax.plot(delta_K, optimized_iter_vol[i], '-', color='deeppink')
	ax.text(1., 26, '%d th iteration  ' % i)
	ax.grid(True)


fig4, ax4 = plt.subplots(1, 1, figsize=(8, 8))
ax4.plot(delta_K, market_vol.ix[0, :].values, 'o', ms=4, color='purple')
ax4.plot(delta_K, initial_obj_return[0], '-', color='deeppink')
ax4.set_xlim([-2.5, 2.5])
ax4.set_xlabel('delta strike to ATM (%)')
# ax4.set_ylim([15., 30.])
ax4.set_ylabel('Vol (%)')
ax4.set_title('SABR Calibration Animation ( Expiry5, Tenor2 ) \n SABR Beta : %1.2f' % initial_beta, fontsize=13)
ax4.grid(True)
plt.tight_layout()
ani = animation.FuncAnimation(fig4, update_plot, fargs=(ax4, optimized_iter_vol), frames=len(optimized_iter_vol))
ani.save('SABR_cal.gif', writer='imagemagick', fps=1)
plt.show()
