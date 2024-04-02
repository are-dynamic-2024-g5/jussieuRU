import numpy as np
from termcolor import colored
import matplotlib.pyplot as plt

class Client:
    def __init__(self, id, restaurant, patience, budget, pref_lists, waiting=True):
        self.id = id
        self.restaurant = restaurant
        self.patience = patience
        self.budget = budget
        self.pref_lists = pref_lists
        self.waiting = waiting
        self.current_max_appeal = 0

    def appeal_byprice(self, restaurant):
        p = restaurant.avg_price
        b = self.budget
        axs = p-b+.3
        val = (1-2*axs)*np.exp(2*axs)
        return max(0, (val+1)/2 )

    def appeal_byqueue(self, restaurant):
        r = restaurant.rank(self.id)+1
        e = restaurant.eff
        p = self.patience
        return np.exp(-r/e/p)
        #return np.exp(-e/r/p)

    def appeal_bydistance(self, restaurant):
        if self.restaurant:
            return np.exp( -self.restaurant.walking_time[restaurant.id]/2 )
        else:
            return np.exp( -restaurant.walking_time[-1])

    def appeal_byprefs(self, restaurant):
        return self.pref_lists[restaurant.id] * 5

    def appeal(self, restaurant):
        bp = self.appeal_byprice(restaurant)
        bq = self.appeal_byqueue(restaurant)
        bd = self.appeal_bydistance(restaurant)
        bpr= self.appeal_byprefs(restaurant)
        #print(colored(restaurant.avg_price, "green"), colored(bp, "red"), colored(bq, "red"))
        #app = bp * bq * bd * bpr
        app = 6*bp + 4*bq + 1*bd + 1*bpr
        return app

    def bestRestaurant(self, restaurants):
        appeals = [self.appeal(restaurant) for restaurant in restaurants]
        self.current_max_appeal = max(appeals)
        return restaurants[ max(range(len(appeals)), key=appeals.__getitem__) ]

class Restaurant:
    def __init__(self, id, eff, avg_price, walking_time, line):
        self.id = id
        self.eff = eff
        self.avg_price = avg_price
        self.walking_time = list(walking_time)
        self.line = line
        self.served = 0

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

def compute_dists(pos_list, pos):
    return np.round( np.sqrt( np.sum( (pos_list-pos)**2, axis=1)), 3)

def run(crousEff=None, crousPrice=None, max_int_CPM=None, timeSpan=None, random_patience=None, random_budget=None, random_prefs=None, showResults=False):
    # PARAMÈTRES
    if not max_int_CPM:
        max_int_CPM = (300, 2000)
    coefs_CPM = ( max_int_CPM[0]**3 * np.exp(6) / (16* max_int_CPM[1]**2),
                 2* max_int_CPM[1] / (max_int_CPM[0] * np.exp(2)) )
    clientsPerMinute = lambda x: coefs_CPM[0]*x**2*np.exp(-x/coefs_CPM[1])
    if not timeSpan:
        timeSpan = 150

    if not random_patience:
        random_patience = lambda: np.random.random()
    if not random_budget:
        random_budget = lambda: np.random.normal(3, 2)
    if not random_prefs:
        random_prefs = lambda: np.random.normal(0, .05, len(restaurants))

    if not crousEff:
        crousEff = 15
    if not crousPrice:
        crousPrice = 2.61
    # PARAMÈTRES

    restaurants_names = ["CROUS", "five", "crepes"]
    restaurants_pos = [[0, 4], [1 / 2, 0], [-1 / 2, 0]]
    restaurants_pos.append([0, 2.5])
    restaurants_pos = np.array(restaurants_pos) - restaurants_pos[-1]

    A = Restaurant(0, crousEff, crousPrice, compute_dists(restaurants_pos, restaurants_pos[0]), [])  # 56% (stats)
    B = Restaurant(1, 3, 7, compute_dists(restaurants_pos, restaurants_pos[1]), [])
    C = Restaurant(2, 1, 6, compute_dists(restaurants_pos, restaurants_pos[2]), [])
    restaurants = [A, B, C]
    clients = []
    clientsTot = 0
    clientsServed = 0

    # MÉTRIQUES
    M_queues = np.zeros((len(restaurants),timeSpan))
    M_flux = np.zeros((timeSpan))
    M_served = np.zeros((timeSpan))
    M_swaps = np.zeros((len(restaurants), timeSpan))
    # MÉTRIQUES

    for i in range(timeSpan):
        for rest_id in range(len(restaurants)):
            M_queues[rest_id, i] = len( restaurants[rest_id].line )
        M_flux[i] = clientsPerMinute(i)
        clientsTot += M_flux[i]
        M_served[i] = sum(restaurant.served for restaurant in restaurants)

        for j in range(round(clientsPerMinute(i))):
            clients.append(Client(None, None,
                                  random_patience(),
                                  random_budget(),
                                  random_prefs() ))
            if len(clients) < 2:
                clients[-1].id = 0
            else:
                clients[-1].id = clients[-2].id + 1

        if not clients or M_served[i] == max_int_CPM[1]-3:
            continue

        for j in range(clients[-1].id):
            if not clients[j].waiting:
                continue
            bestRest = clients[j].bestRestaurant(restaurants)
            currentRest = clients[j].restaurant
            if currentRest != bestRest:
                if currentRest:
                    M_swaps[bestRest.id, i] += 1
                    currentRest.remove_client(j)
                clients[j].restaurant = bestRest
                bestRest.add_client(j)

        for restaurant in restaurants:
            for j in range(restaurant.eff):
                if not restaurant.line:
                    break
                clients[restaurant.line[0]].waiting = False
                restaurant.remove_client( restaurant.line[0] )
                restaurant.served += 1

    global_satisf = np.mean([client.current_max_appeal for client in clients])

    if showResults:
        print('swaps :', np.sum(M_swaps),
              colored(str(np.sum(M_swaps[0])), "red",   attrs=["dark"]),
              colored(str(np.sum(M_swaps[1])), "green", attrs=["dark"]),
              colored(str(np.sum(M_swaps[2])), "blue", attrs=["dark"]))
        print(colored("crous : ", "red"),   A.served, colored( str(round(A.served/clientsTot*100, 1))+"%\n", attrs=["dark"]) +
              colored("five :  ", "green"), B.served, colored( str(round(B.served/clientsTot*100, 1))+"%\n", attrs=["dark"]) +
              colored("crepes :", "blue"),  C.served, colored( str(round(C.served/clientsTot*100, 1))+"%\n", attrs=["dark"]) + "\n" +
              colored("global satisfaction :", "white"),colored( str(round(global_satisf, 3))+"\n", "white", attrs=["bold"]))

        X_arr = np.arange(0, timeSpan, 1)
        colormap = ["#003049", "#d62828", "#f77f00", "#fcbf49", "#eae2b7"]
        fig, axs = plt.subplots(1, 2, sharey=True)
        axs[0].stackplot(X_arr, [M_served, M_queues[0], M_queues[1], M_queues[2], clientsTot-(M_queues[0]+M_queues[1]+M_queues[2]+M_served)], colors=colormap)
        #axs[0].plot(X_arr, clientsTot-M_flux_P, color="white")
        axs[1].plot(X_arr, M_served, color=colormap[0])
        axs[1].plot(X_arr, M_queues[0], color=colormap[1])
        axs[1].plot(X_arr, M_queues[1], color=colormap[2])
        axs[1].plot(X_arr, M_queues[2], color=colormap[3])
        axs[1].plot(X_arr, clientsTot-(M_queues[0]+M_queues[1]+M_queues[2]+M_served), color=colormap[4])
        axs[1].stackplot(X_arr, np.cumsum(M_swaps, axis=1), colors=colormap[1:3], alpha=0.5)
        fig.legend(['mange/à mangé', 'CROUS', 'FIVE', 'CRÈPES', 'en cours', 'à changé de file'], loc="lower center", ncol=6)

        axs[0].set_aspect(timeSpan/clientsTot/1.5)
        axs[1].set_aspect(timeSpan/clientsTot/1.5)
        fig.tight_layout()
        plt.show()

    return global_satisf