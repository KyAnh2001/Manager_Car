$(document).ready(function(){
    $('.addToCartBtn').click(function (e) {
        e.preventDefault();

        var product_id = $(this).siblings('.prod_id').val();
        var token = $('input[name="csrfmiddlewaretoken"]').val();
        $.ajax({
            method: "POST",
            url: "/car/add-to-cart/",
            data: {
                'prod_id': product_id,
                'csrfmiddlewaretoken': token
            },
            success: function (response) {
                console.log(response);
            }

        });
    });
});
