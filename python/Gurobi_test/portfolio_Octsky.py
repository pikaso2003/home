#coding:sjis
"""
�|�[�g�t�H���I���
���ώ��v�ő剻�ECVaR�ŏ���
 ������Ё@�I�N�g�[�o�[�E�X�J�C
2015-10-9
"""
import random
from gurobipy import *

#NumS: �V�i���I��
NumS = 1000
#NumG: ������
NumG = 10
#alpha: �M������
alpha = 0.98
#E[s,g] �V�i���Is�ł̖���g�̎��v�݂����Ȃ���
E = {(s,g):random.random() for s in xrange(NumS) for g in xrange(NumG)}

model=Model()
"""
�ϐ�P[g]: ����g�̃|�[�g�t�H���I
�ϐ�X[s]: �V�i���Is�ł̎��v
�ϐ�Y[s]>=0: �V�i���Is�ł̑����iVaR�ȉ��̂��̂��������̐��l�ƂȂ�j
�ϐ�Ave: ���ώ��v
�ϐ�Dev[s]�F�V�i���Is�ł̕΍�
�ϐ�VaR: VaR
�ϐ�CVaR: CVaR
"""
P = {g: model.addVar() for g in xrange(NumG)}
X = {s: model.addVar() for s in xrange(NumS)}
Y = {s: model.addVar() for s in xrange(NumS)}
Ave = model.addVar()
Dev = {s: model.addVar(lb=-GRB.INFINITY) for s in xrange(NumS)}
VaR = model.addVar()
CVaR = model.addVar()

model.update()

# �|�[�g�t�H���I�̑��a��1
model.addConstr(quicksum(P[g] for g in P) == 1)

for s in xrange(NumS):
    # X[s]�ƃ|�[�g�t�H���I�̊֌W
    model.addConstr(X[s] == quicksum(E[s,g]*P[g] for g in xrange(NumG)))

    # X[s]��Ave,Dev[s]�̊֌W
    model.addConstr(X[s] == Ave - Dev[s])

    # �΍���VaR���傫�������𑹎��ƍl����
    model.addConstr(Dev[s] - VaR <= Y[s])

# �΍��̍��v��0
model.addConstr(quicksum(Dev[s] for s in Dev) == 0)

# VaR + (Y[s]�̃V�i���I��*(1-alpha)�ł̕���) = CVaR�Ƃ�����
model.addConstr(VaR + quicksum(Y[s] for s in Y)/(NumS*(1-alpha)) == CVaR)

#���f���ł́C�V�i���I�ł̕��ώ��v���ő剻���āCCVaR���ŏ�������|�[�g�t�H���I�����
model.setObjective(CVaR - Ave,GRB.MINIMIZE)

# �œK���̎��s
model.optimize()

# ���ʂ̕\��
print "Ave=",Ave.X
print "VaR=",VaR.X
print "CVaR=",CVaR.X
for g in xrange(NumG):
    print "portfolio %d = %f"%(g,P[g].X)
"""
for s in xrange(NumS):
    print "%d,%f"%(s,X[s].X-Ave.X)
"""
