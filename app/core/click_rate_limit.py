from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from functools import wraps
import uuid
from app.models.user import User
from app.core.utility import redis


def click_rate_limiter(max_clicks: int = 5, window: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            short_code = kwargs.get("short_code")

            if not request or not short_code:
                raise Exception("Request or short_code not found")

            # Getting if present(means old visitor) or create visitor_id (means new visitor)
            visitor_id = request.cookies.get("visitor_id")
            new_visitor = False
            if not visitor_id:
                visitor_id = str(uuid.uuid4())
                new_visitor = True

            # Redis key per visitor per short code
            key = f"clicks:{short_code}:{visitor_id}"

            # it will Increment click count atomically and return latest count
            current_clicks = await redis.incr(key)

            # If first click, set expiration
            if current_clicks == 1:
                await redis.expire(key, window)

            if current_clicks > max_clicks:
                raise HTTPException(
                    status_code=429, detail="Too many clicks. Please try again later."
                )

            # Call the actual redirect function
            response: RedirectResponse = await func(*args, **kwargs)

            # Set cookie if new visitor
            if new_visitor:
                response.set_cookie(
                    key="visitor_id",
                    value=visitor_id,
                    max_age=60 * 60 * 24 * 30,  # 1 month
                    httponly=True,
                    samesite="lax",
                )

            return response

        return wrapper

    return decorator


def create_rate_limiter(max_creation: int = 5, window: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            curr_user: User = kwargs.get("current_user")

            if not curr_user:
                raise Exception("Not authenticated")

            # Redis key per visitor per short code
            key = f"create:short_url:{curr_user.id}"

            # it will Increment click count atomically and return latest count
            current_created = await redis.incr(key)

            # If first click, set expiration
            if current_created == 1:
                await redis.expire(key, window)

            if current_created > max_creation:
                raise HTTPException(
                    status_code=429,
                    detail="Too many usrls created. Please try again after some time.",
                )

            # Call the actual redirect function
            response = await func(*args, **kwargs)
            return response

        return wrapper

    return decorator
