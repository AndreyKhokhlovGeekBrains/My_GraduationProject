import os
import pytest
from fastapi.testclient import TestClient
from app.db import connect_db, disconnect_db
from app.main import app

# Set the test database URL before importing the app
os.environ["DATABASE_URL"] = "postgresql://postgres:68064911@localhost:5432/postgres"


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    # Asynchronously connect to the database before tests
    await connect_db()
    yield
    # Asynchronously disconnect from the database after tests
    await disconnect_db()


@pytest.fixture(scope="module")
def client():
    # Use the app directly with TestClient
    with TestClient(app) as client:
        yield client


@pytest.mark.asyncio
async def test_homepage(client):
    # Make a request using the TestClient
    response = client.get("/")
    assert response.status_code == 200
    assert "Main page" in response.text


@pytest.mark.asyncio
async def test_get_edit_item_form(client):
    # Step 1: Set up the product ID to request
    product_id = 9

    # Step 2: Send GET request to fetch the edit form for the product
    response = client.get(f"/edit-item/{product_id}")

    # Step 3: Check status code and HTML response content
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    # Verify the title or specific text in the HTML to confirm correct template rendering
    assert "Edit product form" in response.text, "Expected form title not found in response text."
    assert f'value="New Item"' in response.text, "Expected title not found"
    assert f'>A new item description<' in response.text, "Expected description not found"
    assert f'value="15.00"' in response.text, "Expected price not found"


@pytest.mark.asyncio
async def test_edit_item(client):
    # Set up the product ID and mock data to edit the product
    product_id = 1
    form_data = {
        "title": "Item 1",
        "description": "Some text changed",
        "price": "10.00",
        "discount": "0.1000",
        "quantity": "12",
        "is_featured": "Not Featured",
        "gender_category": "man",
        "item_type": "Accessories",
        "status": "Active"
    }

    # Send the POST request with form data
    response = client.post(f"/edit-item/{product_id}", data=form_data)

    # Print response status code and text for debugging
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)

    # Check if the status code is 303 (redirect) or 200 (page reload on error)
    assert response.status_code in [200, 303]

    if response.status_code == 303:
        # Check that the redirection location is as expected
        assert response.headers["Location"] == "/edit-request?success=true"
    else:
        # If 200 OK, print the HTML response text for debugging
        print("Response Text:", response.text)
        assert "Edit product request" in response.text


@pytest.mark.asyncio
async def test_edit_item_invalid_data(client):
    product_id = 1
    form_data = {
        "title": "Item 1",
        "description": "Some text changed",
        "price": "invalid",  # Invalid price
        "quantity": "12",
        "gender_category": "invalid",  # Invalid gender category
    }
    response = client.post(f"/edit-item/{product_id}", data=form_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_item_valid_data(client):
    form_data = {
        "title": "New Item",
        "description": "A new item description",
        "quantity": "5",
        "price": "15.00",
        "is_featured": "Not Featured",
        "gender_category": "man",
        "item_type": "Accessories",
        "status": "Active"
    }
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../static/img/featured_items/3.svg"))
    # Use `files` for the image upload
    files = {
        "image": ("3.svg", open(path, "rb"), "image/svg+xml")
    }

    response = client.post("/add-item", data=form_data, files=files)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_item_missing_data(client):
    form_data = {
        "title": "New Item",
        # Missing description, price, etc.
    }
    response = client.post("/add-item", data=form_data)
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_search_valid_query(client):
    query = "New Item"
    response = client.get(f"/search?query={query}")
    assert response.status_code == 200
    assert "New Item" in response.text


@pytest.mark.asyncio
async def test_search_empty_query(client):
    response = client.get("/search?query=")
    assert response.status_code == 200
    assert "No items found" in response.text  # Adjust based on expected behavior

if __name__ == '__main__':
    pytest.main(['-vv'])

# pytest .\tests\test_app.py -vv
