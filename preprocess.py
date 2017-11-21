# -*- coding: utf-8 -*-
#!usr/bin/env python

#
# Procesa textos de cualquier tipo para crear un diccionario con las
# raices de las palabras encontradas y la frecuencia de aparicion
#
# Se elimina todo lo que no sean palabras con un minimo de longitud,
# asi como palabras que no aportan lexico (stopwords)
#
# Autor: Jean-Francois Kener
#
# 2017
#

from six.moves import cPickle as pickle
import os, glob, re
from xml.sax.saxutils import unescape # remove &...;
from collections import defaultdict

verbose = True
dataPath = './Data'
stopwordsFile = './External/spanish_stopwords.txt'
minWordLen = 3

generateTrainData = False
generateTestData = True
testInput = './Test/test.txt'
testOutput = './Test/test.pickle'

def CleanText(texto):
    #Limpiar HTML
    re_clean_html = re.compile('<.*?>')
    output = re.sub(re_clean_html, ' ', texto)
    output = unescape(output) # remove &...;

    #Sustituir todo lo que no sea una letra por un espacio
    output = re.sub(r'[^a-zA-ZÁÉÍÓÚáéíóúñç]',' ', output)

    #Sustituir varios espacios seguidos por un solo espacio
    output = re.sub(r'[\ ]{2,}', ' ', output)

    #Pasar todo a minúsculas y eliminar acentos
    output = output.lower()
    #eliminar acentos pendiente
    acentos = {'á':'a', 'é':'e', 'í':'i','ó':'o','ú':'u'}
    for key in acentos:
        output = output.replace(key, acentos[key])

    return output

def Lemmatizador(tokens):
    global minWordLen
    output = []
    for palabra in tokens:
        corregida = palabra

        regla1 = r'((i[eé]ndo|[aá]ndo|[aáeéií]r|[^u]yendo)(sel[ao]s?|l[aeo]s?|nos|se|me))'
        step1 = re.search(regla1, corregida)
        if step1:
            if (len(palabra)-len(step1.group(1))) >= minWordLen:
                corregida = corregida[:-len(step1.group(1))]
            elif (len(palabra)-len(step1.group(3))) >= minWordLen:
                corregida = corregida[:-len(step1.group(3))]

        regla2 = {
          '(anzas?|ic[oa]s?|ismos?|[ai]bles?|istas?|os[oa]s?|[ai]mientos?)$' : '',
          '((ic)?(adora?|ación|ador[ae]s|aciones|antes?|ancias?))$' : '',
          '(log[íi]as?)$' : 'log',
          '(ución|uciones)$' : 'u',
          '(encias?)$' : 'ente',
          '((os|ic|ad|(at)?iv)amente)$' : '',
          '(amente)$' : '',
          '((ante|[ai]ble)?mente)$' : '',
          '((abil|ic|iv)?idad(es)?)$' : '',
          '((at)?iv[ao]s?)$' : '',
          '(ad[ao])$' : '',
          '(ando)$' : '',
          '(aci[óo]n)$' : '',
          '(es)$' : ''
        }
        for key in regla2:
            tmp = re.sub(key, regla2[key], corregida)
            if tmp!=corregida and len(tmp)>=minWordLen:
                corregida = tmp

        regla3 = {
        '(y[ae]n?|yeron|yendo|y[oó]|y[ae]s|yais|yamos)$',
        '(en|es|éis|emos)$',
        '(([aei]ría|ié(ra|se))mos)$',
        '(([aei]re|á[br]a|áse)mos)$',
        '([aei]ría[ns]|[aei]réis|ie((ra|se)[ns]|ron|ndo)|a[br]ais|aseis|íamos)$',
        '([aei](rá[ns]|ría)|a[bdr]as|id[ao]s|íais|([ai]m|ad)os|ie(se|ra)|[ai]ste|aban|ar[ao]n|ase[ns]|ando)$',
        '([aei]r[áé]|a[bdr]a|[ai]d[ao]|ía[ns]|áis|ase)$',
        '(í[as]|[aei]d|a[ns]|ió|[aei]r)$',
        '(os|a|o|á|í|ó)$',
        '(u?é|u?e)$',
        '(ual)$',
        '([áa]tic[oa]?)$'
        }
        for pattern in regla3:
            tmp = re.sub(pattern, '', corregida)
            if tmp!=corregida and len(tmp)>=minWordLen:
                corregida = tmp

        output.append(corregida)
    return output

def GetCorpusFromFolder(folder):
    text = ""
    for filename in glob.glob(folder+'/*.txt'):
        text = text + open(filename, "r").read() + " "
    return text


# Preprocess all corpus
def PreprocessAllCorpus():
    global dataPath, verbose, stopwordsFile, minWordLen

    #Load corpus
    dataFolders = list(os.walk(dataPath))[1:]
    labels = [os.path.basename(os.path.normpath(x[0])) for x in dataFolders]

    #Load stopwords
    with open(stopwordsFile, 'r') as f:
        stopwords = set(f.read().splitlines())


    #Clean corpus, tokenize, remove stopwords and lemmatize, and create freq dictionary
    total_n_tokens = 0
    total_n_tokens_unique = 0

    for i, folder in enumerate(dataFolders):
        corpus = GetCorpusFromFolder(folder[0])
        tokens = CleanText(corpus).split(' ')
        tokens = [word for word in tokens if word not in stopwords]
        tokens = Lemmatizador(tokens)
        tokens = [token for token in tokens if len(token) >= minWordLen]

        #Get number of tokens
        n_tokens = len(tokens)
        n_tokens_unique = len(set(tokens))
        total_n_tokens += n_tokens
        total_n_tokens_unique += n_tokens_unique

        #Obtain sorted dictionary with frequencies
        fq= defaultdict( float )
        for w in tokens:
            fq[w] += 1
        oc_dictionary = sorted(fq.items(), key=lambda item: item[1], reverse=True)
        freq_dictionary = [(word, freq/n_tokens) for (word, freq) in oc_dictionary]

        with open(dataPath+'/'+labels[i]+".pickle", "wb") as f:
            pickle.dump(freq_dictionary, f)

        if verbose:
            print "Corpus " + labels[i] + "\t(" + str(n_tokens) + " tokens, "+str(n_tokens_unique)+" únicos)"





#PreprocessTestCorpus
def PreprocessTestCorpus():
    global verbose, stopwordsFile, minWordLen
    global testInput, testOutput

    #Load stopwords
    with open(stopwordsFile, 'r') as f:
        stopwords = set(f.read().splitlines())

    #Start processing
    corpus = open(testInput, 'r').read()
    tokens = CleanText(corpus).split(' ')
    tokens = [word for word in tokens if word not in stopwords]
    tokens = Lemmatizador(tokens)
    tokens = [token for token in tokens if len(token) >= minWordLen]

    #Get number of tokens
    n_tokens = len(tokens)
    n_tokens_unique = len(set(tokens))

    #Obtain sorted dictionary with frequencies
    fq= defaultdict( float )
    for w in tokens:
        fq[w] += 1
    oc_dictionary = sorted(fq.items(), key=lambda item: item[1], reverse=True)
    freq_dictionary = [(word, freq) for (word, freq) in oc_dictionary] # freq/n_tokens

    with open(testOutput, "wb") as f:
        pickle.dump(freq_dictionary, f)

    if verbose:
        print "Test generated (" + str(n_tokens) + " tokens, "+str(n_tokens_unique)+" únicos)"



if generateTrainData:
    PreprocessAllCorpus()
if generateTestData:
    PreprocessTestCorpus()
