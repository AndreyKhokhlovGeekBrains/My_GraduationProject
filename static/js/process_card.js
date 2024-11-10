document.addEventListener("DOMContentLoaded", function() {
    const cardForm = document.getElementById("card-form");

    cardForm.addEventListener("submit", function(event) {
        event.preventDefault(); // Prevent the default form submission

        // Collect form data
        const formData = new FormData(cardForm);

        // Send the form data using fetch
        fetch("/process_payment/", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show the success message in the toast
                if (data.msg) {
                    sessionStorage.setItem("toastMessage", data.msg);
                }

                // Optionally, you can redirect or do other actions here
                window.location.href = "/"; // Redirect to the homepage
            } else {
                // Show an error message in the toast
                showToast("Payment failed. Please try again.");
            }
        })
        .catch(error => {
            console.error("Error processing payment:", error);
            showToast("An error occurred. Please try again.");
        });
    });

    // Function to show the toast message
    function showToast(message) {
        const toast = document.getElementById("toast");
        toast.textContent = message;
        toast.classList.add("show");

        // Hide the toast after 5 seconds
        setTimeout(() => {
            toast.classList.remove("show");
        }, 3500);
    }
});

// Check for a toast message in sessionStorage when the page loads
window.addEventListener("load", () => {
    const message = sessionStorage.getItem("toastMessage");
    if (message) {
        showToast(message);
        sessionStorage.removeItem("toastMessage"); // Clear the message after showing it
    }
});
