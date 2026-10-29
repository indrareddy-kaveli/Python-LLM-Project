
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from llm_model.chatbot import generate_response
from llm_model.intent_detection import detect_intent
from llm_model.chat_repository import (
    create_session,
    save_message,
    get_chat_history,
    get_all_chats,
    get_chat_messages,
)

app = FastAPI(
    title="LLM ChatModel",
    description="A simple AI chatbot using Groq API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    intent: str
    response: str
    session_id: str


@app.get("/")
def home():
    return {"message": "Python LLM Chatbot API is running..."}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid4())

    # Create or reuse the database session.
    create_session(session_id)

    # Load existing conversation history.
    history = get_chat_history(session_id)

    intent = detect_intent(request.message)

    # Save the user's new message.
    save_message(session_id, "user", request.message)

    # Generate the AI response using previous history.
    answer = generate_response(
        request.message,
        history=history,
    )

    # Save the assistant's response.
    save_message(session_id, "assistant", answer)

    return ChatResponse(
        intent=intent,
        response=answer,
        session_id=session_id,
    )
    
@app.get("/chats")
def list_chats():
    return get_all_chats()


@app.get("/chats/{session_id}")
def read_chat(session_id: str):
    return {
        "session_id": session_id,
        "messages": get_chat_messages(session_id),
    }
