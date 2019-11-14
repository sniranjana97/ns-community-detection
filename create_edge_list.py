# have a two level dict p1 -> p2 -> conformity score
# the object signifies the conformity of p2 to p1

# Try to find community over a particular tweet ID

import numpy as np
import os

conformity = {}
users = set()

class Interaction:
    def __init__(self):
        self.positive=0
        self.negative=0

    def incrementPositive(self):
        self.positive = self.positive+1

    def incrementNegative(self):
        self.negative = self.negative+1

    def print(self):
        print("Positive = " + str(self.positive))
        print("Negative = " + str(self.negative))

# https://github.com/ZwEin27/Community-Detection/blob/master/communities.py

def create_edge_list():
    interactions = {}
    total = {}

    print("Calculating interactions...")
    for r, d, f in os.walk('./output/'):
        for file in f:
            if '.txt' in file:
                with open('./output/' + file, 'r') as f:
                    for line in f:
                        data = line.split(' ')
                        p1 = data[1]
                        p2 = data[2]

                        if p1 in total:
                            total[p1]+=1
                        else:
                            total[p1] = 1
                        if p2 in total:
                            total[p2]+=1
                        else:
                            total[p2] = 1

                        positive = float(data[3]) > 0
                        if p1 in interactions:
                            if p2 in interactions[p1]:
                                obj = interactions[p1][p2]
                            else:
                                obj = Interaction()
                            if positive:
                                obj.incrementPositive()
                            else:
                                obj.incrementNegative()
                            interactions[p1][p2] = obj
                        else:
                            obj = Interaction()
                            if positive:
                                obj.incrementPositive()
                            else:
                                obj.incrementNegative()
                            interactions[p1] = {}
                            interactions[p1][p2] = obj



    print("Writing edge list...")
    with open('./edges.txt', 'w') as f:
        for p1, value in interactions.items():
            for p2,interaction in value.items():
                #Total number of actions is calculated as total tweets plus total retweets
                values = {'positive': interaction.positive, 'negative': interaction.negative, 'total': total[p2]}
                f.write(p2 + " " + p1 + " " + str(values) +"\n")


if __name__ == "__main__":
  create_edge_list()
