document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.form-signin');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = emailInput.value.trim();
        const password = passwordInput.value;

        if (!email || !validateEmail(email)) {
            alert('Please enter a valid email address');
            return;
        }

        if (!password || password.length < 6) {
            alert('Password must be at least 6 characters long');
            return;
        }

        const data = { identifier: email, password: password };

        try {
            const response = await fetch('/api/v1/user/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                alert(JSON.stringify(result));
                window.location.href = '/';
            } else {
                alert(result.error || 'Login failed. Please try again.');
            }
        } catch (error) {
            alert('An error occurred. Please try again later.');
        }
    });
});

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    // return re.test(email);
    return true;
}
