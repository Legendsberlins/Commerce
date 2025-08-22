function togglePassword(fieldId){
    const password = document.getElementById(fieldId); // fieldId lets us know which id is selected (password or confirmation) 
    const passwordIcon = document.getElementById(`toggle${fieldId.charAt(0).toUpperCase() + fieldId.slice(1)}`);

    if (password.type == "password"){
        password.type = "text";
        passwordIcon.classList.remove("fa-eye");
        passwordIcon.classList.add("fa-eye-slash");
    }
    else{
        password.type = "password";
        passwordIcon.classList.remove("fa-eye-slash");
        passwordIcon.classList.add("fa-eye");
    }
}