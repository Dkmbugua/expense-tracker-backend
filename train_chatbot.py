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
            "How can I save money?", "Nifanyeje kuokoa pesa?", "Give me saving tips.",
            "What’s the best way to save in Kenya?", "What percentage of income should I save?",
            "How do I save for a goal?", "Naokoe vipi kutoka HELB?",
            "Is M-Shwari a good savings option?", "How can I save while living in Nairobi?",
            "Naweza save aje na mshahara mdogo?"  # How can I save with a small salary?
        ],
        "responses": [
            "Jaribu 50/30/20 rule: 50% mahitaji (needs), 30% matakwa (wants), 20% savings. Unataka nikuwekee goal?",
            "Automate savings zako na M-Shwari au Equity’s Eazzy Banking. Unahitaji usaidizi wa ku-set up?",
            "Hata KSH 500 kwa mwezi inaweza kuwa mingi baadaye! Una goal gani ya savings?",
            "Ukikaa Nairobi, epuka kula nje kila siku—pika nyumbani. Unataka budget ya chakula?",
            "For HELB, weka aside angalau 10% kabla hujatumia—sawa?"
        ]
    },
    {
        "tag": "budgeting",
        "patterns": [
            "How do I create a budget?", "Nipangaje bajeti yangu?", "Give me budgeting advice.",
            "Best way to manage expenses?", "Naweza gavana aje pesa yangu kama student?",
            "How do I budget my salary in Nairobi?", "Naweza budget aje na HELB tu?",
            "What’s the best way to allocate income as a working Kenyan?"
        ],
        "responses": [
            "Kwa students: Tumia HELB kwa fees, rent, na uchukue kidogo kwa savings. Unataka breakdown?",
            "Kwa wafanyakazi: Jaribu 50/30/20—50% needs kama rent, 30% wants kama outings, 20% savings. Nishow example ya salary yako?",
            "Badala ya Uber, chukua matatu au SWVL—pesa itabaki kwa pocket. Unataka transport hacks zaidi?",
            "Panga pesa yako daily—KSH 200 kwa matatu, KSH 100 kwa lunch. Sawa?"
        ]
    },
    {
        "tag": "investments",
        "patterns": [
            "Where should I invest?", "Nipee mawazo ya investment Kenya.", "Best investments in Kenya?",
            "How can I grow my money?", "Naweza weka pesa wapi i-grow?",
            "Is crypto a good investment?", "Are SACCOs a good investment in Kenya?",
            "Je, Money Market Funds ni poa?"
        ],
        "responses": [
            "Government bonds za CBK ni salama—returns ziko around 10-14%. Unataka kujua jinsi ya kujiunga?",
            "SACCOs kama Stima SACCO au Harambee ni poa kwa dividends. Unahitaji list ya SACCOs za kuaminika?",
            "Badala ya crypto, jaribu Money Market Funds kama Sanlam au CIC—safe na zinagrow polepole. Unataka details?",
            "Real estate ni poa lakini inahitaji capital. Unaweza anza na chama—nishow how?"
        ]
    },
    {
        "tag": "savings_goal",
        "patterns": [
            "I want to set a savings goal", "Nisaidie kuweka savings goal", "Help me track my savings",
            "I need to save for something big", "Naokoa aje kwa project kubwa?",
            "How do I stay disciplined with savings?", "Nifanye nini nisitumie savings zangu?"
        ],
        "responses": [
            "Poa sana! Target yako ni nini? KSH 10,000 kwa sem au KSH 50,000 kwa mwaka? Tui-break down pamoja?",
            "Nikuwekee tracking plan? Unaweza report kila wiki au mwezi—unachagua!",
            "Discipline inakuja na kuweka pesa mahali ngumu kufikia kama M-Shwari locked account. Unajaribu?",
            "Anza na kidogo—KSH 200 daily hukufikisha KSH 6,000 kwa mwezi. Sawa?"
        ]
    },
    {
        "tag": "nairobi_life",
        "patterns": [
            "How do I survive in Nairobi?", "Naweza ishi aje Nairobi bila stress?",
            "Best places to live on a budget?", "How can I spend less in Nairobi?",
            "What’s the cost of living in Nairobi?", "Je, Nairobi ni ghali sana?",
            "Nifanye nini kupunguza gharama za maisha Nairobi?"
        ],
        "responses": [
            "Nairobi ni moto kidogo! Pika nyumbani badala ya kula nje—unaweza save hata KSH 2,000 kwa wiki. Unataka meal plan?",
            "Kaa Rongai, Githurai, Kasarani au Kayole—rent ni chini kuliko Westlands au CBD. Unahitaji options?",
            "Matatu na SWVL ni rahabu kuliko Uber kila siku. Unataka route za bei rahisi?",
            "Average cost Nairobi ni kama KSH 30,000-50,000 kwa mwezi kulingana na lifestyle. Budget yako iko wapi?"
        ]
    }
]
# Train AI Chatbot Model with 15 Iterations

def train_chatbot():
    nlp.initialize()
    for _ in range(15):
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
