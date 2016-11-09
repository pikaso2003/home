import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.datasets import make_moons

mklist = ['pink', 'darkviolet', 'slategrey',
          'dodgerblue', 'olivedrab', 'goldenrod',
          'moccasin', 'coral', 'yellowgreen',
          'skyblue', 'crimson']

os.chdir('C:\Users\Maxwell\Desktop\pycwd\Intro_ML')
plt.style.use('ggplot')

# 0_5
# ID,LIMIT_BAL,SEX,EDUCATION,MARRIAGE,AGE,
# 6_11
# PAY_0,PAY_2,PAY_3,PAY_4,PAY_5,PAY_6,
# 12_17
# BILL_AMT1,BILL_AMT2,BILL_AMT3,BILL_AMT4,BILL_AMT5,BILL_AMT6,
# 18_23
# PAY_AMT1,PAY_AMT2,PAY_AMT3,PAY_AMT4,PAY_AMT5,PAY_AMT6,
# 24
# default payment next month

data = pd.read_csv('Credit_default.csv', header=0)
bill = data.ix[:, 12:18].sum(axis=1)
pay = data.ix[:, 18:24].sum(axis=1)
pay_ratio = pay / bill
pay_ratio = pay_ratio.fillna(0)
pay_ratio[bill <= 0] = 0
pay_ratio.name = 'pay_ratio'
feature = pd.concat((data.ix[:, 0:12], pay_ratio), axis=1)

threshold = 0.2
seed = np.random.random(len(data))
x_train = feature.ix[seed > 0.8, 1:]
x_test = feature.ix[seed <= 0.8, 1:]
y_train = data.ix[seed > 0.8, -1]
y_test = data.ix[seed <= 0.8, -1]


def rf_tuning(n_estimators=10, max_features=5, max_depth=3):
    # function: (int, int, int) -> RandomForestObject
    rf = RandomForestClassifier(n_estimators=n_estimators,
                                criterion='gini',
                                max_depth=max_depth,
                                min_samples_split=2,
                                min_samples_leaf=1,
                                max_features=max_features,
                                random_state=2,
                                n_jobs=3)
    return rf


def gbm_tuning(learning_rate=0.1, n_estimators=100, max_depth=3):
    # function: (int, int, int) -> RandomForestObject
    gbm = GradientBoostingClassifier(loss='deviance',
                                     learning_rate=learning_rate,
                                     n_estimators=n_estimators,
                                     subsample=1.,
                                     min_samples_split=2,
                                     min_samples_leaf=1,
                                     min_weight_fraction_leaf=0.,
                                     max_depth=max_depth,
                                     init=None,
                                     random_state=0
                                     )
    return gbm


# RF
for n in [10, 100, 250, 500, 1000, 5000]:
    rf_tune = rf_tuning(n_estimators=n)
    rf_tune.fit(X=x_train, y=y_train)
    print '-' * 20 + '\n' + 'RF tuning %d' % n
    print 'Train acc : %.4f' % (rf_tune.score(x_train, y_train))
    print 'Test acc : %.4f' % rf_tune.score(x_test, y_test)

print 'Random Forest'
rf = rf_tuning(n_estimators=5000)
rf.fit(X=x_train, y=y_train)
print 'RF Train acc : %.4f' % rf.score(x_train, y_train)
print 'RF Test acc : %.4f' % rf.score(x_test, y_test)
rf_importances = rf.feature_importances_

# GBM
for n in [10, 100, 250, 500, 1000, 5000]:
    gbm_tune = gbm_tuning(n_estimators=n)
    gbm_tune.fit(X=x_train, y=y_train)
    print '-' * 20 + '\n' + 'GBM tuning %d' % n
    print 'Train acc : %.4f' % (gbm_tune.score(x_train, y_train))
    print 'Test acc : %.4f' % gbm_tune.score(x_test, y_test)

for depth in [1, 2, 3, 4, 5]:
    gbm_tune = gbm_tuning(max_depth=depth)
    gbm_tune.fit(X=x_train, y=y_train)
    print '-' * 20 + '\n' + 'GBM tuning %d' % depth
    print 'Train acc : %.4f' % (gbm_tune.score(x_train, y_train))
    print 'Test acc : %.4f' % gbm_tune.score(x_test, y_test)

lr_acc = []
for learning_rate in np.arange(0.01, 0.2, 0.01):
    gbm_tune = gbm_tuning(learning_rate=learning_rate)
    gbm_tune.fit(X=x_train, y=y_train)
    print '-' * 20 + '\n' + 'GBM tuning %d' % learning_rate
    print 'Train acc : %.4f' % (gbm_tune.score(x_train, y_train))
    print 'Test acc : %.4f' % gbm_tune.score(x_test, y_test)
    lr_acc.append((round(learning_rate, 2), gbm_tune.score(x_test, y_test)))

print 'Gradient Boosting Machine'
gbm = gbm_tuning(learning_rate=0.03, n_estimators=100, max_depth=2)
gbm.fit(X=x_train, y=y_train)
print 'GBM Train acc : %.4f' % gbm.score(x_train, y_train)
print 'GBM Test acc : %.4f' % gbm.score(x_test, y_test)
gbm_importances = gbm.feature_importances_

fig, ax = plt.subplots(3, 1, figsize=(12, 8))
ax[0].hist(pay_ratio, bins=np.arange(0, 5, 0.01), color=mklist[1])
ax[0].set_xlim(0, 5)
ax[0].set_ylabel('Frequency')
ax[0].set_title('pay_ratio', size=8)
ax[1].bar(range(len(rf_importances)), rf_importances, width=0.35, align='center')
ax[1].set_xticks(range(len(rf_importances)))
ax[1].set_xticklabels(feature.columns[1:], size=6)
ax[1].set_ylim(0, 0.5)
ax[1].set_ylabel('Importance')
ax[1].set_title('Random Forest')
ax[2].bar(range(len(gbm_importances)), gbm_importances, width=0.35, align='center', color=mklist[4])
ax[2].set_xticks(range(len(gbm_importances)))
ax[2].set_xticklabels(feature.columns[1:], size=6)
ax[2].set_ylim(0, 0.5)
ax[2].set_ylabel('Importance')
ax[2].set_title('Gradient Boosting Machine')
plt.tight_layout()
plt.show()
fig.savefig('default_analysis.png')
