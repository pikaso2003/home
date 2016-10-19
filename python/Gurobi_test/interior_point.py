# coding=utf-8
#
#   Comments :
#
#   Arguments :
#
#   Return :
#
# ---------------------------------------------------------------------------------
#   Date        Developer       Action
#   
#   
#
from pylab import *

def affine_scaling(c, A, b, x0, alpha=0.5, eps=10e-4):
    """
        次のような標準形の線形計画問題を解く
        minimize (c^T)*x
        subject to A*x = b
                   x_i >= 0  (i=1,...,n)

    Parameters
    ----------
    c : matrix, shape (n, 1); 決定変数の係数ベクトル
    A : matrix, shape　(m, n); 制約式の係数行列
    b : matrix, shape (m, 1);  制約式の右辺
    x0 : matrix, shape (n, 1); 決定変数の初期値
    alpha : float in (0, 1);
            ステップサイズ（方向ベクトルの重み），デフォルト値:0.5
    eps : float > 0; 収束の精度，デフォルト値:10e-4

    Returns
    -------
    xk : matrix, shape (n, 1); 最適解　"""

    xk = x0

    delta_x = [inf]
    while norm(delta_x) > eps:
        # Xk : 対角成分が xk の各要素で残りは0の行列
        Xk = diagflat(xk.T)

        # 逆行列の計算を避けるため
        # yk = (A*Xk*Xk*A.T).I * (A*Xk*Xk*c) を計算する代わりに
        # (A*Xk*Xk*A.T)*yk = A*Xk*Xk*c を解く
        yk = solve(A * Xk * Xk * A.T, A * Xk * Xk * c)

        zk = c - A.T * yk
        if all(zk == 0):
            break
        delta_x = -(Xk * Xk * zk) / norm(Xk * zk)
        xk = xk + alpha * delta_x

    return xk


if __name__ == '__main__':
    # 問題
    c = matrix([[-400],
                [-300],
                [0],
                [0],
                [0]])
    A = matrix([[60, 40, 1, 0, 0],
                [20, 30, 0, 1, 0],
                [20, 10, 0, 0, 1]])
    b = matrix([[3800],
                [2100],
                [1200]])
    # 初期値
    x1, x2 = 20, 10
    x0 = matrix([[x1],
                 [x2],
                 [b[0, 0] - A[0, 0] * x1 - A[0, 1] * x2],
                 [b[1, 0] - A[1, 0] * x1 - A[1, 1] * x2],
                 [b[2, 0] - A[2, 0] * x1 - A[2, 1] * x2]])

    x_opt = affine_scaling(c, A, b, x0)

    for i, xi in enumerate(x_opt):
        print "x{} : {}".format(i + 1, round(xi))
    print 'Obj :', round(c.T * x_opt)
