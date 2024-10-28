document.addEventListener('DOMContentLoaded', () => {
    const form = document.forms['form'];

    form.addEventListener('submit', (e) => {
        e.preventDefault(); // Prevent default form submission

        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');

        const data = {
            email: emailInput.value.trim(),
            password: passwordInput.value.trim(),
        };

        fetch('/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                alert("Ошибка, проверьте ввод");
                throw new Error("Ошибка, проверьте ввод");
            }
            return response.json();
        })
        .then(data => {
            alert("Вход прошел успешно");
        })
        .catch(error => {
            console.error(error);
        });
    });
});