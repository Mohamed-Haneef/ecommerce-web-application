document.getElementById('signup-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(this);
    var reenterpassword = formData.get('re-enter-password')
    const userData = {
        username: formData.get('username'),
        email: formData.get('email'),
        dob: formData.get('dob'),
        mobile: formData.get('phone'),
        password: formData.get('password')
    };

    if (!userData.username || !userData.email || !userData.dob || !userData.mobile || !userData.password) {
        alert("Please fill all the fields.");
        return;
    }

    if(userData.password !== reenterpassword){
        alert("Passwords didn't match.");
        return
    }

    fetch('/api/v1/user/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData) 
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);  
        } else {
            alert('Signup successful!');
            redirect('/')
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('There was an error with the signup process.');
    });
});
