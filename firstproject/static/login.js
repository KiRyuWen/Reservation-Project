
let loginBtn = document.getElementById("login_btn");
loginBtn.addEventListener('click',login);




function login(){
    let elements = document.querySelectorAll("input");
    let account = elements[0].value;
    let password = elements[1].value;
    console.log(account);
    console.log(password);
}


