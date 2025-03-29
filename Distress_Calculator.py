import numpy as np
from Sentiment_analysis import SentimentAnalyzer  # Fixed import

def calculate_word_choice_score(text):
    """Calculate distress score based on word choices"""
    distress_words = ['pain', 'help', 'scared', 'afraid']  # Add your keywords
    words = text.lower().split()
    return sum(1 for word in words if word in distress_words) / len(words) if words else 0

def calculate_context_score(text):
    """Calculate context score based on punctuation and length"""
    score = 0
    if '!' in text: score += 0.3
    if '?' in text: score += 0.2
    if len(text.split()) > 10: score += 0.1
    return min(score, 1.0)

def Calc_Panic_Prob(model, text=""):
    """Calculate panic probability"""
    if not text:
        return 0.0
    
    analyzer = SentimentAnalyzer(text)
    result, polarity = analyzer.analyze_sentiment()
    
    # Get vital signs - you'll need to implement this
    heart_rate = 85  # Example - replace with actual measurement
    blood_pressure = 120  # Example
    
    # Make prediction
    sample = np.array([[heart_rate, blood_pressure, polarity]])
    prediction = model.predict(sample)
    
    return float(prediction[0][0])