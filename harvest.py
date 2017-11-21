# -*- coding: utf-8 -*-
#!usr/bin/env python

##
## Un programa que hace búsquedas aleatorias con las palabras indicadas en google
## y convierte a texto: información princpal de las páginas encontradas,
## los pdfs pasados a texto, o, en su caso, los RSS sanitizados.
## Todo el output se guarda en un archivo
##
## Autor: Jean-Francois Kener
##
## 2017
##

from google import search
import random
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
import urllib
import re
from goose import Goose
from bs4 import BeautifulSoup as bs
import feedparser
import unicodedata
from xml.sax.saxutils import unescape # remove &...;
import sys

outputFolder='./CorpusGenerados/'
verbose = True

#GOOGLE
num_keywords_per_search = 3
num_searches = 8
num_links_per_search = 10
search_delay = 1.5

#SOURCE PARAMS
max_pdf_bytes_per_source = 5000000 # 5mb
min_bytes_per_source = 350 # 0.35kb
max_bytes_per_source = 75000 # 75kb

#KEYWORDS

semillas = {
    'salud' : {'biología', 'anatomía', 'cromosoma', 'ribosomas', 'histona',
    '\"evolución de las especies\"', '\"gregor mendel\"', 'medicina', 'patologías',
    'bacterias', 'microorganismos', 'inflamación', '\"respuesta inmunitaria\"',
    'citología', '\"regulación homeostática\"', 'circadiano', 'biosfera'},

    'ingeniería' : {'\"álgebra abstracta\"', '\"teoría de números\"', '\"ecuación diofántica\"',
    '\"proceso industrial\"', 'ingeniería', 'software', '\"fabricación industrial\"',
    'electromagnetico', 'aeroespacial', 'física', '\"Revolución Industrial\"', 'programación'},

    'bellasartes' : {'\"Van Gogh\"', 'renacentista', '\"danza moderna\"', 'romanticismo',
    'barroco', 'música', 'expresionismo', 'basílica', 'sentimientos', 'escultor','picasso',
    'homero', '\"charles chaplin\"', 'tragicomedia', '\"pintura al óleo\"'},

    'humanidades' : {'shakespeare', 'homero', 'sócrates', 'literatura', 'lingüística',
    'psicología', 'filosofía', 'crítica', '\"gabriel garcía márquez\"','\"generación del 98\"'
    '\"caverna de platón\"', '\"antropología cultural\"'},

    'derecho' : {'\"derecho civil\"', 'legislatura', '\"jurisdicción\"', 'constitución',
    'pudiere', 'postulados', 'jurisprudencia', '\"tratado internacional\"', 'legislador',
    '\"derecho mercantil\"', '\"ley de sociedades\"'}
}


def CleanText(texto):
    #Limpiar HTML
    re_clean_html = re.compile('<.*?>')
    output = re.sub(re_clean_html, ' ', texto)
    output = unescape(output) # remove &...;

    #Sustituir todo lo que no sea una letra por un espacio
    output = re.sub(u'[^a-zA-ZáéíóúÁÉÍÓÚñçüÜ]',u' ', output, re.UNICODE)

    #Sustituir varios espacios seguidos por un solo espacio
    output = re.sub(u'[\ ]{2,}', u' ', output, re.UNICODE)

    #Normaliza los símbolos unicode
    output = unicodedata.normalize('NFC', output)

    return output

def GetRemoteSize(url):
    try:
        return urllib.urlopen(url).info().getheaders("Content-Length")[0]
    except:
        return False

def download_pdf(download_url):
    try:
        web_file = urllib.urlopen(download_url)
        local_file = open('tmp.pdf', 'w')
        local_file.write(web_file.read())
        size = local_file.tell()
        web_file.close()
        local_file.close()
        return size
    except:
        print "Error descargando PDF"
        return None

def convert_pdf_to_txt(path):
    try:
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        fp = file(path, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos=set()

        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
            interpreter.process_page(page)

        text = retstr.getvalue()

        fp.close()
        device.close()
        retstr.close()
        return text
    except:
        print "Error converting pdf... Maybe password protected"
	print "Error extrayendo info:", sys.exc_info()[0]
    	return ""


def get_single_rss(input_data):
    result = []
    html = bs(input_data, "lxml")
    feed_urls = html.findAll("link", rel="alternate")
    # extract URL and type
    for feed_link in feed_urls:
        url = feed_link.get("href", None)
        if url:
            result.append(url)

    if len(result) == 1:
        return result[0]
    else: return None

####### start main program

for corpus in semillas:

    if verbose:
        print "\n\nCorpus: " + corpus

    outputfile = outputFolder + "_CORPUS_" + corpus + ".txt"

    if verbose:
        print "Escribiendo al archivo: " + outputfile

    queries = []
    for i in xrange(num_searches):
        queries.append(" ".join(random.sample(semillas[corpus], num_keywords_per_search)))

    links = []
    for query in queries:
        if verbose:
            print "Gooogleando: " + query
	links.extend(search(query, num=num_links_per_search, stop=num_links_per_search, start=0,
	pause=search_delay, lang='es', only_standard=True))

    links = set(links)

    if verbose:
        print "Encontrados " + str(len(links)) + " en Google"


    with open(outputfile, 'a') as f:
        f.truncate()
        for link in links:
            try:
                # IF ITS PDF
                if re.search('\.pdf$',link):
                    print "Downloading pdf..."
                    pdf_size = GetRemoteSize(link)
                    if pdf_size is not None and pdf_size < max_pdf_bytes_per_source:
                        if download_pdf(link):
                            text = CleanText(convert_pdf_to_txt('tmp.pdf').decode('unicode-escape')).encode('utf8')
                            if len(text) > max_bytes_per_source:
                                text = text[:max_bytes_per_source] # Dont cut words...?
                            f.write(text)
                            if verbose:
                                print "Written PDF\t\t" + str(len(text))
                        else:
                            print "Error downloading PDF"
                    else:
                        print "PDF too big"
                else:
                    data = urllib.urlopen(link).read()
                    rss = get_single_rss(data)
                    if rss is not None:
                        #THERE IS A RSS (and only one)
                        if rss[0] == "/":
                            url_parsed = urlparse(link)
                            url_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=url_pasred)
                            rss = url_domain + rss
                        if verbose:
                            print "Leyendo RSS: " + rss
                        data = feedparser.parse(rss)
                        data = u''.join([CleanText(item.description) for item in data.entries])
                        if len(data) < min_bytes_per_source:
                            print "Skipping small info rss"
                        else:
                            if len(data) > max_bytes_per_source:
                                data = data[:max_bytes_per_source] # Dont cut words...?
                            f.write(data.encode('utf8'))
                            if verbose:
                                print "Written RSS bytes\t\t" + str(len(data))
                            else:
                                print "RSS data returned 0 length..."
                    else:
                        #ASSUME IS A TEXT/HTML/SOME READABLE FORMAT
                        g = Goose().extract(url=link)
                        text = CleanText(g.cleaned_text)
                        if len(text) < min_bytes_per_source:
                            print "Skipping small info webpage"
                        else:
                            if len(text) > max_bytes_per_source:
                                text = text[:max_bytes_per_source] # Dont cut words...?
                            f.write(text.encode('utf8'))
                            if verbose:
                                print "Written Webpage bytes\t\t" + str(len(text))
            except:
                print "Error extrayendo info:", sys.exc_info()[0]
                pass
