from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ChatSession, Message
from .serializers import ChatSessionSerializer, MessageSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .predict import predict_disease, normalize_input, DISEASE_ADVICE
import unicodedata
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import openai

OPENAI_API_KEY = "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"  # Đặt key thật vào biến môi trường hoặc settings

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)]) 

FAQ = {
    "xin chào": "Chào bạn! Tôi có thể giúp gì cho bạn?",
    "bạn là ai": "Tôi là chatbot hỗ trợ y tế.",
    "làm sao để đặt lịch khám": "Bạn có thể vào mục Đặt lịch để chọn bác sĩ và thời gian phù hợp.",
    # ... (các mục FAQ khác như bản cũ của bạn)
}

def ask_gpt(message):
    import openai
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Bạn là trợ lý AI, trả lời mọi câu hỏi của người dùng một cách tự nhiên, thân thiện, dễ hiểu."},
            {"role": "user", "content": message}
        ],
        max_tokens=300,
        temperature=0.7,
    )
    return response.choices[0].message.content

class ChatAPIView(APIView):
    def post(self, request):
        user_message = request.data.get("message", "").strip().lower()
        user_message_no_accents = normalize_input(user_message)

        # 0. Nhận diện ý định xin lời khuyên linh hoạt
        advice_keywords = [
            "nen lam gi", "toi nen lam gi", "phai lam sao", "lam gi bay gio", "nen lam sao", "toi phai lam gi", "toi lam gi bay gio", "nen lam gi tiep theo", "nen lam gi luc nay", "nen lam gi hien tai"
        ]
        for kw in advice_keywords:
            if kw in user_message_no_accents:
                return Response({
                    "reply": "Nếu bạn cảm thấy không khỏe hoặc có triệu chứng bất thường, bạn nên đi khám bác sĩ để được tư vấn và điều trị kịp thời. Ngoài ra, hãy nghỉ ngơi, uống đủ nước và theo dõi sức khỏe của mình."
                })

        # 1. Tra cứu Q&A
        for key in FAQ:
            key_no_accents = normalize_input(key)
            if key_no_accents in user_message_no_accents:
                return Response({"reply": FAQ[key]})
        
        # 2. Nếu là câu hỏi về triệu chứng, gọi AI
        prediction = predict_disease(user_message)
        if prediction != "Không xác định bệnh":
            return Response({"reply": prediction})
        
        # 3. Nếu không khớp gì, hỏi GPT
        try:
            gpt_reply = ask_gpt(user_message)
            return Response({"reply": gpt_reply})
        except Exception as e:
            print("OpenAI error:", e)
            return Response({"reply": "Xin lỗi, tôi chưa thể trả lời câu hỏi này ngay bây giờ."})

class ChatSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        chat_session = self.get_object()
        content = request.data.get('content')
        
        if not content:
            return Response(
                {'error': 'Message content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save user message
        user_message = Message.objects.create(
            session=chat_session,
            sender='USER',
            content=content
        )

        # TODO: Process the message with your chatbot logic here
        bot_response = "This is a placeholder response. Implement your chatbot logic."

        # Save bot response
        bot_message = Message.objects.create(
            session=chat_session,
            sender='BOT',
            content=bot_response
        )

        return Response({
            'user_message': MessageSerializer(user_message).data,
            'bot_message': MessageSerializer(bot_message).data
        })
