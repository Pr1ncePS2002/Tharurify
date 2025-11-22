from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.services import rag_service, resume_parser
from app.utils import bot_utils
from app.auth.auth_utils import get_current_user
from app.database.models import User

router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str
    role: Optional[str] = None
    skills: Optional[List[str]] = None
    user_id: Optional[int] = None
    entire_data: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str

@router.post("/chat/speech", response_model=ChatResponse)
def handle_speech_chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Endpoint for the speech feedback chat bot."""
    if req.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    
    response = bot_utils.chat_with_speech_bot(req.prompt, req.user_id)
    return ChatResponse(response=response)

@router.post("/chat/interview-qna", response_model=ChatResponse)
def handle_interview_qna_chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Endpoint for the interview Q&A bot."""
    if req.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="User ID mismatch")

    response = bot_utils.chat_with_interview_bot(req.prompt, req.role, req.skills, req.user_id)
    return ChatResponse(response=response)

@router.post("/chat/mock-interview", response_model=ChatResponse)
def handle_mock_interview_chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Endpoint for the mock interviewer bot."""
    if req.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="User ID mismatch")

    response = bot_utils.chat_with_interviewer(req.prompt, req.entire_data, req.user_id)
    return ChatResponse(response=response)
