document.querySelectorAll(".delete-item").forEach(button => {
    button.addEventListener("click", function() {
        const itemId = this.getAttribute("data-item-id");

        // Make a POST request to the /delete/ endpoint
        fetch(`/cart/delete/?position_id=${itemId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include' // Include cookies in the request
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.msg);
                // Optionally, remove the item from the DOM
                this.closest(".cart-item").remove();
                location.reload();
            } else {
                showToast("Failed to delete item from cart.");
            }
        })
        .catch(error => {
            console.error("Error deleting item from cart:", error);
            showToast("An error occurred. Please try again.");
        });
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
    }, 5000);
}
