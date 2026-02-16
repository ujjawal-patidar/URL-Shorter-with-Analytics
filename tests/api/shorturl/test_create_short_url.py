# import pytest
# from app.models.shorturl import ShortURL

# pytestmark = pytest.mark.asyncio


async def test_create_short_link(auth_client, test_user):
    payload = {
        "original_url": "https://example.com",
    }

    response = await auth_client.post("/links/", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert data["original_url"] == "https://example.com"
    assert "short_code" in data
    assert data["is_active"] is True


async def test_get_all_links(auth_client, test_user):
    res = await auth_client.get("/")
    assert res.status_code == 200


async def test_delete_short_url(auth_client, test_user):
    payload = {
        "user_id": str(test_user["id"]),
        "original_url": "https://delete.com",
    }

    create_response = await auth_client.post("/links/", json=payload)
    short_code = create_response.json()["short_code"]

    delete_response = await auth_client.delete(f"/links/{short_code}")

    assert delete_response.status_code == 204


async def test_delete_not_found(auth_client):
    response = await auth_client.delete("/links/invalidcode/")

    assert response.status_code == 307
