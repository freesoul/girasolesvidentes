# -*- coding: utf-8 -*-
#!usr/bin/env python
#
# Aplicacion del clasificador bayesiano multinomial
# para la categorizacion te textos en funcion de las
# frecuencias de uso de las palabras empleadas
#
# Autor: Jean-Francois Kener
#
# 2017
#

import glob, os
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from collections import Counter
from six.moves import cPickle as pickle

prepareTrainData=False
trainData=False
testData=True
verbose = False
minDesvTipica = 0.25
dataPath = './Data'
testFile = './Test/test.pickle'

def GenerateDataVectors():
    global dataPath, minDesvTipica

    #Load dictionaries of tokens + frequencies
    data = []
    for filename in glob.glob(dataPath+'/*.pickle'):
        data.append( dict(pickle.load(open(filename, "r"))) )

    #Generate dictionary with all words
    common_dict = Counter()
    for dictionary in data:
        common_dict += Counter(dictionary)

    common_dict_len = len(common_dict)

    #Create word labels
    word_labels = [word for word in common_dict]

    #Fill vectors with freqs
    vectors = np.zeros((len(data), common_dict_len))
    for i, some_dict in enumerate(data):
        for word in some_dict:
            vectors[i][word_labels.index(word)] = some_dict[word]


    #Remove too similar data between groups
    #Normalize freqs
    sum_vector = np.sum(vectors, axis=0)
    normalized_vectors = vectors / sum_vector
    vectors = normalized_vectors # better ?

    removewords = []
    desv = np.std(normalized_vectors, axis=0)
    for i, x in enumerate(desv):
        if x < minDesvTipica:
            removewords.append(i)

    vector_labels = [os.path.splitext(os.path.basename(x))[0] for x in glob.glob(dataPath+'/*.pickle')]
    vectors = np.delete(vectors, removewords, 1)
    word_labels = [word for i, word in enumerate(word_labels) if i not in removewords]

    with open('./VECTORS.pickle', 'wb') as f:
        print "Dumping vectors file..."
        pickle.dump((vector_labels, vectors, word_labels),f)

    return vector_labels, vectors, word_labels



def GenerateTestVector():
    global testFile, minDesvTipica

    #Load test file
    with open(testFile, 'r') as f:
        testData = pickle.load(f)

    testVector = np.zeros(len(word_labels))

    for word_tuple in testData:
        if word_tuple[0] in word_labels:
            index = word_labels.index(word_tuple[0])
            testVector[index] = word_tuple[1]

    return testVector



if prepareTrainData:
    print "Preparing data..."
    vector_labels, vectors, word_labels = GenerateDataVectors()
else:
    try:
        with open('./VECTORS.pickle', 'rb') as f:
            vector_labels, vectors, word_labels = pickle.load(f)
    except:
        print "Please, set prepareTrainData to true"




if trainData:
    print "Training..."

    clf = MultinomialNB()
    clf.fit(vectors, vector_labels)
    with open('./MULTINOMIAL.pickle', 'wb') as f:
        pickle.dump(clf, f)
else:
    with open('./MULTINOMIAL.pickle', 'rb') as f:
        clf = pickle.load(f)



if testData:
    print "Generating test vector..."
    testVector = GenerateTestVector()

    print "Predicted:"
    print clf.predict([testVector])[0]
    print clf.classes_
    probs = clf.predict_proba([testVector])[0]
    print probs


