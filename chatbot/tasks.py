from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import FAQ, DiseasePrediction
from .services import ChatbotService, DiseasePredictionService
import tensorflow as tf
import numpy as np
import json
import os

@shared_task
def train_chatbot_model():
    """Train the chatbot model with updated FAQ data"""
    try:
        # Load and preprocess FAQ data
        faqs = FAQ.objects.all()
        questions = [faq.question for faq in faqs]
        answers = [faq.answer for faq in faqs]

        # Initialize chatbot service
        chatbot_service = ChatbotService()
        
        # Train the model
        chatbot_service.model.fit(
            chatbot_service.tokenizer.texts_to_sequences(questions),
            chatbot_service.tokenizer.texts_to_sequences(answers),
            epochs=10,
            batch_size=32
        )

        # Save the trained model
        model_path = os.path.join(settings.BASE_DIR, 'chatbot', 'models', 'chatbot_model.h5')
        chatbot_service.model.save(model_path)

        return "Chatbot model training completed successfully"
    except Exception as e:
        return f"Error training chatbot model: {str(e)}"

@shared_task
def train_disease_prediction_model():
    """Train the disease prediction model with updated data"""
    try:
        # Load and preprocess training data
        predictions = DiseasePrediction.objects.all()
        symptoms = [pred.symptoms for pred in predictions]
        diseases = [pred.predicted_disease for pred in predictions]

        # Initialize prediction service
        prediction_service = DiseasePredictionService()
        
        # Train the model
        prediction_service.model.fit(
            np.array([prediction_service._preprocess_symptoms(s) for s in symptoms]),
            np.array([prediction_service.symptom_encoder.get(d, 0) for d in diseases]),
            epochs=20,
            batch_size=32
        )

        # Save the trained model
        model_path = os.path.join(settings.BASE_DIR, 'chatbot', 'models', 'disease_prediction_model.h5')
        prediction_service.model.save(model_path)

        return "Disease prediction model training completed successfully"
    except Exception as e:
        return f"Error training disease prediction model: {str(e)}"

@shared_task
def send_appointment_reminder(appointment_id):
    """Send appointment reminder email"""
    from healthcare.models import Appointment
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        subject = f'Appointment Reminder: {appointment.doctor.user.get_full_name()}'
        message = f"""
        Dear {appointment.patient.get_full_name()},
        
        This is a reminder for your appointment with Dr. {appointment.doctor.user.get_full_name()}
        at {appointment.facility.name} on {appointment.date} at {appointment.time}.
        
        Reason for appointment: {appointment.reason}
        
        Please arrive 15 minutes before your scheduled time.
        
        Best regards,
        Healthcare Bot Team
        """
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [appointment.patient.email],
            fail_silently=False,
        )
        
        return f"Appointment reminder sent to {appointment.patient.email}"
    except Exception as e:
        return f"Error sending appointment reminder: {str(e)}"

@shared_task
def update_facility_ratings():
    """Update healthcare facility ratings based on reviews"""
    from healthcare.models import HealthcareFacility, Review
    
    try:
        facilities = HealthcareFacility.objects.all()
        for facility in facilities:
            reviews = Review.objects.filter(facility=facility)
            if reviews.exists():
                avg_rating = reviews.aggregate(avg_rating=models.Avg('rating'))['avg_rating']
                facility.rating = avg_rating
                facility.review_count = reviews.count()
                facility.save()
        
        return "Facility ratings updated successfully"
    except Exception as e:
        return f"Error updating facility ratings: {str(e)}"

@shared_task
def update_doctor_ratings():
    """Update doctor ratings based on reviews"""
    from healthcare.models import Doctor, Review
    
    try:
        doctors = Doctor.objects.all()
        for doctor in doctors:
            reviews = Review.objects.filter(doctor=doctor)
            if reviews.exists():
                avg_rating = reviews.aggregate(avg_rating=models.Avg('rating'))['avg_rating']
                doctor.rating = avg_rating
                doctor.review_count = reviews.count()
                doctor.save()
        
        return "Doctor ratings updated successfully"
    except Exception as e:
        return f"Error updating doctor ratings: {str(e)}" 