function showToast() {
    const toast = document.getElementById("toast");
    toast.className = "toast-message show";
    setTimeout(() => {
        toast.className = toast.className.replace("show", "");
    }, 3000);
}

// Проверяем наличие состояния в localStorage и показываем тост, если оно есть
window.onload = function() {
    if (localStorage.getItem('toastVisible') === 'true') {
        showToast();
        localStorage.removeItem('toastVisible'); // Удаляем состояние после показа
    }
};

document.querySelectorAll(".delete-item").forEach(button => {
    button.addEventListener("click", async function(event) {
        event.preventDefault(); // Предотвращаем стандартное поведение кнопки

        const itemId = this.getAttribute("data-item-id"); // Получаем ID товара

        try {
            const response = await fetch(`/cart/delete/?position_id=${itemId}&amount=1`, {
                method: "POST", // Используем метод POST
                headers: {
                    'Content-Type': 'application/json', // Устанавливаем заголовок для JSON
                    'Accept': 'application/json' // Устанавливаем заголовок для принятия JSON
                }
            });

            if (response.ok) {
                const result = await response.json(); // Получаем JSON ответ
                console.log("Response:", result); // Выводим ответ в консоль

                if (result.success) { // Проверяем статус
                    localStorage.setItem('toastVisible', 'true'); // Сохраняем состояние
                    location.reload(); // Перезагрузка страницы после успешного удаления
                } else {
                    alert("Ошибка: " + result.msg); // Отображаем сообщение об ошибке
                }
            } else {
                const errorText = await response.text(); // Получаем текст ошибки
                console.error("HTTP Error:", response.status, errorText);
                alert("Ошибка: " + errorText);
            }
        } catch (error) {
            alert("Ошибка: " + error);
            console.error("Fetch Error:", error);
        }
    });
});