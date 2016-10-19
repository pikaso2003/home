#coding:sjis
"""
ポートフォリオ問題
平均収益最大化・CVaR最小化
 株式会社　オクトーバー・スカイ
2015-10-9
"""
import random
from gurobipy import *

#NumS: シナリオ数
NumS = 1000
#NumG: 銘柄数
NumG = 10
#alpha: 信頼水準
alpha = 0.98
#E[s,g] シナリオsでの銘柄gの収益みたいなもの
E = {(s,g):random.random() for s in xrange(NumS) for g in xrange(NumG)}

model=Model()
"""
変数P[g]: 銘柄gのポートフォリオ
変数X[s]: シナリオsでの収益
変数Y[s]>=0: シナリオsでの損失（VaR以下のものだけが正の数値となる）
変数Ave: 平均収益
変数Dev[s]：シナリオsでの偏差
変数VaR: VaR
変数CVaR: CVaR
"""
P = {g: model.addVar() for g in xrange(NumG)}
X = {s: model.addVar() for s in xrange(NumS)}
Y = {s: model.addVar() for s in xrange(NumS)}
Ave = model.addVar()
Dev = {s: model.addVar(lb=-GRB.INFINITY) for s in xrange(NumS)}
VaR = model.addVar()
CVaR = model.addVar()

model.update()

# ポートフォリオの総和は1
model.addConstr(quicksum(P[g] for g in P) == 1)

for s in xrange(NumS):
    # X[s]とポートフォリオの関係
    model.addConstr(X[s] == quicksum(E[s,g]*P[g] for g in xrange(NumG)))

    # X[s]とAve,Dev[s]の関係
    model.addConstr(X[s] == Ave - Dev[s])

    # 偏差のVaRより大きい部分を損失と考える
    model.addConstr(Dev[s] - VaR <= Y[s])

# 偏差の合計は0
model.addConstr(quicksum(Dev[s] for s in Dev) == 0)

# VaR + (Y[s]のシナリオ数*(1-alpha)個での平均) = CVaRとおいた
model.addConstr(VaR + quicksum(Y[s] for s in Y)/(NumS*(1-alpha)) == CVaR)

#モデルでは，シナリオでの平均収益を最大化して，CVaRを最小化するポートフォリオを作る
model.setObjective(CVaR - Ave,GRB.MINIMIZE)

# 最適化の実行
model.optimize()

# 結果の表示
print "Ave=",Ave.X
print "VaR=",VaR.X
print "CVaR=",CVaR.X
for g in xrange(NumG):
    print "portfolio %d = %f"%(g,P[g].X)
"""
for s in xrange(NumS):
    print "%d,%f"%(s,X[s].X-Ave.X)
"""
