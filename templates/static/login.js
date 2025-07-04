function login() {
    let username = document.getElementById('uname');
    let password = document.getElementById('pass');
    let data = { password: password.value, username: username.value };

    axios.post('/login', data)
        .then(response => {
            location.reload();
        })
        .catch(error => {
            if (error.status == 401) {
                document.getElementById('uname').style.border = "2px solid red";
                document.getElementById('pass').style.border = "2px solid red";
            } 
            else console.log(error.status)
        });
}