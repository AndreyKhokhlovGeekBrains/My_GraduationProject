function showToast() {
    const toast = document.getElementById("toast");
    toast.className = "toast-message show";
    setTimeout(() => {
        toast.className = toast.className.replace("show", "");
    }, 3000);
}

document.getElementById("add-order-form").addEventListener("submit", async function(event) {
    event.preventDefault(); // Prevent the default form submission

    // Collect form data
    const formData = new FormData(this);
    const data = {};

    // Преобразуем FormData в обычный объект
    formData.forEach((value, key) => {
        data[key] = value;
    });

    try {
        const response = await fetch("/add-order/", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json', // Устанавливаем заголовок для JSON
                'Accept': 'application/json' // Устанавливаем заголовок для принятия JSON
            },
            body: JSON.stringify(data), // Преобразуем объект в JSON
        });

        if (response.ok) {
            const result = await response.json(); // Получаем JSON ответ
            console.log("Response:", result); // Выводим ответ в консоль

            if (result.success) { // Предполагается, что в ответе есть поле success
                showToast(); // Показываем уведомление
            } else {
                alert("Ошибка: " + result.detail);
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