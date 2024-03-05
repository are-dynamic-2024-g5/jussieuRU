import math
from random import random
from termcolor import colored

class Client:
    def __init__(self, id, restaurant, patience, budget, waiting=True):
        self.id = id
        self.restaurant = restaurant
        self.patience = patience
        self.budget = budget
        self.waiting = waiting

    def appeal_byprice(self, restaurant):
        p = restaurant.avg_price
        b = self.budget
        axs = p-b+.3
        val = (1-2*axs)*math.exp(2*axs)
        return max(0, (val+1)/2 )

    def appeal_byqueue(self, restaurant):
        r = restaurant.rank(self.id)+1
        e = restaurant.eff
        p = self.patience
        return e/r/p

    def appeal(self, restaurant):
        bp = self.appeal_byprice(restaurant)
        bq = self.appeal_byqueue(restaurant)
        #print(colored(restaurant.avg_price, "green"), colored(bp, "red"), colored(bq, "red"))
        return bp * bq

    def bestRestaurant(self, restaurants):
        appeals = [self.appeal(restaurant) for restaurant in restaurants]
        return restaurants[ max(range(len(appeals)), key=appeals.__getitem__) ]

class Restaurant:
    def __init__(self, name, eff, avg_price, line):
        self.name = name
        self.eff = eff
        self.avg_price = avg_price
        self.line = line
        self.tot = 0

    def add_client(self, id):
        self.line.append(id)

    def remove_client(self, id):
        for i in range(len(self.line)):
            if self.line[i] == id:
                return self.line.pop(i)
        return None

    def rank(self, id):
        for i in range(len(self.line)):
            if self.line[i] == id:
                return i
        return len(self.line)

A = Restaurant("CROUS", 10, 3, [])
B = Restaurant("five", 2, 7, [])
C = Restaurant("crepes", 1, 6, [])
restaurants = [A, B, C]
clients = []
clientsPerMinute = 30
clientsTot = 500
timeSpan = 45

for i in range(timeSpan):
    print("t =",i)
    for j in range(clientsPerMinute):
        if not clients or clients[-1].id <= clientsTot:
            clients.append( Client(i*clientsPerMinute+j, None, random(), 10*random()) )

    for j in range(clients[-1].id):
        if not clients[j].waiting:
            continue
        bestRest = clients[j].bestRestaurant(restaurants)
        currentRest = clients[j].restaurant
        if currentRest != bestRest:
            print(colored(restaurants[0].line, "red"))
            print(colored(restaurants[1].line, "green"))
            print(colored(restaurants[2].line, "blue"))

            if currentRest:
                print(f"swap ({j} -> {bestRest.name})")
                currentRest.remove_client(j)
            print("")
            clients[j].restaurant = bestRest
            bestRest.add_client(j)

    for restaurant in restaurants:m
        for j in range(restaurant.eff):
            if not restaurant.line:
                break
            clients[restaurant.line[0]].waiting = False
            restaurant.remove_client( restaurant.line[0] )
            restaurant.tot += 1
#for client in clients:
#    ranks = [len(restaurant.line)-restaurant.rank(client.id) for restaurant in restaurants]
#    print(ranks)
print('')
print(colored("crous : ", "red"),   A.tot, colored( str(round(A.tot/clientsTot*100, 1))+"%\n", attrs=["dark"]) +
      colored("five :  ", "green"), B.tot, colored( str(round(B.tot/clientsTot*100, 1))+"%\n", attrs=["dark"]) +
      colored("crepes :", "blue"),  C.tot, colored( str(round(C.tot/clientsTot*100, 1))+"%\n", attrs=["dark"])  )

