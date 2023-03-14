         'Foodie' - conversational bot (chatbot)

Problem Statement:
          An Indian startup named 'Foodie' wants to build a conversational bot (chatbot) which can help users discover restaurants across several Indian cities. You have been hired as the lead data scientist for creating this product.
       The main purpose of the bot is to help users discover restaurants quickly and efficiently and to provide a good restaurant discovery experience. The project brief provided to you is as follows.

1. Create Virtual Environment in Anaconda
------------------------------------------
## List env
conda info --envs

## Delete existing env
conda remove -n rasa --all

## create a new env named rasa (can name it anything else as well)
conda create -n rasa python==3.7.9

## Activate env 
conda activate rasa

## List installed packages
pip freeze

## Install Rasa module
pip install rasa

## connect venv to Jupyter notebook (Optional)
pip install ipykernel
python -m ipykernel install --user --name rasa --display-name rasa

2. Install Rasa and Spacy into Virtual environment
---------------------------------------------
## Install compatible spacy 
pip install rasa[spacy]==2.8.2
Or
pip install spacy==3.1.1

## Download spacy model
python -m spacy download en_core_web_md

3. Train the Rasa NLU and Rasa Core 
------------------------------------------
a. open the anaconda new terminal
b. # rasa train   # this will train both rasa NLU and rasa core

4. Start the action server
-------------------------------
# rasa run actions --cors "*"

5. Testing the Model
-------------------------------
# rasa shell

Example conversation : 
---------------------------------------------------
Your input ->  Hi
Hey, How is it going. How May I help you Today
Your input ->  please find me a restaurant
In what location?
Sorry I could not understand the location you provided. try some other location
Your input ->  delhi
? what kind of cuisine would you like? (Use arrow keys)
 » 1: Chinese (Chinese)
   2: Italian (Italian)
   3: South Indian (South Indian)
   4: North Indian (North Indian)
   5: Mexican (Mexican)
   6: American (American)
   Type out your own message...
Bot: What's the average budget for two people?
? None (Use arrow keys)
 » 1: Lesser than 300 (lt300)
   2: between 300 to 700 (lt700)
   3: More than 700 (gt700)
   Type out your own message...
User: <300
Bot: Showing you top rated restaurants:
1. Restaurant 1 in Area 1. And the average price for two people here is: XXX Rs
2. Restaurant 1 in Area 1. And the average price for two people here is: XXX Rs
Bot: Shall I send you details of all the restaurants on email? User: yes
Bot: To what email id should I send it to?
User: saravana4285@gmail.com
Bot: Done, thank you 








