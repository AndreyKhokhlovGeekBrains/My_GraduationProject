$(document).ready(function() {
    $('.image-container a').on('click', function(event) {
        event.preventDefault();
        var positionId = $(this).attr('href').split('=')[1];
        var amount = 1; // default amount is 1
        var url = '/cart/add/?position_id=' + positionId + '&amount=' + amount;

        $.ajax({
            type: 'POST',
            url: url,
            success: function(data) {
                console.log(data);
                // Обновляем корзину после успешного добавления
                updateCart().then(function() {
                    location.reload(); // Перезагрузка страницы после обновления корзины
                }).catch(function(error) {
                    console.error("Ошибка при обновлении корзины:", error);
                });
            },
            error: function(xhr, status, error) {
                console.error("Ошибка AJAX:", status, error);
            }
        });
    });
});

// Функция для обновления содержимого корзины
function updateCart() {
    return new Promise(function(resolve, reject) {
        $.ajax({
            type: 'GET',
            url: '/cart/get/',
            success: function(data) {
                $('#cart-items').html(data); // Обновляем содержимое элемента с ID cart
                resolve(); // Успешное обновление
            },
            error: function(xhr, status, error) {
                reject(error); // Ошибка при обновлении
            }
        });
    });
}