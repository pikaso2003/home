"""
tsp_gui.py: Simple GUI for the TSP solver

Copyright (c) by Joao Pedro PEDROSO and Mikio KUBO, 2008
"""
from tsp import mk_matrix, distL2, randtour, length, nearest_neighbor, read_tsplib
from tsp import localsearch, multistart_localsearch
# from tsp_simple import localsearch, multistart_localsearch
import random
random.seed(1)
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        # create a graph with several cities' coordinates
        coord = [(4,0),(5,6),(8,3),(4,4),(4,1),(4,10),(4,7),(6,8),(8,1)]
        n, D = mk_matrix(coord, distL2) # create the distance matrix
        instance = "toy problem"
    else:
        instance = sys.argv[1]
        n, coord, D = read_tsplib(instance)     # create the distance matrix

    import networkx as NX
    import matplotlib.pyplot as P
    P.ion()
    G = NX.Graph()
    P.title(instance)
    G.add_nodes_from(range(n))
    position = {}
    for i in range(n):
        position[i]=tuple(coord[i])
    P.draw()                         # redraw the canvas
    NX.draw(G,position)
    raw_input("Press enter to continue")

    def update_graph(z,t,title=None):
        """function to call for updating the graphic output"""
        P.clf()                         # clear the canvas
        G.clear()
        if title == None:
            P.title("tour length=%s" % z)
        else:
            P.title(title + " (length=%s)" % z)
        for i in range(len(t)):
            G.add_edge(t[i], t[i-1])
        P.draw()
        NX.draw(G,position)
        raw_input("Press enter to continue")
        return 

    # random construction
    t = randtour(n)     # create a random tour
    z = length(t,D)     # calculate its length
    update_graph(z,t,"random solution")
    print "random:", t, z, '  -->  ',
    z = localsearch(t,z,D)      # local search starting from the random tour
    print t, z
    update_graph(z,t,"random solution, after local search")

    # greedy construction
    # [try cycle for more possibilities] for i in range(n):
    i = 0
    t = nearest_neighbor(n,i,D) # create a greedy tour, visiting city 'i' first
    z = length(t,D)
    update_graph(z,t,"nearest_neighbor, starting on city %d" % i)
    print "nneigh:", t, z, '  -->  ',
    z = localsearch(t,z,D)
    print t, z
    update_graph(z,t,"nearest_neighbor, starting on city %d (after local search)" % i)

    # multi-start local search
    print "random start local search:"
    niter = 1000
    t,z = multistart_localsearch(niter,n,D,update_graph)
    print "best found solution on %d multistart_localsearch:" % niter
    print t
    print "z=",z
    update_graph(z,t,"best found solution on %d multistart_localsearch:" % niter)
    raw_input("[press enter for exiting]")
