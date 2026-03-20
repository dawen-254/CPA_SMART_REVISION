import openai
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from .models import ChatSession, ChatMessage
from apps.content.models import Topic

@login_required
def chat_view(request, topic_id=None):
    """View to display the chat interface."""
    session_id = request.GET.get("session_id")
    # If topic_id is not passed in URL, check query params
    if not topic_id:
        topic_id = request.GET.get("topic_id")
    
    sessions = ChatSession.objects.filter(student=request.user)
    
    current_session = None
    chat_messages = []
    
    if session_id:
        current_session = get_object_or_404(ChatSession, id=session_id, student=request.user)
        chat_messages = current_session.messages.all()
    elif topic_id:
        # Check if an active session already exists for this topic
        topic = get_object_or_404(Topic, id=topic_id)
        current_session = ChatSession.objects.filter(student=request.user, topic=topic).first()
        if not current_session:
            # Create a new session for this topic
            current_session = ChatSession.objects.create(
                student=request.user, 
                topic=topic,
                title=f"Learning: {topic.title}"
            )
        chat_messages = current_session.messages.all()
    
    context = {
        "sessions": sessions,
        "current_session": current_session,
        "chat_messages": chat_messages,
        "topic_id": topic_id,
    }
    return render(request, "ai_tutor/chat.html", context)

@login_required
def send_message(request):
    """Handle sending a message to the AI tutor via AJAX."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)
        
    content = request.POST.get("content")
    session_id = request.POST.get("session_id")
    topic_id = request.POST.get("topic_id")
    
    if not content:
        return JsonResponse({"error": "Message content is required"}, status=400)
        
    # Get or create session
    if session_id:
        session = get_object_or_404(ChatSession, id=session_id, student=request.user)
    elif topic_id:
        topic = get_object_or_404(Topic, id=topic_id)
        session, created = ChatSession.objects.get_or_create(
            student=request.user, 
            topic=topic,
            defaults={'title': f"Learning: {topic.title}"}
        )
    else:
        # Create a new general session
        title = content[:50] + "..." if len(content) > 50 else content
        session = ChatSession.objects.create(student=request.user, title=title)
        
    # Save user message
    ChatMessage.objects.create(session=session, role="user", content=content)
    
    # Call AI
    ai_response = get_ai_response(session)
    
    # Save AI message
    ChatMessage.objects.create(session=session, role="assistant", content=ai_response)
    
    # Update session timestamp to move it to the top of the list
    session.save()
    
    return JsonResponse({
        "content": ai_response,
        "session_id": session.id,
        "topic_id": session.topic.id if session.topic else None
    })

def get_ai_response(session):
    """Helper function to call the AI provider and get a response."""
    system_prompt = "You are a helpful AI tutor for CPA (Certified Public Accountant) students. Answer their questions clearly and concisely."
    
    if session.topic:
        system_prompt += f"\n\nThe student is currently studying the topic: {session.topic.title}.\n"
        system_prompt += f"Context about this topic:\n{session.topic.content[:2000]}\n" # Limit context size
        system_prompt += "\nUse this context to provide specific and accurate answers related to this topic."

    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Add previous messages for context (limit to last 10 for tokens)
    previous_messages = session.messages.all().order_by('-timestamp')[:10]
    for msg in reversed(previous_messages):
        messages.append({"role": msg.role, "content": msg.content})
        
    try:
        if settings.AI_PROVIDER == "openai":
            if not settings.OPENAI_API_KEY:
                return "OpenAI API key is missing. Please contact the administrator."
                
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return response.choices[0].message.content
        elif settings.AI_PROVIDER == "anthropic":
            # Anthropic implementation if needed
            import anthropic
            if not settings.ANTHROPIC_API_KEY:
                return "Anthropic API key is missing. Please contact the administrator."
                
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            # Adjust messages for Anthropic format
            anthropic_messages = []
            for msg in messages:
                if msg["role"] != "system":
                    anthropic_messages.append({"role": msg["role"], "content": msg["content"]})
            
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                system=system_prompt,
                messages=anthropic_messages
            )
            return response.content[0].text
        elif settings.AI_PROVIDER == "gemini":
            import google.generativeai as genai
            if not settings.GEMINI_API_KEY:
                return "Gemini API key is missing. Please contact the administrator."
            
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(
                'gemini-flash-latest',
                system_instruction=system_prompt
            )
            
            # Prepare chat history for Gemini
            chat_history = []
            
            # Gemini likes the first message to be user, but we can prepend system info or use system_instruction
            # For simplicity with the existing 'messages' structure:
            gemini_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    continue # handled by model init if using system_instruction
                role = "user" if msg["role"] == "user" else "model"
                gemini_messages.append({"role": role, "parts": [msg["content"]]})
            
            # Use the last message as the prompt, and previous as history
            if not gemini_messages:
                return "No message content found."
                
            last_message = gemini_messages.pop()
            chat = model.start_chat(history=gemini_messages)
            response = chat.send_message(last_message["parts"][0])
            return response.text
    except Exception as e:
        return f"I'm sorry, I encountered an error: {str(e)}"
    
    return "AI provider not configured properly."

