from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.model import LLMService

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    reply = LLMService.complete(req.messages, temperature=req.temperature, max_tokens=req.max_tokens)
    return ChatResponse(reply=reply, model="auto", provider=LLMService.provider)

@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    def token_gen():
        for chunk in LLMService.stream(req.messages, temperature=req.temperature, max_tokens=req.max_tokens):
            yield chunk
    return StreamingResponse(token_gen(), media_type="text/plain")

@router.websocket("/ws/chat")
async def ws_chat(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            payload = await ws.receive_json()
            messages = payload.get("messages", [])
            for chunk in LLMService.stream(messages):
                await ws.send_text(chunk)
            await ws.send_text("[END]")
    except WebSocketDisconnect:
        pass