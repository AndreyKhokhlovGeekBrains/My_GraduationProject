// add_order.js
document.addEventListener("DOMContentLoaded", function() {
    // Get the "add-order-button" and add a click event listener
    const addOrderButton = document.querySelector(".add-order-button");

    addOrderButton.addEventListener("click", function(event) {
        event.preventDefault(); // Prevent default button behavior

        // Redirect to the /order-form/ endpoint
        window.location.href = "/order-form/";
    });
});
