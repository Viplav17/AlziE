import nltk
nltk.download('stopwords')
nltk.download('punkt')
import spacy
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from spacytextblob.spacytextblob import SpacyTextBlob

s = PorterStemmer()
l = WordNetLemmatizer()
nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("spacytextblob")

HARMFUL_PHRASES = {
    "kill yourself": {"polarity": -1.0, "sentiment": "Emergency Negative"},
    "self harm": {"polarity": -1.0, "sentiment": "Emergency Negative"},
    "i hate you": {"polarity": -1.0, "sentiment": "Emergency Negative"},
    "i don't know who": {"polarity": -0.9, "sentiment": "Distressed User"},
    "i don't know where": {"polarity": -0.9, "sentiment": "Distressed User"},
    "don't remember": {"polarity": -0.9, "sentiment": "Distressed User"},
}

class SentimentAnalyzer:
    def __init__(self, text):
        self.text = text
        self.lemmatized = None
        self.filtered_text = None
        
    def lemmatize(self):
        doc = nlp(self.text)
        lemmas = [token.lemma_ for token in doc]
        self.lemmatized = ' '.join(lemmas)
        return self.lemmatized
    
    def remove_stopwords(self):
        if not self.lemmatized:
            self.lemmatize()
            
        stop_words = set(stopwords.words("english"))
        word_tokens = word_tokenize(self.lemmatized)
        filtered_words = [word for word in word_tokens if word not in stop_words]
        self.filtered_text = ' '.join(filtered_words)
        return self.filtered_text
    
    def analyze_sentiment(self):
        # First check for harmful phrases
        lower_text = self.text.lower()
        for phrase, data in HARMFUL_PHRASES.items():
            if phrase in lower_text:
                # Return complete result including processed text
                return {
                    'original_text': self.text,
                    'processed_text': self.text,  # Using original as processed for harmful phrases
                    'polarity': data['polarity'],
                    'sentiment': data['sentiment']
                }
        
        # Normal processing for non-harmful phrases
        if not self.filtered_text:
            self.remove_stopwords()
            
        doc = nlp(self.filtered_text)
        polarity = doc._.blob.polarity
        
        if polarity > 0.2:
            sentiment = "Positive"
        elif polarity < -0.1:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
            
        return {
            'original_text': self.text,
            'processed_text': self.filtered_text,
            'polarity': polarity,
            'sentiment': sentiment
        }

def analyze_text(text):
    analyzer = SentimentAnalyzer(text)
    return analyzer.analyze_sentiment()

if __name__ == "__main__":
    from Speech_Recognition import recognize_speech
    
    speech_text = recognize_speech()  
    if speech_text:
        result = analyze_text(speech_text)
        
        print(f"\nOriginal Text: {result['original_text']}")
        print(f"Processed Text: {result['processed_text']}")
        print(f"Sentiment: {result['sentiment']} (Polarity: {result['polarity']:.2f})")
        
        if result['sentiment'] == "Emergency Negative":
            print("\n⚠️ WARNING: Harmful content detected! Please seek help if needed. ⚠️")
    else:
        print("No speech detected")