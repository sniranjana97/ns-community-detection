

uid_map = {}

def getUidMap():
    index = 0
    with open('uidlist.txt') as f:
        for line in f:
            uid_map[index] = line.rstrip();
            index+=1



if __name__ == "__main__":
    getUidMap()
