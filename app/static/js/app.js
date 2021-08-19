function agreeTnC() {
    var checkbox = document.getElementById('tnc')
    var btn = document.getElementById('register_btn')
    var agree = document.getElementById('agree')
    checkbox.hidden = false
    btn.disabled = false
    agree.innerHTML = "I Agree to"
}