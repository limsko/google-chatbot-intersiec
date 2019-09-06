#
#   Webhook for Diaglow
#	Beta Version
#   Kamil Łuczak    2019.09.05  kamil@limsko.pl     http://limsko.pl
#	
# -*- coding: utf-8 -*-
from flask import Flask, request, json
import pymysql, logging
app = Flask(__name__)

# Logging
logger = logging.getLogger('webhook')
hdlr = logging.FileHandler('/home/kamil/diagflow/webhook.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

# MySQL configurations
# https://sweetcode.io/flask-python-3-mysql/

# Data tables:
# CREATE TABLE `diagflow`.`topics` ( `id` INT(11) NOT NULL AUTO_INCREMENT , `topic` VARCHAR(255) NOT NULL , `opis` TEXT NOT NULL , PRIMARY KEY (`id`), UNIQUE `topic` (`topic`)) ENGINE = InnoDB;
# CREATE TABLE `diagflow`.`synonyms` ( `id` INT NOT NULL AUTO_INCREMENT , `synonym` VARCHAR(255) NOT NULL , `topicid` INT NOT NULL , PRIMARY KEY (`id`)) ENGINE = InnoDB;


class Database:

    def __init__(self):
    	# Fill the params below!
        host = "localhost"
        user = ""
        password = ""
        db = ""
        self.con = pymysql.connect(host=host, user=user, password=password, db=db, charset='utf8', cursorclass=pymysql.cursors.
                                   DictCursor)
        self.cur = self.con.cursor()

    def list_topics(self):
        self.cur.execute("SELECT topic, opis FROM topics")
        result = self.cur.fetchall()
        return result

    def get_topic(self, topic):
        sql = "SELECT topic, opis FROM topics WHERE `topic`=%s"
        self.cur.execute(sql, (topic,))
        result = self.cur.fetchone()
        logger.info(result)
        if result:
            return result
        else:
            return 0

    def get_synonym(self, synonym):
        sql = "SELECT topicid FROM synonyms WHERE synonym=%s"
        self.cur.execute(sql, (synonym,))
        result = self.cur.fetchone()
        logger.info(result)
        if result:
            sql = "SELECT topic, opis  FROM topics WHERE id=%s"
            self.cur.execute(sql, (result['topicid'],))
            result = self.cur.fetchone()
            logger.info(result)
            if result:
                return result
            else:
                return 0
        else:
            return 0


def buildReply(info):
    if info == 0:
        info = "Nie znalazłem informacji na podany temat"
    return {
        'fulfillmentText': info,
    }


@app.route("/", methods=['GET','POST'])
def main():
    db = Database()
    try:
        req = request.get_json(silent=True, force=True)
        print(req)
        logger.info(req)
        query = req.get('queryResult').get('queryText')
        logger.info(query)
        if 'lista tematów' in query:
            logger.info("Wyświetl liste tematów")
            list = db.list_topics()
            answer = ''
            for entry in list:
                answer = answer + entry['topic'] + ', '
            return buildReply(answer)
        topic = req.get('queryResult').get('parameters').get('topic')
        logger.info(topic)
        if topic:
            logger.info("looking for {}".format(topic))
            desc = db.get_topic(topic)
            if desc != 0 and desc['opis']:
                logger.info("got topic!")
                return buildReply(desc['opis'])
            desc = db.get_synonym(topic)
            if desc != 0 and desc['opis']:
                logger.info("got synonym!")
                return buildReply(desc['opis'])
            return buildReply(0)
        else:
            logger.info("if topic failed")
        return buildReply(0)

    except Exception as e:
        return json.dumps({'error':str(e)})


if __name__ == "__main__":
    app.run(debug=True)