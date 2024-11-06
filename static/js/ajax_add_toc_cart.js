// Define isLoggedIn based on the presence of a JWT cookie
const isLoggedIn = document.cookie.split(';').some((cookie) => cookie.trim().startsWith('JWT='));

// Then, proceed with the AJAX code as it is
$(document).ready(function() {
    $('.image-container a').on('click', function(event) {
        event.preventDefault();
        var positionId = $(this).attr('href').split('=')[1];
        var amount = 1;

        if (isLoggedIn) {
            $.ajax({
                type: 'POST',
                url: '/cart/add/',
                data: { position_id: positionId, amount: amount },
                success: function(data) {
                    alert(data.msg);
                    updateCart().then(function() {
                        location.reload();
                    });
                },
                error: function(xhr, status, error) {
                    alert("Failed to add position to cart.");
                }
            });
        } else {
            window.location.href = "/login/";
        }
    });
});

// Function to update cart contents
function updateCart() {
    return new Promise(function(resolve, reject) {
        $.ajax({
            type: 'GET',
            url: '/cart/get/',
            success: function(data) {
                $('#cart-items').html(data); // Update the contents of the element with ID cart-items
                resolve(); // Successful update
            },
            error: function(xhr, status, error) {
                reject(error); // Error during update
            }
        });
    });
}
