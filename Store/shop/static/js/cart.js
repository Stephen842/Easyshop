function updateCart(productId, action, csrfToken) {
    let formData = new FormData();
    formData.append("product_id", productId);
    formData.append("action", action);

    fetch("/add-to-cart/", {  // Ensure this URL is correct
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById("cart-message").textContent = data.message;
            document.getElementById("cart-message").classList.remove("hidden");

            // update the cart count
            if (data.cart_count !== undefined) {
                document.getElementById("cart-count").textContent = data.cart_count;
            }

        } else {
            alert("Error: " + data.message);
        }
    })
    .catch(error => console.error("Error:", error));
}

document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll(".cart-action-btn").forEach(button => {
        button.addEventListener("click", function() {
            let productId = button.getAttribute("data-product-id");
            let action = button.getAttribute("data-action");
            let csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']").value;
            updateCart(productId, action, csrfToken);
        });
    });
});


document.addEventListener("DOMContentLoaded", function () {
    function reloadPage() {
        setTimeout(() => {
            location.reload();
        }, 1000); // Reload after 2 seconds
    }

    document.body.addEventListener("click", function (event) {
        if (event.target.classList.contains("cart-action-btn")) {
            reloadPage();
        }
    });
});
