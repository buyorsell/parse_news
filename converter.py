import os
import json

import db_setup
import ner_handler


def convert_commersant(path):

	for file in os.listdir(path):

		with open(path + file, encoding='UTF-8') as json_file:

			json_data = json.loads(json_file.read())

			for data in json_data:

				data = ner_handler.process_news(data)

				db_setup.Commersant(

					datetime=data['datetime'],
					rubric=data['rubric'],
					link=data['rubric'],

					title=data['header'],
					text=data['header'],

					locs= Column('locs', ARRAY(TEXT)),
					pers=Column('pers', ARRAY(TEXT)),
					orgs=Column('orgs', ARRAY(TEXT))


				)



				ins = meduza_db.insert().values(

					title=data['header'],
					text=data['text'],

					date=convert_meduza_date(data['datetime']),

					link=''
				)

				conn.execute(ins)


convert_meduza()
