document.addEventListener("DOMContentLoaded", function() {
    // Function to update quantity
    function updateQuantity(itemId, newQuantity) {
        // Make an AJAX request to update the quantity on the server
        fetch(`/cart/update_quantity/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ item_id: itemId, quantity: newQuantity })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Recalculate and update the item total amount on the page without reloading
                const itemElement = document.querySelector(`.cart-item-details[data-item-id="${itemId}"]`);
                const itemPrice = parseFloat(itemElement.querySelector(".item-price").textContent);
                const itemDiscount = parseFloat(itemElement.querySelector(".item-discount").textContent || 0);

                // Calculate the new item total with the updated quantity
                const itemTotal = newQuantity * itemPrice * (1 - itemDiscount / 100);
                itemElement.querySelector(".item-total").textContent = itemTotal.toFixed(2);

                // Update the overall total amount on the page
                updateTotalAmount();
            } else {
                alert("Failed to update quantity.");
            }
        })
        .catch(error => {
            console.error("Error updating quantity:", error);
        });
    }

    // Function to update the overall total amount
    function updateTotalAmount() {
        let totalAmount = 0.0;
        document.querySelectorAll(".cart-item").forEach(item => {
            const itemTotal = parseFloat(item.querySelector(".item-total").textContent);
            totalAmount += itemTotal;
        });
        document.querySelector(".total-amount h3").textContent = `Total Amount: ${totalAmount.toFixed(2)}`;
    }

    // Add event listeners for the quantity input fields
    document.querySelectorAll(".quantity-input").forEach(input => {
        input.addEventListener("change", function() {
            const itemId = this.getAttribute("data-item-id");
            let newQuantity = parseInt(this.value);

            if (newQuantity > 0) {
                updateQuantity(itemId, newQuantity);
            } else {
                alert("Quantity must be at least 1.");
                this.value = 1; // Reset to 1 if an invalid value is entered
            }
        });
    });
});
