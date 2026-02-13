import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status
from app.models.shorturl import ShortURL

pytestmark = pytest.mark.asyncio


async def test_redirect_to_original_url(auth_client, db_session, test_user):
    # Create a short URL
    short_url = ShortURL(
        user_id=test_user["id"],
        original_url="https://example.com",
        short_code="abc123",
        is_active=True,
    )
    db_session.add(short_url)
    await db_session.commit()
    await db_session.refresh(short_url)

    # Patch save_analytics so it will not execute
    with patch("app.api.routes.redirect.save_analytics", new_callable=AsyncMock):
        response = await auth_client.get(f"/{short_url.short_code}", follow_redirects=False)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers["location"] == short_url.original_url
