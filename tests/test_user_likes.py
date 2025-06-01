import pytest
from httpx import AsyncClient
from uuid import uuid4

@pytest.fixture
def test_movie_data():
    return {
        "title": "Test Movie",
        "description": "A test movie description",
        "genres": ["Action", "Drama"],
        "tags": ["test", "movie"],
        "release_year": 2024,
        "director": "Test Director",
        "actors": ["Actor 1", "Actor 2"]
    }

async def test_like_movie(client: AsyncClient, auth_headers: dict, test_movie_data: dict, test_user: dict):
    create_response = await client.post(
        "/movies/movies",
        json=test_movie_data,
        headers=auth_headers
    )
    movie_id = create_response.json()["id"]
    
    response = await client.post(
        f"/users/{test_user['id']}/likes?movie_id={movie_id}",
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Movie liked"

async def test_unlike_movie(client: AsyncClient, auth_headers: dict, test_movie_data: dict, test_user: dict):
    create_response = await client.post(
        "/movies/movies",
        json=test_movie_data,
        headers=auth_headers
    )
    movie_id = create_response.json()["id"]
    
    await client.post(
        f"/users/{test_user['id']}/likes?movie_id={movie_id}",
        headers=auth_headers
    )
    
    response = await client.delete(
        f"/users/{test_user['id']}/likes/{movie_id}",
        headers=auth_headers
    )
    assert response.status_code == 204

async def test_get_liked_movies(client: AsyncClient, auth_headers: dict, test_movie_data: dict, test_user: dict):
    create_response = await client.post(
        "/movies/movies",
        json=test_movie_data,
        headers=auth_headers
    )
    movie_id = create_response.json()["id"]
    
    await client.post(
        f"/users/{test_user['id']}/likes?movie_id={movie_id}",
        headers=auth_headers
    )
    
    response = await client.get(
        f"/users/{test_user['id']}/likes",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert str(movie_id) in [str(mid) for mid in data]

async def test_like_nonexistent_movie(client: AsyncClient, auth_headers: dict, test_user: dict):
    response = await client.post(
        f"/users/{test_user['id']}/likes?movie_id=00000000-0000-0000-0000-000000000000",
        headers=auth_headers
    )
    assert response.status_code == 404

async def test_unlike_nonexistent_movie(client: AsyncClient, auth_headers: dict, test_user: dict):
    response = await client.delete(
        f"/users/{test_user['id']}/likes/00000000-0000-0000-0000-000000000000",
        headers=auth_headers
    )
    assert response.status_code == 404 