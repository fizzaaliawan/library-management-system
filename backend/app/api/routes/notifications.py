import asyncio
import json
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from app.core.config import settings
import redis.asyncio as aioredis

router = APIRouter()

@router.get("/stream")
async def stream_notifications(request: Request):
    """
    """
    async def event_generator():
        # Setup async redis connection
        r_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        pubsub = r_client.pubsub()
        await pubsub.subscribe("notifications")
        
        try:
            # Yield a welcome event on connection
            yield {
                "event": "info",
                "data": json.dumps({"status": "connected", "message": "Connected to LMS notification stream"})
            }
            
            while True:
                # Check for client disconnection
                if await request.is_disconnected():
                    break
                
                # Check for new messages from Redis pubsub channel
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    yield {
                        "event": "message",
                        "data": message["data"]
                    }
                
                # Yield a heart beat to keep connection alive
                await asyncio.sleep(0.5)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            # Yield error event
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
        finally:
            await pubsub.unsubscribe("notifications")
            await pubsub.close()
            await r_client.close()
            
    return EventSourceResponse(event_generator())
