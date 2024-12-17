const API_BASE = "/api/v1/product";

document.getElementById("addProductForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("product_name", document.getElementById("productName").value);
    formData.append("product_description", document.getElementById("productDescription").value);
    formData.append("product_price", document.getElementById("productPrice").value);
    formData.append("product_image", document.getElementById("productImage").files[0]);

    try {
        const response = await fetch(`${API_BASE}/add`, {
            method: "POST",
            body: formData,
        });
        const result = await response.json();
        alert(result.message);
    } catch (err) {
        console.error("Error adding product:", err);
        alert("Failed to add product.");
    }
});

document.getElementById("updateProductForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const productId = document.getElementById("updateProductId").value;
    const formData = new FormData();
    formData.append("product_name", document.getElementById("updateProductName").value);
    formData.append("product_description", document.getElementById("updateProductDescription").value);
    formData.append("product_price", document.getElementById("updateProductPrice").value);
    if (document.getElementById("updateProductImage").files[0]) {
        formData.append("product_image", document.getElementById("updateProductImage").files[0]);
    }

    try {
        const response = await fetch(`${API_BASE}/update/${productId}`, {
            method: "PUT",
            body: formData,
        });
        const result = await response.json();
        alert(result.message);
    } catch (err) {
        console.error("Error updating product:", err);
        alert("Failed to update product.");
    }
});

document.getElementById("deleteProductForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const productId = document.getElementById("deleteProductId").value;

    try {
        const response = await fetch(`${API_BASE}/delete/${productId}`, {
            method: "DELETE",
        });
        const result = await response.json();
        alert(result.message);
    } catch (err) {
        console.error("Error deleting product:", err);
        alert("Failed to delete product.");
    }
});