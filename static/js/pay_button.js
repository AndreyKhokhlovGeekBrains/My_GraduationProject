document.addEventListener("DOMContentLoaded", function() {
    const payButton = document.querySelector(".pay-btn");

    payButton.addEventListener("click", function(event) {
        event.preventDefault(); // Prevent default form submission

        // Get the address value from the input field
        const address = document.getElementById("address").value;

        // Redirect to the payment page with the address as a query parameter
        window.location.href = `/payment/?address=${encodeURIComponent(address)}`;
    });
});
