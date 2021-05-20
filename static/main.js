var ws = null;

function connect(event) {
    var itemId = document.getElementById("itemId")
    var token = document.getElementById("token")
    ws = new WebSocket("ws://localhost:8000/items/" + itemId.value + "/ws?token=" + token.value);
    ws.onmessage = function (event) {
        let eventData = JSON.parse(event.data)
        console.log(eventData)
        var messages = document.getElementById('messages')
        var message = document.createElement('li')
        message.classList.add(eventData.owner === token.value ? "my-message" : "receiver-message")
        var content = document.createTextNode(eventData.text)
        message.appendChild(content)
        messages.appendChild(message)
        messages.scrollTop = messages.scrollHeight;
    };
    event.preventDefault()
}

function sendMessage(event) {
    var input = document.getElementById("messageText")
    ws.send(input.value)
    input.value = ''
    event.preventDefault()
}

async function uploadFile() {
    let formData = new FormData();
    formData.append("file", fileupload.files[0]);
    await fetch('/import_file', {
        method: "POST",
        body: formData
  });
    alert('The file has been uploaded successfully.');
}