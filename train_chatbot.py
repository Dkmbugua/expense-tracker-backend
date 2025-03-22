import os
import random
import spacy
import pickle
from spacy.pipeline.textcat import Config, single_label_cnn_config
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta

# Initialize spaCy blank model
nlp = spacy.blank("en")

# Add Text Categorizer to Pipeline
config = Config().from_str(single_label_cnn_config)
textcat = nlp.add_pipe("textcat", config=config)

# Define Intent Labels for Nairobi Students & Workers
intents = ["savings", "budgeting", "investments", "loans", "student_finance", "nairobi_life", "savings_goal"]
for intent in intents:
    textcat.add_label(intent)

# Expanded AI Training Data with Localized Context
training_data = [
    {
        "tag": "savings",
        "patterns": [
            "How can I save money as a Kenyan student?",
            "Naweza aje pata dooh na budget yangu ya campus?",
            "Give me saving tips, bro!",
            "What’s the best way to save in Kenya with this economy?",
            "What percentage of my income should I save in 2025?",
            "How do I save for a goal like a phone or rent?",
            "Naweza aje tumia pesa za HELB vizuri instead of kulipia vibes?",
            "Is M-Shwari still a good savings option now?",
            "How do I save while surviving Nairobi’s high prices?",
            "Naweza save aje na mshahara mdogo na bei ziko juu?",
            "How do I save while hustling in Nairobi’s madness?",
            "Naweza save aje pesa za pocket money bila kuwa broke?",
            "How do I stop spending all my cash and save instead?",
            "Nifanye nini na pesa kidogo niko nayo ili nisave?"
        ],
        "responses": [
            # English Responses
            "Yoh, as a student, atleast take 20% of your HELB straight to savings—before it vanishes on smocha and ice pops! Create your saving goal and stick to it.",
            "Bro, mm kama ni ww i save KSH 50bob daily in a secure place, within a month itakuwa KSH 1500 a month, no stress. Try you best to avoid sherehe during you broke moments?",
            "With this 2025 economy, try 50/30/20: 50% for rent and food, 30% for fun but be careful liquor and beer is for people with money, 20% for savings. live within your means or utainama",
            "Nairobi’s wild—cook ugali at home instead of hitting hotels, you’ll save like KSH 1,500 a week. You cook or need some cheap recipes, pitia kibandaski and see their recipe",
            "M-Shwari’s interest is favourably low  but your cash stays safe. I lock KSH 1,000 monthly. Thinking of jumping in?",
            "Even KSH 50 a day adds up—saved KSH 18,000 in a year with that trick! What’s your target?",
            "Hustling in Nairobi? Skip Java for vibanda, I save KSH 300 daily that way. Can you roll with that or need more hacks?",
            "Pocket money’s tight? Cut random outings, brew kettle tea—saves you KSH 100 a day. What do you usually spend on?",
            "To stop blowing cash, set a small goal like KSH 2,000 a month—feels like a win when you hit it. What’s your vibe?",
            # Swahili Responses
            "Bro, kama na HELB, weka 10% aside kabla haijapotea kwa fare au shopping—future yako itakucheki poa. Unasave kwa nini?",
            "Na mshahara mdogo, mimi naanza na coin jar—hadi KSH 100 daily inafika mbali. Unahustle nini?",
            "Nairobi ni moto, lakini pika nyumbani badala ya kula nje—unasave KSH 2,000 kwa wiki. Unapika aje?",
            "M-Shwari ni rahabu—mimi nalock pesa zangu hapo kila mwezi. Unafikiria kuweka zako wapi?",
            "Hata KSH 50 kwa siku inakua pesa mingi—mimi nimejaribu na nikapata KSH 18,000 mwaka moja! Una target gani?",
            "Bei ziko juu, lakini weka loose change kwa wallet—inaweza kufika KSH 300 kwa wiki. Unajaribu hiyo ama unataka trick ingine?",
            "Pesa ya pocket iko kidogo? Kata chai ya nje, pika kettle—unasave KSH 100 daily. Unapenda kuspender wapi?"
        ]
    },
    {
        "tag": "budgeting",
        "patterns": [
            "How do I create a budget?",
            "Nipangaje bajeti yangu?",
            "Give me budgeting advice.",
            "Best way to manage expenses?",
            "Naweza gavana aje pesa yangu kama student?",
            "How do I budget my salary in Nairobi?",
            "Naweza budget aje na HELB tu?",
            "What’s the best way to allocate income as a working Kenyan?"
        ],
        "responses": [
            # English Responses
            "Start with your must-haves—fees, rent, food—then sneak some into savings. Want me to sketch a student budget for you?",
            "I’d go 50/30/20 with a salary: 50% needs, 30% wants, 20% savings. Got a salary figure I can work with?",
            "Ditch Uber for matatus or SWVL—keeps cash in your pocket. Need more transport hacks for Nairobi?",
            "For HELB, I’d split it: 60% fees, 30% survival, 10% savings. How’s your HELB looking?",
            # Swahili Responses
            "Kama student, panga HELB yako—fees, rent, chakula, na uweke kidogo savings. Unataka breakdown ya hiyo?",
            "Mimi Nairobi, napanga KSH 200 kwa matatu, KSH 100 lunch—bajeti iko tight lakini inafanya kazi. Unapanga aje siku yako?",
            "Na mshahara, jaribu 50/30/20—50% rent na food, 30% raha, 20% savings. Nishow mshahara wako nikuwekee?",
            "HELB pekee? Weka 60% fees, 30% maisha, 10% savings—unasurvive aje na hiyo?"
        ]
    },
    {
        "tag": "investments",
        "patterns": [
            "Where should I invest?",
            "Nipee mawazo ya investment Kenya.",
            "Best investments in Kenya?",
            "How can I grow my money?",
            "Naweza weka pesa wapi i-grow?",
            "Is crypto a good investment?",
            "Are SACCOs a good investment in Kenya?",
            "Je, Money Market Funds ni poa?"
        ],
        "responses": [
            # English Responses
            "CBK bonds are safe—10-14% returns, no drama. Want me to tell you how to sign up?",
            "SACCOs like Stima or Harambee pay solid dividends. Need a list of legit ones to check out?",
            "Crypto’s risky, but Money Market Funds like CIC give steady growth. You into safe bets or big swings?",
            # Swahili Responses
            "Weka pesa kwa bond za CBK—10-14% returns, hakuna stress. Unataka nikuonyeshe jinsi ya kuanza?",
            "SACCO kama Stima ni poa kwa dividends—mimi niko na moja. Unahitaji majina ya SACCO za kuaminika?",
            "Crypto ni hatari, lakini Money Market Funds kama Sanlam ni salama na zinakua. Unapenda aje?"
        ]
    },
    {
        "tag": "savings_goal",
        "patterns": [
            "I want to set a savings goal",
            "Nisaidie kuweka savings goal",
            "Help me track my savings",
            "I need to save for something big",
            "Naokoa aje kwa project kubwa?",
            "How do I stay disciplined with savings?",
            "Nifanye nini nisitumie savings zangu?"
        ],
        "responses": [
            # English Responses
            "Cool, what’s your target? KSH 10,000 for a sem or KSH 50,000 in a year? Let’s break it down together!",
            "I’d set you a tracking plan—weekly or monthly updates, your call. How often you wanna check in?",
            "Discipline’s key—lock it in M-Shwari’s locked account. Wanna try that or got another spot?",
            # Swahili Responses
            "Poa! Target yako ni nini? KSH 10,000 kwa sem ama KSH 50,000 kwa mwaka? Tuipange pamoja?",
            "Nikuwekee plan ya kufollow savings? Unaweza nicheki kila wiki au mwezi—unachagua nini?",
            "Usitumie savings zako—lock pesa kwa M-Shwari au jar ngumu kufika. Unajaribu hiyo ama unataka njia ingine?"
        ]
    },
    {
        "tag": "nairobi_life",
        "patterns": [
            "How do I survive in Nairobi?",
            "Naweza ishi aje Nairobi bila stress?",
            "Best places to live on a budget?",
            "How can I spend less in Nairobi?",
            "What’s the cost of living in Nairobi?",
            "Je, Nairobi ni ghali sana?",
            "Nifanye nini kupunguza gharama za maisha Nairobi?"
        ],
        "responses": [
            # English Responses
            "Nairobi’s a hustle! Cook at home instead of eating out—saves me KSH 2,000 weekly. Want a cheap meal plan?",
            "Live in Rongai or Kasarani—rent’s way lower than Westlands. Need more spot ideas?",
            "Matatus over Uber any day—saves cash. Got a route you wanna cut costs on?",
            # Swahili Responses
            "Nairobi ni moto! Pika nyumbani badala ya hoteli—mimi nasave KSH 2,000 kwa wiki. Unataka meal plan rahabu?",
            "Kaa Rongai ama Githurai—rent ni bei poa kuliko CBD. Unahitaji maeneo zaidi ya kuangalia?",
            "Matatu ni rahabu kuliko Uber—pesa inabaki. Una route gani unataka kupunguza gharama?"
        ]
    }
]

# Train AI Chatbot Model with 20 Iterations for improved accuracy

def train_chatbot():
    nlp.initialize()
    for _ in range(20):
        losses = {}
        for data in training_data:
            for pattern in data["patterns"]:
                doc = nlp.make_doc(pattern)
                example = spacy.training.Example.from_dict(doc, {"cats": {data["tag"]: 1.0}})
                nlp.update([example], losses=losses)

    # Save trained model
    nlp.to_disk("chatbot_model")
    with open("responses.pkl", "wb") as file:
        pickle.dump(training_data, file)
    print("✅ AI Model Trained & Saved as 'chatbot_model'")

# AI Chatbot Response with Personalized Follow-ups

def chatbot_response(user_input):
    doc = nlp(user_input)
    predicted_intent = max(doc.cats, key=doc.cats.get)
    for intent in training_data:
        if intent["tag"] == predicted_intent:
            response = random.choice(intent["responses"])
            follow_ups = {
                "savings": "Would you like me to help set up a savings tracker?",
                "budgeting": "Do you want a budgeting template for your income?",
                "investments": "Want to compare SACCOs and government bonds?",
                "loans": "Are you considering a business or personal loan?",
                "nairobi_life": "Would you like recommendations on cheap housing & food?",
                "savings_goal": "I can track your savings! Want to set reminders?"
            }
            return response + " " + follow_ups.get(predicted_intent, "")
    return "I'm here to help! Could you rephrase your question?"

# Train chatbot when script is run
if __name__ == "__main__":
    train_chatbot()