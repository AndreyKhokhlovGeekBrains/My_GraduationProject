import redis
import schedule
import time


"""
Создаем Redis клиент, хост - localhost,
порт  - 6379, это стандартный порт для Redis, мы указали его в docker-compose,
db - это номер базы данных, мы можем указать любой
"""

client = redis.Redis(host='localhost', port=6379, db=0)


def redis_backup():
    """
    Создаем бэкап
    """
    schedule.every(1).day.at("02:00").do(client.bgsave())

    while True:
        schedule.run_pending()
        time.sleep(1)


def redis_add_to_cart(user_id, position_id, amount):
    try:
        client.hincrby(user_id, position_id, amount=amount)
        return {"status": 200}
    except Exception as e:
        print(f"Error adding to cart: {e}")
        return {"status": 500, "msg": "Failed to add to cart"}


def redis_remove_from_cart(user_id, position_id, amount):
    try:
        if client.exists(user_id) and client.type(user_id) == b'hash':
            current_amount = client.hget(user_id, position_id)
            if current_amount is not None:
                new_amount = int(current_amount) - amount
                if new_amount <= 0:
                    client.hdel(user_id, position_id)
                else:
                    client.hincrby(user_id, position_id, amount=-amount)
            return {"status": 200}
        return {"status": 404, "msg": "Item not found in cart"}
    except Exception as e:
        print(f"Error removing from cart: {e}")
        return {"status": 500, "msg": "Failed to remove from cart"}


def redis_get_from_cart(user_id: int):
    try:
        if client.exists(str(user_id)) and client.type(str(user_id)) == b'hash':
            values = client.hgetall(str(user_id))
            # Decode both keys and values from bytes to strings
            decoded_values = {key.decode('utf-8'): value.decode('utf-8') for key, value in values.items()}
            return decoded_values
        return {}
    except Exception as e:
        print(f"Error retrieving cart: {e}")
        return {}


def redis_clear_cart(user_email):
    try:
        if client.exists(user_email):
            client.delete(user_email)
        return {"status": 200, "msg": "Cart cleared successfully"}
    except Exception as e:
        print(f"Error clearing cart: {e}")
        return {"status": 500, "msg": "Failed to clear cart"}


def get_unique_item(user_id):
    if client.exists(user_id):
        key_type = client.type(user_id)
        if key_type == b'hash':
            return client.hlen(user_id)
    return 0


def update_item_quantity_in_cart(user_id: int, item_id: int, quantity: int) -> bool:
    try:
        if quantity > 0:
            client.hset(str(user_id), str(item_id), str(quantity))
        else:
            client.hdel(str(user_id), str(item_id))  # Remove the item if quantity is less than or equal to 0
        return True
    except Exception as e:
        print(f"Error updating item quantity: {e}")
        return False




