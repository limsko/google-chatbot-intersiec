#
#   Wgrywator fraz z pliku tekstowego do MySQL
#   Kamil Łuczak    2019.09.05  kamil@limsko.pl     http://limsko.pl
#	
# -*- coding: utf-8 -*-

import pymysql, io

class Database:

    def __init__(self):
        host = "127.0.0.1"
        user = "diagflow"
        password = "diagflow"
        db = "diagflow"
        self.con = pymysql.connect(host=host, user=user, password=password, db=db, charset='utf8', cursorclass=pymysql.cursors.
                                   DictCursor)
        self.cur = self.con.cursor()

    def insert_topic(self, topic, desc):
        sql = "INSERT INTO topics (topic, opis) VALUES (%s, %s)"
        self.cur.execute(sql, (topic, desc, ))
        self.con.commit()

    def get_topic(self, topic):
        sql = "SELECT topic, opis FROM topics WHERE `topic`=%s"
        self.cur.execute(sql, (topic,))
        result = self.cur.fetchone()
        if result:
            return result
        else:
            return 0

db = Database()

employee_handbook = open('Python_scenariusz_zmieniony.txt', 'r', encoding="utf-8")
while True:

    topic = employee_handbook.readline()
    if not (topic):
        break

    if (topic != '\r\n') and (len(topic.split(' ')) < 7):

        action_text = ''

        last_line = ''
        line = employee_handbook.readline()

        while (last_line != '\r\n') and (line != '\r\n') and (len(line.split(' ')) > 7):
            action_text += line
            last_line = line
            line = employee_handbook.readline()

        if action_text != '':

            action_text = action_text
            # Nazwa tematu zawsze małymi literami !!!
            topic_name = topic.strip().lower()

            if topic_name and action_text:
                # if getsizeof(action_text) > 1500:
                #     print('####ERROR ZA DŁUGI TEKST {} znaków: {}, {}\n####'.format(getsizeof(action_text), topic_name,
                #                                                                     action_text))
                # else:
                if db.get_topic(topic_name) == 0:
                    print('Zapisuje temat: {}\n{}'.format(topic_name, action_text))
                    db.insert_topic(topic_name, action_text)
                else:
                    print("Temat {} już istnieje")
            else:
                print('####ERROR: Nazwa tematu:\n{}\nWykryta tresc:\n{}\n####\n'.format(topic_name, action_text))