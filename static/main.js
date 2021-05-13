var ws = null;

function connect(event) {
    var itemId = document.getElementById("itemId")
    var token = document.getElementById("token")
    ws = new WebSocket("ws://localhost:8000/items/" + itemId.value + "/ws?token=" + token.value);
    ws.onmessage = function (event) {
        let eventData = JSON.parse(event.data)
        var messages = document.getElementById('messages')
        var message = document.createElement('li')
        message.classList.add(eventData.owner === token.value ? "my-message" : "receiver-message")
        var content = document.createTextNode(eventData.text)
        message.appendChild(content)
        messages.appendChild(message)
    };
    event.preventDefault()
}

function sendMessage(event) {
    var input = document.getElementById("messageText")
    ws.send(input.value)
    input.value = ''
    event.preventDefault()

    /*const token = document.getElementById('token').value;
    const messages = document.getElementById('messages').children;
    for (let i = 0; i < messages.length; i++) {
        const message = messages[i].textContent;
        if (message.indexOf(token) !== -1) {
            messages[i].style.cssText = `
                margin: 5px 0 5px auto;
                `;
        }
    }*/

}

