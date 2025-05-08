# AI Healthcare Bot

A comprehensive healthcare chatbot system that provides medical assistance, doctor/clinic location services, and disease risk prediction.

## Features

### User Module
- User registration and authentication
- Personal profile management
- AI-powered medical chatbot
- Healthcare facility locator using Google Places API
- Disease risk prediction using CNN

### Admin Module
- User management
- Content management for chatbot knowledge base
- System monitoring and statistics
- AI model training and management

## Technology Stack

### Backend
- Python 3.x
- Django 4.2
- Django REST Framework
- TensorFlow/Keras for AI models
- spaCy/NLTK for NLP
- MySQL/MariaDB
- Redis for caching
- Celery for background tasks

### Frontend
- HTML5/CSS3/JavaScript
- Bootstrap/Material-UI
- Google Maps JavaScript API

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in required environment variables
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
ai_healthcare_bot/
├── core/                 # Core project settings and configurations
├── users/               # User management app
├── chatbot/            # Chatbot functionality
├── healthcare/         # Healthcare services (facility locator, risk prediction)
├── static/             # Static files
└── templates/          # HTML templates
```

## Security Considerations

- All sensitive data is encrypted
- HTTPS/TLS enforced
- CSRF protection enabled
- Input validation implemented
- Regular security updates

## License

This project is licensed under the MIT License - see the LICENSE file for details. # EHealthcareUTH
