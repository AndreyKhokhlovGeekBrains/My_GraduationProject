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
                    updateCart();
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
