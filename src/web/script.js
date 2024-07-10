function loadPage() {
    changeSignInType()

}

function changeSignInType() {
    let idInput = document.getElementById("signin-input")
    let idText = document.getElementById("signin-text")
    let idVal = idInput.placeholder
    if ([null, undefined, "", "phone number"].includes(idVal)) {
        idInput.type = "email"
        idInput.placeholder = "email address"
        idText.innerHTML = "phone number"
    } else if (idVal == "email address") {
        idInput.type = "tel"
        idInput.placeholder = "phone number"
        idText.innerHTML = "email address"
    } else {
        console.error("some error")
    }


}