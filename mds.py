from numpy import *
import scipy.linalg
import random
import csv
from datetime import datetime
import json

"""
Dal post:
http://a-ma.us/wp/2012/04/multidimensional-scaling/
"""

def centering_matrix(n):
    """
    Construct an n x n centering matrix
    The form is P = I - (1/n) U where U is a matrix of all ones
    """
    P = eye(n) - 1/float(n) * ones((n,n))
    return P

def metric(x, y):
    """
    Compute the pairwise distance between vector x and y
    """
    d = 2
    summ = []
    i = 0
    while i < len(x):
        # in this case use euclidean distance
        summ.append((x[i] - y[i])**d)
        i = i + 1
    return sum(summ) ** (1 / float(d))

def pairwise_distances(data):
    """
    Calcolo matrice delle distanze,
    a partire dalla matrice delle posizioni dei partiti
    """
    distances = []
    for x in data:
        distances_row = []
        for y in data:
            distances_row.append(metric(x, y)**2)
        distances.append(distances_row)
    return distances


def read_risposte_from_csv(csv_risposte):
    """
    lettura risposte partiti dal csv
    """

    try:
        csv_in = open(csv_risposte, 'rb')
        r_reader = csv.DictReader(csv_in, delimiter=',')
    except IOError:
        print "It was impossible to open file %s" % csv_risposte
        exit(1)

    risposte_partiti = {}
    for row in r_reader:
        partito_id = int(row['partito_id'])
        domanda_id = int(row['domanda_id'])
        risposta = int(row['risposta_int'])
        if not partito_id in risposte_partiti:
            risposte_partiti[partito_id] = {}
        risposte_partiti[partito_id][domanda_id] = risposta

    return risposte_partiti


def get_partiti_posizioni(rps):
    """
    costruisce array partiti e matrice delle posizioni
    p[i] sigla (id) del partito
    posizioni[i][j] posizione (risposta) del partito i sulla domanda j
    """
    partiti = []
    posizioni = []
    for p, rp in rps.items():
        rpk = rp.keys()
        rpk.sort()
        risposte = []
        partiti.append(p)
        for r in rpk:
            risposte.append(rp[r])
        posizioni.append(risposte)
    return (partiti, posizioni)


def normalize_coords(coords):
    """
    Normalize all coords, so that the range of the values are between 0 and 1
    Coordinates, have 3 significative digits.
    """
    # minimax a-la-python
    (max_x, max_y) = map(max, zip(*coords))[1:3]
    (min_x, min_y) = map(min, zip(*coords))[1:3]

    x_range = max_x - min_x
    y_range = max_y - min_y

    norm_coords = map(lambda x: ["%d" % x[0],
                                 "%.3f" % ((x[1]-min_x)/x_range),
                                 "%.3f" % ((x[2]-min_y)/y_range)], coords)
    return norm_coords



def main():

    # legge risposte da file csv
    csv_risposte = 'dump/risposte.csv'
    rps = read_risposte_from_csv(csv_risposte)

    t0 = datetime.now()
    # costruisce array partiti e matrice delle posizioni
    (partiti, posizioni) = get_partiti_posizioni(rps)

    # costruisce matrice delle distanze
    X = pairwise_distances(posizioni)

    P = centering_matrix(len(partiti))
    A = -1/2.0 * P * X * P
    [vals, vectors] = scipy.linalg.eig(A)

    coords = []
    for i, v in enumerate(vals):
        v_coords = [partiti[i],
                   float(vals[1] * vectors[i][1]),
                   float(vals[2] * vectors[i][2])
                  ]
        coords.append(v_coords)

    norm_coords = normalize_coords(coords)

    t1 = datetime.now()

    print json.dumps(norm_coords)
    print t1-t0

main()