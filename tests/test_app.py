import os
import pytest
import pytest_asyncio
from datetime import date
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, delete
from app.models import users, products
from app.db import connect_db, disconnect_db, database
from app.main import app
from app.crud import get_item_id_by_title, add_item
from app.schemas import ItemIn

# Set the test database URL
os.environ["DATABASE_URL"] = "postgresql://postgres:68064911@localhost:5432/postgres"

TEST_ITEM_TITLE = "Test Item"
TEST_ITEM_ID = None


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    """Connect to and disconnect from the database asynchronously before and after tests."""
    await connect_db()
    yield
    await disconnect_db()


@pytest_asyncio.fixture(scope="session")
async def async_client():
    """Provide an asynchronous client for async tests using ASGI transport."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_homepage(async_client: AsyncClient):
    """Test homepage through making a request using the TestClient."""
    if not database.is_connected:
        await database.connect()
    response = await async_client.get("/")

    assert response.status_code == 200
    assert "Main page" in response.text
    await database.disconnect()


@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient):
    """Test creating a new user."""
    # Step 1: Prepare test data
    form_data = {
        "input-name": "Test User",
        "input-email": "testuser@example.com",
        "input-password": "TestPassword123",
        "input-birthdate": "2000-01-01",
        "input-phone": "+1234567890",
        "input-checkbox": "on"  # Agreement is checked
    }

    if not database.is_connected:
        await database.connect()

    # Step 2: Send POST request to the /form/ endpoint using AsyncClient
    response = await async_client.post("/form/", data=form_data, follow_redirects=False)

    assert response.status_code == 303, f"Unexpected status code: {response.status_code}. Response content: {response.text}"

    # Step 3: Connect to the database
    await database.connect()
    try:
        # Step 4: Query the database to verify that the user was added
        query = select(users).where(users.c.email == form_data["input-email"])
        user_record = await database.fetch_one(query)

        # Step 5: Validate that the user exists in the database and has correct attributes
        assert user_record is not None, "User was not added to the database"
        assert user_record["name"] == form_data["input-name"]
        assert user_record["email"] == form_data["input-email"]
        assert user_record["phone"] == form_data["input-phone"]
        assert user_record["agreement"] is True
        assert user_record["birthdate"] == date(2000, 1, 1)  # Convert to date object for comparison

        # Step 6: Clean up the database by deleting the test user
        delete_query = users.delete().where(users.c.email == form_data["input-email"])
        await database.execute(delete_query)
    finally:
        # Ensure the database connection is closed after the test
        await database.disconnect()

# *** *** ***


@pytest.mark.asyncio
async def test_create_item_and_get_id():
    """Test creating a new item and retrieving its ID from the database."""
    global TEST_ITEM_ID

    item_in = ItemIn(
        title=TEST_ITEM_TITLE,
        description="A test item description",
        quantity=10,
        price=20.00,
        discount=0.1,
        is_featured="Not Featured",
        gender_category="man",
        item_type_id=1,
        image_filename="1.svg"
    )
    if not database.is_connected:
        await database.connect()
    TEST_ITEM_ID = await add_item(item_in)

    assert TEST_ITEM_ID is not None, "Item was not added to the database"
    await database.disconnect()


@pytest.mark.asyncio
async def test_get_edit_item_form(async_client: AsyncClient):
    """Test getting the edit item form."""
    if not database.is_connected:
        await database.connect()
    try:
        # Step 1: Send GET request to fetch the edit form for the product
        response = await async_client.get(f"/edit-item/{TEST_ITEM_ID}")

        # Step 2: Check status code and HTML response content
        assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

        # Verify the title or specific text in the HTML to confirm correct template rendering
        assert TEST_ITEM_TITLE in response.text, "Expected form title not found in response text."
        assert f'value="Test Item"' in response.text, "Expected title not found"
        assert f'>A test item description<' in response.text, "Expected description not found"
        assert f'value="20.00"' in response.text, "Expected price not found"
    finally:
        await database.disconnect()


@pytest.mark.asyncio
async def test_edit_item(async_client: AsyncClient):
    """Test a product can be edited."""
    # Set up the product ID and mock data to edit the product
    form_data = {
        "title": "Test Item changed",
        "description": "A test item description changed",
        "price": 10.00,
        "discount": 0.5000,
        "quantity": 12,
        "is_featured": "Featured",
        "gender_category": "women",
        "item_type": "Bags",
        "status": "Deleted"
    }
    if not database.is_connected:
        await database.connect()
    try:
        # Send the POST request with form data
        response = await async_client.post(f"/edit-item/{TEST_ITEM_ID}", data=form_data)

        # Check if the status code is 303 (redirect) or 200 (page reload on error)
        assert response.status_code in [200, 303]

        if response.status_code == 303:
            # Check that the redirection location is as expected
            assert response.headers["Location"] == "/edit-request?success=true"
        else:
            # If 200 OK, print the HTML response text for debugging
            assert "Edit product request" in response.text
        select_query = select(products).where(products.c.id == TEST_ITEM_ID)
        result = await database.fetch_one(select_query)
        assert result["title"] == "Test Item changed", f'Title was not changed'
        assert result["description"] == "A test item description changed", f'Description was not changed'
        assert result["price"] == 10.00, f'Price was not changed'
        assert result["discount"] == 0.5000, f'Discount was not changed'
        assert result["quantity"] == 12, f'Quantity was not changed'
        assert result["is_featured"] == "Featured", f'Is_featured was not changed'
        assert result["gender_category"].value == "women", f'Gender was not changed'
        assert result["item_type_id"] == 2, f'Item type was not changed'
        assert result["status"] == "Deleted", f'Status was not changed'
    finally:
        await database.disconnect()


@pytest.mark.asyncio
async def test_edit_item_invalid_data(async_client: AsyncClient):
    """Test sending invalid data to edit-item form."""
    form_data = {
        "title": "Test Item changed",
        "description": "A test item description changed",
        "price": "invalid",  # Invalid price
        "quantity": 12,
        "gender_category": "invalid",  # Invalid gender category
    }
    if not database.is_connected:
        await database.connect()
    try:
        response = await async_client.post(f"/edit-item/{TEST_ITEM_ID}", data=form_data)
        assert response.status_code == 422
    finally:
        await database.disconnect()


@pytest.mark.asyncio
async def test_add_item_missing_data(async_client: AsyncClient):
    """Test sending invalid data to add-item form."""
    form_data = {
        "title": "New Item",
        # Missing description, price, etc.
    }
    if not database.is_connected:
        await database.connect()
    try:
        response = await async_client.post("/add-item", data=form_data)
        assert response.status_code in [400, 422]
    finally:
        await database.disconnect()


@pytest.mark.asyncio
async def test_delete_test_item():
    """Test deletion of the test item."""
    if not database.is_connected:
        await database.connect()
    try:
        delete_query = delete(products).where(products.c.id == TEST_ITEM_ID)
        await database.execute(delete_query)
        select_query = select(products).where(products.c.id == TEST_ITEM_ID)
        result = await database.fetch_one(select_query)

        # Assert that the item is indeed deleted (should return None)
        assert result is None, f"Item with ID {TEST_ITEM_ID} was not deleted from the database."
    finally:
        await database.disconnect()


@pytest.mark.asyncio
async def test_search_valid_query(async_client: AsyncClient):
    """Test searching for an item with a valid query."""
    query = "New Item"
    if not database.is_connected:
        await database.connect()
    response = await async_client.get(f"/search?query={query}")
    assert response.status_code == 200
    assert "New Item" in response.text
    await database.disconnect()


@pytest.mark.asyncio
async def test_search_empty_query(async_client: AsyncClient):
    """Test searching with an empty query, expecting 'No items found' message."""
    if not database.is_connected:
        await database.connect()
    response = await async_client.get("/search?query=")
    assert response.status_code == 200
    assert "No items found" in response.text
    await database.disconnect()


if __name__ == '__main__':
    pytest.main(['-vv'])
