from heapq import *
from graphtools import adjacent

def mk_part(adj,p1,p2,node):
    """make a partition of nodes from a graph, for the differencing_construct"""
    p1.append(node)
    for j in adj[node]:
        adj[j].remove(node)
        mk_part(adj,p2,p1,j)
    return p1,p2

def differencing_construct(data):
    """partition a list of items with the differencing method -- case of two partitions"""
    
    # create heap with data and their indices
    # as we want decreasing order, we set -data[] as the key
    n = len(data)
    label = []
    for i in range(n):
        heappush(label, (-data[i],i))   # added tuples have a -datum and its index in 'data'

    # differencing method: create graph with labels updated with differences
    edges = []
    while len(label) > 1:
        d1,i1 = heappop(label)
        d2,i2 = heappop(label)

        # calculate differences between two largest elements
        # update the label of the largest with the difference
        heappush(label, (d1-d2, i1))
        edges.append((i1,i2))   # edge will force the two items in different partitions
        
    # last element of the heap has the difference between the two partitions (i.e., the objective)
    obj,_ = heappop(label)
    obj = -obj

    # print "edges:", edges

    # create the partitions by going through the graph created
    nodes = range(n)
    adj = adjacent(nodes,edges)
    p1, p2 = mk_part(adj,[],[],0)

    # make a list with the weights for each partition
    d1 = [data[i] for i in p1]
    d2 = [data[i] for i in p2]
    # print "p1 indices:", p1, "weights:", d1, sum(d1)
    # print "p2 indices:", p2, "weights:", d2, sum(d2)
    # print "objective:", obj
    return obj, d1, d2


def longest_processing_time(data_,m):
    """separate 'data' into 'm' partitions with longest_processing_time method"""

    # copy and sort data by decreasing order
    data = list(data_)
    data.sort()
    data.reverse()
    
    part = [[] for i in range(m)]       # initialize partition with empty lists
    weight = []                         # heap with weights on each partition
    for p in range(m):
        heappush(weight, (0,p))

    # for each item, add it to the partition with least weight
    for item in data:
        w,p = heappop(weight)
        part[p].append(item)
        w += item
        heappush(weight, (w,p))

    # for p in part:
    #     print p, sum(p)
    return part
        

def multi_differencing_construct(data, m):
    """partition a list of items with the differencing method for more than two partitions"""
    
    n = len(data)
    
    # create a heap to hold tuples with the information required by the algorithm
    # each 3-tuple has (a,b,c) where
    #   a -- label
    #   b -- list of the lists of items on each partition
    #   c -- sum of the weights on each partition (for ordering them)
    # eg: heap = [(-4, [[10], [8, 5], [14]], [10, 13, 14]), (-1, [[], [], [1]], [0, 0, 1]), ...]
    print "log of the execution with multi_differencing_construct:"
    heap = []
    for i in range(n):
        datum = data[i]
        part = [[] for p in range(m)]   # initially, all partitions are empty 
        sums = [0 for p in range(m)]
        part[-1].append(datum)  # insert one item on the last partition
        sums[-1] = datum        # update the sum of weights for last partition
        label = -datum  # as the heap is in increasing order
        heappush(heap, (label, part, sums))
    print "initial heap:", heap

    print
    # differencing method
    while len(heap) > 1:
        # join two elements with largest weights in the heap
        label1,part1,sums1 = heappop(heap)
        label2,part2,sums2 = heappop(heap)

        print "poped element 1", label1,part1,sums1
        print "poped element 2", label2,part2,sums2

        # on each element sort the sets of items by the
        # corresponding sum
        tmp = []
        for p in range(m):
            part = part1[p] + part2[-1-p]       # join the lists of items by reverse order
            sums = sums1[p] + sums2[-1-p]       # update the sum of weights in each list
            tmp.append((sums, part))
        tmp.sort()      # sort by increasing order of weights
        print "created new element:", tmp
        sums = [i for (i,_) in tmp]     # extract the sum of item's weights
        part = [p for (_,p) in tmp]     # extract the lists of items
            
        label = sums[0] - sums[-1]      # the new label is the different between the farthest sums of weights
        heappush(heap,(label, part, sums))
        print "current heap:", heap
        print

    # last element of the heap has the two partitions, the sums
    # difference between the two partitions (i.e., the objective)
    obj,part,sums = heappop(heap)
    obj = -obj
    print "objective:", obj
    print "partitions:", part
    print "sum of weights for each partition:", sums
    return obj,part,sums





    

if __name__ == '__main__':
    """Heuristics for the Number Partitioning Problem: sample usage."""
    
    data = [1, 2, 5, 8, 10, 14]
    n = len(data)
    print "initial data:", data

    print "\ndifferencing_construct: case of two partitions"""
    obj, p1, p2 = differencing_construct(data)

    print "\nlongest processing time heuristic"""
    part = longest_processing_time(data,2)

    print "\ndifferencing_construct: multi partition"""
    print "\nresults for two partitions"""
    obj,part,sums = multi_differencing_construct(data,2)
    print "\nresults for three partitions"""
    obj,part,sums = multi_differencing_construct(data,3)
    
    
    
