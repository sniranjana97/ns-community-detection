

uid_map = {}

def getUidMap():
    index = 0
    with open('uidlist.txt') as f:
        for line in f:
            uid_map[index] = line.rstrip();
            index+=1

def extract_sub_graph():
    nodes_used = set()
    with open('edges.txt') as f:
        for line in f:
            data = line.rstrip().split(" ")
            nodes_used.add(data[0])
            nodes_used.add(data[1])

    print("Number of nodes: ", len(nodes_used))
    f = open('weibo_network.txt', 'r')
    output = open('sub_graph.txt', 'w+')
    line = f.readline().rstrip()
    data = line.split()
    N = int(data[0])
    print("Total: ", N)
    for i in range(N):
        print("Processing: ", i)
        line = f.readline().rstrip()
        data = line.split()
        user1 = uid_map[int(data[0])]
        k = int(data[1])
        i = 2
        while i < k:
            user2 = uid_map[int(data[i])]
            type = data[i+1]
            if user1 in nodes_used and user2 in nodes_used:
                output.write(user1 + " " + user2+"\n")
                if type == '1':
                    output.write(user2 + " " + user1+"\n")
            i = i+2

if __name__ == "__main__":
    getUidMap()
    extract_sub_graph()
