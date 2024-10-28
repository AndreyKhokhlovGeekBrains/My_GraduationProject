document.querySelectorAll('.add-order').forEach(button => {
  button.addEventListener('click', function() {
    const itemId = this.getAttribute('data-item-id');
    const itemAmount = this.getAttribute('data-item-amount');
    const itemName = this.getAttribute('data-item-name');
    const itemPrice = this.getAttribute('data-item-price');
    const itemAbsolute_price = itemAmount * itemPrice; // Убедитесь, что вы используете itemPrice вместо price

    // Формируем URL
    const url = `/add-order/?item_id=${encodeURIComponent(itemId)}&amount=${encodeURIComponent(itemAmount)}&itemName=${encodeURIComponent(itemName)}&price=${encodeURIComponent(itemPrice)}&absolute_price=${encodeURIComponent(itemAbsolute_price)}`;

    // Вместо fetch используем просто перенаправление
    window.location.href = url; // Перенаправляем пользователя на страницу
  });
});