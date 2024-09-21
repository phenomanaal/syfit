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

function changeSignInOrUp() {
    let signInHeader = document.getElementById("signin-header")
    let signInFooter = document.getElementById("signin-footer")
    let signInSwitch = document.getElementById("signin-switch")
    let temp = signInHeader.innerHTML
    signInHeader.innerHTML = signInSwitch.innerHTML
    signInSwitch.innerHTML = temp

    if (signInSwitch.innerHTML == "sign up") {
        signInFooter.innerHTML = "don't have an account?"
    } else if (signInSwitch.innerHTML == "sign in") {
        signInFooter.innerHTML = "already have an account?"
    }
}