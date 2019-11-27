import networkx as nx
import urllib
import csv

from networkx.algorithms.community.quality import modularity
from networkx.utils.mapped_queue import MappedQueue

def total_conformity(G, communities):
    group_conf = 0.0
    #groups conformity is defined as sum of comformity of each individual to other individuals in the group
    #conformity of an individual to a group is defined as the number of times the individual agree with other users in the groups
    # divided by total actions of the other users
    for community in communities:
        total_actions=0
        for node in community:
            for edge in G.edges(node, data=True):
                total_actions += edge[2]['total']
        if total_actions==0:
            continue
        for node in community:
            ind_conf=0.0
            for edge in G.edges(node, data=True):
                u, v, data = edge
                if v in community:
                    ind_conf += data['positive'] - data['negative']
            group_conf += ind_conf/total_actions
    return group_conf

def peer_conformity(G, node1, node2):
  peer_conf1 = 0
  peer_conf2 = 0
  for edge in G.edges(node1, data=True):
    u, v, data = edge
    if node2==v:
      peer_conf1 = (data['positive']-data['negative'])/data['total']
      break
  for edge in G.edges(node2, data=True):
    u, v, data = edge
    if node1==v:
      peer_conf2 = (data['positive']-data['negative'])/data['total']
      break
  return max(peer_conf1, peer_conf2)


def greedy_modularity_communities(G, weight=None):

    # Count nodes and edges
    N = len(G.nodes())
    m = sum([d.get('weight', 1) for u, v, d in G.edges(data=True)])

    # Map node labels to contiguous integers
    num_to_id_map = dict((i, v) for i, v in enumerate(G.nodes()))
    id_to_num_map = dict((num_to_id_map[i], i) for i in range(N))

    #print(num_to_id_map)
    # Initialize community and merge lists
    communities = dict((i, frozenset([i])) for i in range(N))
    merges = []

    # Initial conformity
    partition = [[num_to_id_map[x] for x in c] for c in communities.values()]
    q_cnm = total_conformity(G, partition)


    dq_dict = dict(
        (i, dict(
            (j, peer_conformity(G, num_to_id_map[i], num_to_id_map[j]))
            for j in [
                id_to_num_map[u]
                for u in G.neighbors(num_to_id_map[i])]
            if j != i))
        for i in range(N))

    dq_heap = [
        MappedQueue([
            (-dq, i, j)
            for j, dq in dq_dict[i].items()])
        for i in range(N)]


    H = MappedQueue([
        dq_heap[i].h[0]
        for i in range(N)
        if len(dq_heap[i]) > 0])


    # Merge communities until we can't improve modularity
    while len(H) > 1:
        # Find best merge
        # Remove from heap of row maxes
        # Ties will be broken by choosing the pair with lowest min community id
        try:
            dq, i, j = H.pop()
        except IndexError:
            break
        #print("1. Popped " + str(i) + " " + str(j))
        dq = -dq
        # Remove best merge from row i heap
        dq_heap[i].pop()
        # Push new row max onto H
        # if len(dq_heap[i]) > 0:
        #     print("2. Pushed into H " + str(dq_heap[i].h[0]))
        #     H.push(dq_heap[i].h[0])

        # if there is an edge from j to i, remove the corresponding entries
        if i in dq_dict[j].keys():
          d_old = (-dq_dict[j][i], j, i)
          old_max = dq_heap[j].h[0]
          #print("3. Removing from H " + str(old_max))
          H.remove(old_max)
          #print("3.1. Removing from dq_heap["+str(j)+"] "+ str(d_old))
          dq_heap[j].remove(d_old)
          if len(dq_heap[j]) > 0:
            H.push(dq_heap[j].h[0])
          del dq_dict[j][i]
        # Stop when change is non-positive
        # if dq <= 0:
        #     break

        # Perform merge
        #print("4. Merging " + str(i) + " " + str(j)+ " into " + str(j))
        communities[j] = frozenset(communities[i] | communities[j])
        del communities[i]
        merges.append((i, j, dq))
        # New modularity
        q_cnm += dq

        # updating dq for all k which i and j connects to
        i_set = set(dq_dict[i].keys())
        j_set = set(dq_dict[j].keys())
        all_set = (i_set | j_set) - {i, j}
        both_set = i_set & j_set

        # remove old maximum of heap j
        old_j_heap_max = None
        if len(dq_heap[j]) > 0:
          old_j_heap_max = dq_heap[j].h[0]

        for k in all_set:
          if k in both_set:
            # get the old j->k entry
            old_d_jk = (-dq_dict[j][k], j, k)
            old_heap_max = dq_heap[j].h[0]

            # remove the entry from heap[j]
            #print("5. Removing from dq_heap["+str(j)+"] "+ str(old_d_jk))
            dq_heap[j].remove(old_d_jk)
            # update the entry in dq_dict
            dq_dict[j][k] = dq_dict[j][k] + dq_dict[i][k]
            # push the entry to heap[j]
            new_d_jk = (-dq_dict[j][k], j, k)
            #print("6. Pushing to dq_heap["+str(j)+"] "+ str(new_d_jk))
            dq_heap[j].push(new_d_jk)
            # if the new entry is the new max, push it into H
            # remove the entry from H if it was present in H

            # print("7. Removing from H "+ str(old_heap_max))
            # H.remove(old_heap_max)
            # print("8. Pushing to H "+ str(dq_heap[j].h[0]))
            # H.push(dq_heap[j].h[0])

            # get the entry for i->k
            d_old = (-dq_dict[i][k], i, k)
            # remove the entry from H if it was present in H
            # if dq_heap[i].h[0] == d_old:
            #   print("9. Removing from H "+ str(d_old))
            #   H.remove(d_old)
            #print("10. Removing from dq_heap["+str(i)+"] "+ str(d_old))
            dq_heap[i].remove(d_old)
            del dq_dict[i][k]
          elif k in j_set:
            continue
          else:
            if k==j:
              continue
            # k in i_set
            d_old = (-dq_dict[i][k], i, k)
            # remove the entry from H if it was present in H
            # if dq_heap[i].h[0] == d_old:
            #   print("11. Removing from H "+ str(d_old))
            #   H.remove(d_old)
            # remove the entry from heap[j]
            #print("12. Removing from dq_heap["+str(i)+"] "+ str(d_old))
            dq_heap[i].remove(d_old)
            dq_dict[j][k] = dq_dict[i][k]
            del dq_dict[i][k]
            # push the entry to heap[j]
            # if len(dq_heap[j])>0:
            #   old_heap_max = dq_heap[j].h[0]
            #   print("13. Removing from H "+ str(old_heap_max))
            #   H.remove(old_heap_max)

            #print("14. Pushing to dq_heap["+str(j)+"] "+ str((-dq_dict[j][k], j, k)))
            dq_heap[j].push((-dq_dict[j][k], j, k))
            # if the new entry is the new max, push it into H
            # print("15. Pushing to H "+ str(dq_heap[j].h[0]))
            # H.push(dq_heap[j].h[0])

        if len(dq_heap[j]) > 0 and (old_j_heap_max==None or old_j_heap_max!=dq_heap[j].h[0]):
          if old_j_heap_max is not None:
            #print("13. Removing from H "+ str(old_j_heap_max))
            H.remove(old_j_heap_max)
          #print("15. Pushing to H "+ str(dq_heap[j].h[0]))
          H.push(dq_heap[j].h[0])


        # updating dq for all nodes that connect to j and i
        i_set = set(k for k in dq_dict.keys() if i in dq_dict[k].keys())
        j_set = set(k for k in dq_dict.keys() if j in dq_dict[k].keys())
        all_set = (i_set | j_set) - {i, j}
        both_set = i_set & j_set
        for k in all_set:
          if k in both_set:
            if i==k:
              continue
            old_d_kj = (-dq_dict[k][j], k, j)
            old_heap_max = dq_heap[k].h[0]
            #print("16. Removing from dq_heap["+str(k)+"] "+ str(old_d_kj))
            dq_heap[k].remove(old_d_kj)

            old_d_ki =  (-dq_dict[k][i], k, i)
            #print("17. Removing from dq_heap["+str(k)+"] "+ str(old_d_ki))
            dq_heap[k].remove(old_d_ki)

            #print("18. Removing from H "+ str(old_heap_max))
            H.remove(old_heap_max)

            d_new = (-(dq_dict[k][j] + dq_dict[k][i]), k, j)
            dq_dict[k][j] = dq_dict[k][j] + dq_dict[k][i]
            del dq_dict[k][i]

            #print("19. Pushing to dq_heap["+str(k)+"] "+ str(d_new))
            dq_heap[k].push(d_new)
            #print("20. Pushing to H "+ str(dq_heap[k].h[0]))
            H.push(dq_heap[k].h[0])
          elif k in j_set:
            continue
          else:
            if k==j:
              continue
            # k in i_set
            d_old =  (-dq_dict[k][i], k, i)
            old_heap_max = dq_heap[k].h[0]
            #print("21. Removing from dq_heap["+str(k)+"] "+ str(d_old))
            dq_heap[k].remove(d_old)
            #print("22. Removing from H "+ str(old_heap_max))
            H.remove(old_heap_max)

            d_new = (-dq_dict[k][i], k, j)
            dq_dict[k][j] = dq_dict[k][i]
            del dq_dict[k][i]
            #print("23. Pushing to dq_heap["+str(k)+"] "+ str(d_new))
            dq_heap[k].push(d_new)
            #print("24. Pushing to H "+ str(dq_heap[k].h[0]))
            H.push(dq_heap[k].h[0])

        del dq_dict[i]
        dq_heap[i] = MappedQueue()


    communities = [
        frozenset([num_to_id_map[i] for i in c])
        for c in communities.values()]
    return sorted(communities, key=len, reverse=True)


def clustering():
    G = nx.read_edgelist('./edges.txt', create_using=nx.DiGraph, nodetype=int, data=True)

    c = list(greedy_modularity_communities(G))

    with open('c_communities.csv', 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerow(c)
        writeFile.close()
    largest_community = G.subgraph(c[0])
    nx.write_edgelist(largest_community,'largest_community.edgelist',data=False)
    print("Number of nodes: "+ str(nx.number_of_nodes(G)))
    print("Number of edges: "+ str(nx.number_of_edges(G)))
    print(len(c[0]))

if __name__ == "__main__":
    clustering()
