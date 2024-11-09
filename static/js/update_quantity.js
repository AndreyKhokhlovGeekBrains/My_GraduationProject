document.querySelectorAll(".quantity-input").forEach(input => {
    input.addEventListener("change", function() {
        const itemId = this.getAttribute("data-item-id");
        let newQuantity = parseInt(this.value);

        if (newQuantity > 0) {
            // Send the updated quantity to the server
            updateQuantity(itemId, newQuantity);
        } else {
            alert("Quantity must be at least 1.");
            this.value = 1; // Reset to 1 if an invalid value is entered
        }
    });
});

// Function to show the toast message
function showToast(message) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3500);
}

function updateQuantity(itemId, quantityChange) {
    fetch(`/cart/update_quantity/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId, quantity: quantityChange })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Store the message in sessionStorage
            if (data.message) {
                sessionStorage.setItem("toastMessage", data.message);
            } else {
                sessionStorage.setItem("toastMessage", "Quantity updated successfully.");
            }

            // Reload the page to update the view
            location.reload();
        } else {
            showToast("Failed to update quantity.");
        }
    })
    .catch(error => {
        console.error("Error updating quantity:", error);
        showToast("An error occurred. Please try again.");
    });
}

// Check for a toast message in sessionStorage when the page loads
window.addEventListener("load", () => {
    const message = sessionStorage.getItem("toastMessage");
    if (message) {
        showToast(message);
        sessionStorage.removeItem("toastMessage"); // Clear the message after showing it
    }
});

