import os
import json

import db_setup
import ner_handler


def import_commersant(path):

	for file in os.listdir(path):

		with open(path + file, encoding='UTF-8') as json_file:

			json_data = json.loads(json_file.read())

			for data in json_data:

				data = ner_handler.process_news(data)

				cs = db_setup.Commersant(

					datetime=data['datetime'],
					rubric=data['rubric'],
					link=data['rubric'],

					title=data['header'],
					text=data['header'],

					locs=data['locs'],
					pers=data['pers'],
					orgs=data['orgs']

				)

				db_setup.session.add(cs)

	db_setup.session.commit()