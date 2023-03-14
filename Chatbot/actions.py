from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import pandas as pd
import json

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_mail_check import send_email

ZomatoData = pd.read_csv('zomato.csv', encoding='ISO-8859-1')
ZomatoData = ZomatoData.drop_duplicates().reset_index(drop=True)
WeOperate = [ 'Ahmedabad', 'Bengaluru', 'Chennai', 'Delhi', 'Hyderabad', 'Kolkata', 'Mumbai' ,'Pune', 'Agra', 'Ajmer', 'Aligarh', 'Amravati', 'Amritsar', 'Asansol', 'Aurangabad', 'Bareilly', 'Belgaum', 'Bhavnagar', 'Bhiwandi', 'Bhopal', 'Bhubaneswar', 'Bikaner', 'Bilaspur','Bokaro Steel City', 'Chandigarh', 'Coimbatore', 'Cuttack', 'Dehradun', 'Dhanbad', 'Bhilai', 'Durgapur', 'Erode', 'Faridabad', 'Firozabad', 'Ghaziabad', 'Gorakhpur', 'Gulbarga', 'Guntur', 'Gwalior', 'Gurgaon', 'Guwahati', 'Hamirpur', 'Hubli–Dharwad', 'Indore', 'Jabalpur', 'Jaipur', 'Jalandhar', 'Jalgaon', 'Jammu', 'Jamnagar', 'Jamshedpur', 'Jhansi', 'Jodhpur', 'Kakinada', 'Kannur', 'Kanpur', 'Karnal', 'Kochi', 'Kolhapur', 'Kollam','Kozhikode', 'Kurnool', 'Ludhiana', 'Lucknow', 'Madurai', 'Malappuram', 'Mathura', 'Mangalore', 'Meerut', 'Moradabad', 'Mysore', 'Nagpur', 'Nanded', 'Nashik', 'Nellore', 'Noida', 'Patna', 'Pondicherry', 'Purulia', 'Prayagraj', 'Raipur', 'Rajkot', 'Rajahmundry', 'Ranchi', 'Rourkela', 'Ratlam', 'Salem', 'Sangli', 'Shimla', 'Siliguri', 'Solapur', 'Srinagar', 'Surat', 'Thanjavur', 'Thiruvananthapuram', 'Thrissur', 'Tiruchirappalli', 'Tirunelveli', 'Tiruvannamalai', 'Ujjain', 'Bijapur', 'Vadodara', 'Varanasi', 'Vasai-Virar City', 'Vijayawada', 'Visakhapatnam', 'Vellore Warangal']

def RestaurantSearch(City,Cuisine):
	TEMP = ZomatoData[(ZomatoData['Cuisines'].apply(lambda x: Cuisine.lower() in x.lower())) & (ZomatoData['City'].apply(lambda x: City.lower() in x.lower()))]
	return TEMP[['Restaurant Name','Address','Average Cost for two','Aggregate rating']]

class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_restaurant'
		
	def run(self, dispatcher, tracker, domain):
		#config={ "user_key":"0fffffff9c"}#type your zomato API key here
		#zomato = zomatopy.initialize_app(config)
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		cuisine = cuisine.lower()
		#budget1 = tracker.get_slot('budget')
		#budget = 'average cost for two ' + str(budget1)
		budget = tracker.get_slot('budget')
		if budget == 'low':
			cost_to_filer_min = 0
			cost_to_filer_max = 300
		elif budget == 'mid':
			cost_to_filer_min = 301
			cost_to_filer_max = 700
		elif budget == 'high':
			cost_to_filer_min = 701
			cost_to_filer_max = 9999
		cols = ['restaurant name', 'restaurant address', 'avg. budget for two', 'zomato rating']
		resrnt_df = pd.DataFrame(columns = cols)
		location_detail=zomato.get_location(loc, 1)
		#print(location_detail)
		d1 = json.loads(location_detail)
		lat=d1["location_suggestions"][0]["latitude"]
		lon=d1["location_suggestions"][0]["longitude"]
		cuisines_dict={'american':1,'chinese':25,'mexican':73,'italian':55,'north indian':50,'south indian':85}
		#results=zomato.restaurant_search(str(budget), lat, lon, str(cuisines_dict.get(cuisine)),"rating","desc", 20)
		results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)),"rating","desc", 20)#get first 20 and filter budget later
		response=""
		for i in range(0,5, 1):
			d = json.loads(results[i])
			if d['results_found'] != 0:
				#print(json.dumps(d, indent=2))
				for restaurant in d['restaurants']:
					curr_res = {'zomato rating':restaurant['restaurant']["user_rating"]["aggregate_rating"],'restaurant name':restaurant['restaurant']['name'],'restaurant address': restaurant['restaurant']['location']['address'], 'avg. budget for two': restaurant['restaurant']['average_cost_for_two']}		
					if (curr_res['avg. budget for two'] >= cost_to_filer_min) and (curr_res['avg. budget for two'] <= cost_to_filer_max):						
						resrnt_df.loc[len(resrnt_df)] = curr_res
			#print(len(resrnt_df))
		# sort restarants on aggregate rating  
		resrnt_df = resrnt_df.sort_values(['zomato rating','avg. budget for two'], ascending=[False,True])
		resrnt_df10 = resrnt_df.head(10)
		resrnt_df = resrnt_df.head(5)
		resrnt_df = resrnt_df.reset_index(drop=True)
		resrnt_df.index = resrnt_df.index.map(str)

		# print to console in format
		if len(resrnt_df) != 0:
			for index, row in resrnt_df.iterrows():
				response = response+ index + ". Found \""+ row['restaurant name']+ "\" in "+ row['restaurant address']+" has been rated "+ row['zomato rating']+"\n"
		else:
			response = 'Found 0 restaurants in given price range'
		#print(response)
		dispatcher.utter_message(response)
		return [SlotSet('budget',budget)]


class ActionSendMail(Action):
	def name(self):
		return 'action_send_mail'
	
	def run(self,dispatcher,tracker,domain):

		body=""
		file=open('body.txt','r')
		
		for line in file.readlines():
			body+=line
		file.close()
		
		gmail_user="saravana4285@gmail.com"
		gmail_password="Muthuraman1"
		
		sent_from=gmail_user
		to=tracker.get_slot('email')
		subject=" Restaurant recommendations in "+tracker.get_slot("location").title()
		
		email_text= """\  
		From: %s  
		To: %s  
		Subject: %s
		%s
		""" % (sent_from,to, subject, body)
		
		try:  
			server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
			server.ehlo()
			server.login(gmail_user, gmail_password)
			server.sendmail(sent_from, to, email_text)
			server.close()
			dispatcher.utter_template("utter_email_Sent", tracker)
			
		except:		
			
			dispatcher.utter_template("utter_email_error", tracker)
			
		return [SlotSet('email',to)]


class Check_location(Action):
	def name(self):
		return 'action_check_location'
		
	def run(self, dispatcher, tracker, domain):
		list_loc = [ 'Ahmedabad', 'Bengaluru', 'Chennai', 'Delhi', 'Hyderabad', 'Kolkata', 'Mumbai' ,'Pune', 'Agra', 'Ajmer', 'Aligarh', 'Amravati', 'Amritsar', 'Asansol', 'Aurangabad', 'Bareilly', 'Belgaum', 'Bhavnagar', 'Bhiwandi', 'Bhopal', 'Bhubaneswar', 'Bikaner', 'Bilaspur','Bokaro Steel City', 'Chandigarh', 'Coimbatore', 'Cuttack', 'Dehradun', 'Dhanbad', 'Bhilai', 'Durgapur', 'Erode', 'Faridabad', 'Firozabad', 'Ghaziabad', 'Gorakhpur', 'Gulbarga', 'Guntur', 'Gwalior', 'Gurgaon', 'Guwahati', 'Hamirpur', 'Hubli–Dharwad', 'Indore', 'Jabalpur', 'Jaipur', 'Jalandhar', 'Jalgaon', 'Jammu', 'Jamnagar', 'Jamshedpur', 'Jhansi', 'Jodhpur', 'Kakinada', 'Kannur', 'Kanpur', 'Karnal', 'Kochi', 'Kolhapur', 'Kollam','Kozhikode', 'Kurnool', 'Ludhiana', 'Lucknow', 'Madurai', 'Malappuram', 'Mathura', 'Mangalore', 'Meerut', 'Moradabad', 'Mysore', 'Nagpur', 'Nanded', 'Nashik', 'Nellore', 'Noida', 'Patna', 'Pondicherry', 'Purulia', 'Prayagraj', 'Raipur', 'Rajkot', 'Rajahmundry', 'Ranchi', 'Rourkela', 'Ratlam', 'Salem', 'Sangli', 'Shimla', 'Siliguri', 'Solapur', 'Srinagar', 'Surat', 'Thanjavur', 'Thiruvananthapuram', 'Thrissur', 'Tiruchirappalli', 'Tirunelveli', 'Tiruvannamalai', 'Ujjain', 'Bijapur', 'Vadodara', 'Varanasi', 'Vasai-Virar City', 'Vijayawada', 'Visakhapatnam', 'Vellore Warangal']
		loc = tracker.get_slot('location')
		if loc is not None:
			if loc.lower() in list_loc:
				return[SlotSet('location',loc)]
			else:
				dispatcher.utter_message("Sorry we do not operate in this area yet. try some other location")
				return[SlotSet('location',None)]
		else:
			dispatcher.utter_message("Sorry I could not understand the location you provided. try some other location")
			return[SlotSet('location', None)]

class ActionRestarted(Action): 	
    def name(self): 		
        return 'action_restarted' 	
    def run(self, dispatcher, tracker, domain): 
        return[Restarted()] 