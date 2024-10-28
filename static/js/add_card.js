document.getElementById('card-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Предотвращаем стандартное поведение формы

    // Собираем данные из формы
    const cardData = {
        card_owner: document.getElementById('card_owner').value,
        card_number: document.getElementById('card_number').value,
        expiry_date: document.getElementById('expiry_date').value,
        cvv: document.getElementById('cvv').value
    };

    // Отправляем POST-запрос
    fetch('/add-card/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json' // Указываем, что отправляем JSON
        },
        body: JSON.stringify(cardData) // Преобразуем объект в JSON
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Сеть ответила с ошибкой: ' + response.status);
        }
        return response.json(); // Преобразуем ответ в JSON
    })
    .then(data => {
        console.log('Успех:', data); // Обрабатываем успешный ответ
        // Проверяем, если ответ успешный, показываем toast
        if (data.success) {
            showToast();
        }
    })
    .catch((error) => {
        console.error('Ошибка:', error); // Обрабатываем ошибку
    });
});

// Function to display the toast message
function showToast() {
    const toast = document.getElementById("toast");
    toast.className = "toast-message show";
    setTimeout(() => {
        toast.className = toast.className.replace("show", "");
    }, 3000);
}

// Check for the 'success' parameter in the URL
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('success') === 'true') {
    showToast();
}