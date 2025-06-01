import pytest
from httpx import AsyncClient
from uuid import uuid4
from sqlalchemy import text

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

async def test_create_movie(client: AsyncClient, auth_headers: dict, test_movie_data: dict):
    response = await client.post(
        "/movies/movies",
        json=test_movie_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == test_movie_data["title"]
    assert "id" in data

async def test_get_movie(client: AsyncClient, auth_headers: dict, test_movie_data: dict):
    create_response = await client.post(
        "/movies/movies",
        json=test_movie_data,
        headers=auth_headers
    )
    movie_id = create_response.json()["id"]
    
    response = await client.get(f"/movies/movie?movie_id={movie_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == test_movie_data["title"]

async def test_list_movies(client: AsyncClient, auth_headers: dict):
    response = await client.get("/movies/movies", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

async def test_movies_lookup(client: AsyncClient, auth_headers: dict):
    response = await client.get("/movies/movies/lookup", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

async def test_recommend_movies(client: AsyncClient, auth_headers: dict, test_movie_data: dict):
    create_response = await client.post(
        "/movies/movies",
        json=test_movie_data,
        headers=auth_headers
    )
    movie_id = create_response.json()["id"]
    
    response = await client.post(
        "/movies/recommend",
        json={"liked_movie_ids": [movie_id]},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

async def test_update_movie(client: AsyncClient, auth_headers: dict, test_movie_data: dict):
    create_response = await client.post(
        "/movies/movies",
        json=test_movie_data,
        headers=auth_headers
    )
    movie_id = create_response.json()["id"]
    
    update_data = {"title": "Updated Title"}
    response = await client.patch(
        f"/movies/movies/{movie_id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 404

async def test_delete_movie(client: AsyncClient, auth_headers: dict, test_movie_data: dict):
    create_response = await client.post(
        "/movies/movies",
        json=test_movie_data,
        headers=auth_headers
    )
    movie_id = create_response.json()["id"]
    
    response = await client.delete(
        f"/movies/movies/{movie_id}",
        headers=auth_headers
    )
    assert response.status_code == 404
    
    get_response = await client.get(
        f"/movies/movie?movie_id={movie_id}",
        headers=auth_headers
    )
    assert get_response.status_code == 200 