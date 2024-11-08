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

function updateQuantity(itemId, quantityChange) {
    fetch(`/cart/update_quantity/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId, quantity: quantityChange })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the HTML elements if needed, or reload the page to reflect changes
            location.reload(); // Optionally reload to refresh the cart view
        } else {
            alert("Failed to update quantity.");
        }
    })
    .catch(error => {
        console.error("Error updating quantity:", error);
    });
}
