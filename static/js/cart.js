async function updateItem(productId) {
    const quantity = prompt("Enter new quantity:");
    if (quantity) {
        const response = await fetch('/api/v1/cart/update', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, quantity: parseInt(quantity) }),
        });
        location.reload();
    }
}

async function removeItem(productId) {
    const response = await fetch('/api/v1/cart/remove', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId }),
    });
    location.reload();
}

async function clearCart() {
    const response = await fetch('/api/v1/cart/clear', {
        method: 'DELETE',
    });
    location.reload();
}
