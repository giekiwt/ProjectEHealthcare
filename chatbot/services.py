import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from .models import FAQ
import os
from django.conf import settings

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

class ChatbotService:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.tokenizer = Tokenizer()
        self.model = self._load_chatbot_model()
        self._prepare_tokenizer()

    def _load_chatbot_model(self):
        model_path = os.path.join(settings.BASE_DIR, 'chatbot', 'models', 'chatbot_model.h5')
        if os.path.exists(model_path):
            return load_model(model_path)
        return self._create_chatbot_model()

    def _create_chatbot_model(self):
        # Create a simple model for demonstration
        model = tf.keras.Sequential([
            tf.keras.layers.Embedding(10000, 64),
            tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64)),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(10000, activation='softmax')
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model

    def _prepare_tokenizer(self):
        # Load FAQ data and fit tokenizer
        faqs = FAQ.objects.all()
        texts = [faq.question for faq in faqs]
        self.tokenizer.fit_on_texts(texts)

    def _preprocess_text(self, text):
        # Convert to lowercase
        text = text.lower()
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(text)
        filtered_text = [w for w in word_tokens if not w in stop_words]
        return ' '.join(filtered_text)

    def _get_similar_faq(self, question):
        # Preprocess the question
        processed_question = self._preprocess_text(question)
        
        # Get all FAQs
        faqs = FAQ.objects.all()
        best_match = None
        best_score = 0
        
        # Simple similarity check (can be improved with more sophisticated methods)
        for faq in faqs:
            processed_faq = self._preprocess_text(faq.question)
            similarity = self._calculate_similarity(processed_question, processed_faq)
            if similarity > best_score:
                best_score = similarity
                best_match = faq
        
        return best_match if best_score > 0.5 else None

    def _calculate_similarity(self, text1, text2):
        # Simple cosine similarity implementation
        doc1 = self.nlp(text1)
        doc2 = self.nlp(text2)
        return doc1.similarity(doc2)

    def get_response(self, question):
        # First try to find a matching FAQ
        matching_faq = self._get_similar_faq(question)
        if matching_faq:
            return matching_faq.answer
        
        # If no FAQ match, generate a response using the model
        processed_question = self._preprocess_text(question)
        sequence = self.tokenizer.texts_to_sequences([processed_question])
        padded_sequence = pad_sequences(sequence, maxlen=100)
        
        # Get model prediction
        prediction = self.model.predict(padded_sequence)
        predicted_index = np.argmax(prediction[0])
        
        # For demonstration, return a generic response
        return "I understand you're asking about a medical concern. While I can provide general information, please consult a healthcare professional for specific medical advice."

class DiseasePredictionService:
    def __init__(self):
        self.model = self._load_prediction_model()
        self.symptom_encoder = self._load_symptom_encoder()

    def _load_prediction_model(self):
        model_path = os.path.join(settings.BASE_DIR, 'chatbot', 'models', 'disease_prediction_model.h5')
        if os.path.exists(model_path):
            return load_model(model_path)
        return self._create_prediction_model()

    def _create_prediction_model(self):
        # Create a simple CNN model for demonstration
        model = tf.keras.Sequential([
            tf.keras.layers.Conv1D(64, 3, activation='relu', input_shape=(100, 1)),
            tf.keras.layers.MaxPooling1D(2),
            tf.keras.layers.Conv1D(128, 3, activation='relu'),
            tf.keras.layers.MaxPooling1D(2),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(10, activation='softmax')  # 10 disease classes for demonstration
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model

    def _load_symptom_encoder(self):
        # Load or create symptom encoder
        encoder_path = os.path.join(settings.BASE_DIR, 'chatbot', 'models', 'symptom_encoder.pkl')
        if os.path.exists(encoder_path):
            import pickle
            with open(encoder_path, 'rb') as f:
                return pickle.load(f)
        return self._create_symptom_encoder()

    def _create_symptom_encoder(self):
        # Create a simple symptom encoder for demonstration
        symptoms = [
            'fever', 'cough', 'headache', 'fatigue', 'nausea',
            'vomiting', 'diarrhea', 'rash', 'pain', 'swelling'
        ]
        return {symptom: i for i, symptom in enumerate(symptoms)}

    def _preprocess_symptoms(self, symptoms_text):
        # Convert symptoms text to encoded format
        symptoms = symptoms_text.lower().split(',')
        encoded = np.zeros(len(self.symptom_encoder))
        for symptom in symptoms:
            symptom = symptom.strip()
            if symptom in self.symptom_encoder:
                encoded[self.symptom_encoder[symptom]] = 1
        return encoded.reshape(1, -1, 1)

    def predict_disease(self, symptoms_text):
        # Preprocess symptoms
        processed_symptoms = self._preprocess_symptoms(symptoms_text)
        
        # Get model prediction
        prediction = self.model.predict(processed_symptoms)
        predicted_class = np.argmax(prediction[0])
        confidence = float(prediction[0][predicted_class])
        
        # Map predicted class to disease name (for demonstration)
        diseases = [
            'Common Cold', 'Flu', 'Allergy', 'Food Poisoning',
            'Migraine', 'Arthritis', 'Diabetes', 'Hypertension',
            'Asthma', 'Anemia'
        ]
        
        return {
            'disease': diseases[predicted_class],
            'confidence': confidence
        } 