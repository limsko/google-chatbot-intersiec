#
#   Procesor Synonimów
#   Kamil Łuczak    2019.09.05  kamil@limsko.pl     http://limsko.pl
#	# -*- coding: utf-8 -*-

from stop_words import get_stop_words
from bs4 import BeautifulSoup
import requests
import re
import pymysql
import urllib.parse

class Database:

    def __init__(self):
        host = "127.0.0.1"
        user = "diagflow"
        password = "diagflow"
        db = "diagflow"
        self.con = pymysql.connect(host=host, user=user, password=password, db=db, charset='utf8', cursorclass=pymysql.cursors.
                                   DictCursor)
        self.cur = self.con.cursor()

    def list_topics(self):
        self.cur.execute("SELECT id, topic, opis FROM topics")
        result = self.cur.fetchall()
        return result

    def insert_synonym(self, topicid, synonym):
        sql = "INSERT INTO synonyms (topicid, synonym) VALUES (%s, %s)"
        self.cur.execute(sql, (topicid, synonym, ))
        self.con.commit()

    def get_synonym(self, synonym):
        sql = "SELECT topicid FROM synonyms WHERE synonym=%s"
        self.cur.execute(sql, (synonym,))
        result = self.cur.fetchone()
        if result:
            sql = "SELECT topic, opis  FROM topics WHERE id=%s"
            self.cur.execute(sql, (result['topicid'],))
            result = self.cur.fetchone()
            if result:
                return result
            else:
                return 0
        else:
            return 0


def get_synonyms(word):
    word = str(word)
    print("The word is: {}".format(word))
    s = requests.session()
    synonyms_output = []
    synonyms_output.append(word)
    # Pobieram data=h
    response = s.get('http://odmiana.net')
    s.encoding = 'utf-8'
    html = response.text
    x = re.search(r'data\-h\="([a-f0-9]*)\"', html)
    if x:
        varH = x.group(1)
        # Pobieram rzeczownik
        # http://odmiana.net/a.filtruj.php?h=bd077a519d7ac9e6623155b96dbaefd5&f=FRAZA
        url = 'http://odmiana.net/a.filtruj.php?h={}&f={}'.format(varH, urllib.parse.quote(word))
        response = s.get(url)
        print('Pobieram rzeczownik: {}'.format(url))
        code = response.status_code
        if code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            for rzeczownik in soup.find_all('b'):
                if (rzeczownik.text == 'Lista wyszukiwania jest pusta!'):
                    print("Brak znalezionych wynikow, uznaje słowo za rzeczownik, aby kontynuować")
                    rzeczownikVar = word
                else:
                    print("Rzeczownik to: {}".format(rzeczownik.text))
                    rzeczownikVar = rzeczownik.text

                # Add noun to list of synonyms
                if rzeczownikVar != 'Brak znalezionych wynikow':
                    if rzeczownik.text not in synonyms_output:
                        synonyms_output.append(rzeczownikVar)

                # Mamy rzeczownik
                # Odmiana przez przypadki
                # http://odmiana.net/odmiana-przez-przypadki-rzeczownika-drzewo
                url = 'http://odmiana.net/odmiana-przez-przypadki-rzeczownika-{}'.format(urllib.parse.quote(rzeczownikVar))
                response = s.get(url)
                s.encoding = 'utf-8'
                print(
                    "Pobieram odmiany: {}".format(url))
                code = response.status_code
                if code == 200:
                    html = response.text
                    soup = BeautifulSoup(html, 'lxml')
                    skip = ['Przypadek', 'Liczba pojedyncza', 'Liczba mnoga', 'Mianownik (kto? co?):',
                            'Narzędnik (z kim? z czym?):', 'Dopełniacz (kogo? czego?):', 'Celownik (komu? czemu?):',
                            'Biernik (kogo? co?):', 'Miejscownik (o kim? o czym?):', 'Wołacz (hej!):']
                    for main_div in soup.findAll('div', {'class': 'ekran'}):
                        for element in main_div.findAll('td'):
                            if element.text not in skip and element.text not in synonyms_output:
                                synonyms_output.append(element.text)
                # Pobieramy wszystkie synonimy
                # http://intersiechost.home.pl/_pub/synonimy/index.php?word=drzewo
                url = 'http://intersiechost.home.pl/_pub/synonimy/index.php?word={}'.format(urllib.parse.quote(rzeczownikVar))
                response = s.get(url)
                html = response.text
                print('Pobieram synonimy: {}'.format(url))
                synonimy = html.split(";")
                for synonim in synonimy:
                    if synonim not in synonyms_output and synonim != "":
                        synonyms_output.append(synonim)
                break
    else:
        print("Nie znaleziono rzeczownika")
    return synonyms_output


db = Database()
topics = db.list_topics()
stop = get_stop_words('polish')

for result in topics:
    for word in result['topic'].split():


        # Beautify
        strips = ['(', ')', ',']
        for strip in strips:
            word = word.strip(strip)
        skip_words = ['ang.']

        if word not in skip_words:

            print("look for synonym: {}, of topic {}: {}".format(word, result['id'], result['topic']))

            # Pomijam zbędne słowa
            if word in stop:
                print("Word {} in stop-words, continue.".format(word))
                continue

            synonyms = set()
            for syn in get_synonyms(word):
                synonyms.add(syn)

            print("topicid, word, synonyms")
            print(result['id'], word, synonyms)

            db.insert_synonym(result['id'], word)

            for dictionary_synonym in synonyms:
                db.insert_synonym(result['id'], dictionary_synonym)
            #     synonym_key = datastore_client.key(kind, dictionary_synonym)
            #     synonym = datastore.Entity(key=synonym_key)
            #     synonym['synonym'] = result.key.name
            #     print("synonym key is: {}, dict_synonym_is {}, [synonym] is: {} ".format(synonym_key, dictionary_synonym,
            #                                                                              result.key.name))
            #     datastore_client.put(synonym)
        else:
            print("Skip: ",format(word))