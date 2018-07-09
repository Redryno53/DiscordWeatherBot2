#! /usr/bin/python

# Author - Redryno
# Email  - redryno.123@gmail.com

# Requirements - discord, weatheralerts
# python3 -m pip install -U discord.py
# python3 -m pip install -U weatheralerts

# Info - This program will post National Weather Service alerts in text to Discord chat
#	and tag areas provided within the States/Counties provided below.
#	This can be used for multiple states, and multiple counties on one Discord channel_id. 

################# EDIT THIS INFO #################

# enter your token below, in place of <token>
token = '<token>'
# enter the name you gave your bot, in place of <name>
Title = '<name>'
# enter the channel id where you would like the info posted, in place of <channelID>
channel_id = '<channelID>'

# State abbreviation and Counties within that state to get info about alerts from the NWS
Counties_in_State = [{'MO':['St. Charles', 'St. Louis', 'Franklin', 'Jefferson', 'Lincoln']}, 
					# {'IL':['Madison', 'St. Clair']}
					]

# Areas within the above Counties to tag with '@' symbol in Discord chat (@ symbol will be added by program)
Cities_in_County = [{'St. Charles':['LakeSaintLouis', 'Ofallon', 'StCharles', 'MainStCharles',
					'StPeters', 'RecPlex', 'Wentzville']}, 
					{'St. Louis':['Affton', 'Ballwin', 'Brentwood', 'Bridgeton', 'CWE', 'CherokeeStreet',
					'Chesterfield', 'Crestwood', 'CreveCoeur', 'CreveCoeurLakePark', 'Clayton',
					'DelmarLoop', 'DesPeres', 'DowntownSTL', 'Ellisville', 'Eureka', 'Fenton',
					'FentonPark', 'Ferguson', 'Florissant', 'ForestPark', 'Hazelwood', 'JeffersonBarracks', 
					'Kirkwood', 'KirkwoodPark', 'Ladue', 'Manchester', 'Maplewood', 'MarylandHeights',
					'MaryvilleUni', 'Mehville', 'MidTown', 'Normandy', 'NorthCity', 'Olivette', 
					'Overland', 'Sappington', 'SculpturePark', 'Shrewsbury', 'SLU', 'Soulard', 'SouthCity',
					'StAnn', 'StJohn', 'SunsetHills', 'TowerGrove', 'TownAndCountry', 'UCity',
					'ValleyPark', 'WebsterGroves', 'WebsterUni', 'Wildwood']},
					{'Franklin':['Pacific']}, 
					{'Jefferson':['Arnold', 'Festus', 'Herculaneum', 'HighRidge', 'Pevely']},
					{'Lincoln':['Troy']},
					# {'Madison':['Alton', 'Edwardsville', 'GraniteCity']}, 
					# {'St. Clair':['Belleville', 'OfallonIL', 'Shiloh']}
					]

##################################################


import asyncio, discord, time, threading, readline
from weatheralerts import WeatherAlerts
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s') 
logging.disable(logging.NOTSET) # NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL

Started = time.time()
Posted = []
loop = asyncio.new_event_loop()
bot = discord.Client()
bot_token = True
message_queue = asyncio.Queue()

def bot_thread(loop, bot, bot_token, message_queue, channel_id):
	asyncio.set_event_loop(loop)

	@bot.event
	async def on_ready():
		while True:
			data = await message_queue.get()
			event = data[0]
			message = data[1]
			channel_id = data[2]
			try:
				await bot.send_message(bot.get_channel(channel_id), message)
			except:
				pass
			event.set()

	bot.run(token, bot = bot_token)

thread = threading.Thread(target = bot_thread, args = (loop, bot, bot_token, message_queue, channel_id), daemon = True)
thread.start()

def send(channel_id, message):
	event = threading.Event()
	message_queue.put_nowait([event, message, channel_id])
	event.wait()

print('Bot logging in...')
msg = "{} has been initiated.".format(Title)
send(channel_id, msg)


def CheckForAlerts():
	logging.warning('-------------------------------------------------------------------')
	global Started
	global Posted
	Alert_to_Post = []
	# once every 24hrs clear the Posted list
	if (time.time() - Started) >= 86400:
		Posted = []
		Started = time.time()

	# check for alerts for the counties privieded 
	for q in Counties_in_State:
		for currentState, Counties in q.items():
			nws = WeatherAlerts(state=currentState)
			for alert in nws.alerts:
				for currentCounty in Counties:
					Is_Posted = False
					if currentCounty in alert.areadesc:
						Alert = [alert.severity, [currentCounty], alert.title, alert.summary]
						logging.debug('Alert = {}'.format(Alert))
						try:
							if Alert not in Alert_to_Post:
								if Alert_to_Post == []:
									Alert_to_Post.append(Alert)
									logging.debug("Alert to post empty, adding to alert to post.  {}".format (alert))
									Is_Posted = True
								else:
									for i in Alert_to_Post:
										if (i[2] == Alert[2]) and (i[3] == Alert[3]):
											if currentCounty not in i[1]:
												i[1].append(currentCounty)
												Is_Posted = True
									if Is_Posted == False:	
										Alert_to_Post.append(Alert)
										logging.debug("Alert doesn't match any found.  {}".format (alert))
										Is_Posted = True
						except Exception:
							Alert_to_Post.append(Alert)
							logging.debug("Try error, adding to alert to post.  {}".format (alert))

	logging.debug('Alert_to_Post = {}'.format(Alert_to_Post))

	# check if alert has been posted
	if Posted == []:
		for new_alert in Alert_to_Post:
			tempList = []
			tempList4 = []
			for i in new_alert[1]:
				tempList.append(i)
			for i in tempList:
				for z in Cities_in_County:
					for county, city in z.items():
						if county in i:
								for m in city:
									tempList4.append(m)
				cities_affected = ' @{}'.format(' @'.join(tempList4))
			msg = "**{}** - {} - {}".format(new_alert[2], new_alert[3], cities_affected)
			send(channel_id, msg)
			Posted.append(new_alert)
	else:
		for new_alert in Alert_to_Post:
			tempList4 = []
			if new_alert not in Posted:
				tempList = []
				for i in new_alert[1]:
					tempList.append(i)
				for i in tempList:
					for z in Cities_in_County:
						for county, city in z.items():
							if county in i:
								for m in city:
									tempList4.append(m)
				cities_affected = ' @{}'.format(' @'.join(tempList4))
				msg = "**{}** - {} - {}".format(new_alert[2], new_alert[3], cities_affected)
				send(channel_id, msg)
				Posted.append(new_alert)

try:
	kek = False
	while not kek:
		time.sleep(0.1)
		if bot._is_ready.is_set(): # wait until the ready event
			while True:
				CheckForAlerts()
				time.sleep(1)
			kek = True
except KeyboardInterrupt:
	pass
