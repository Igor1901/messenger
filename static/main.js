let ws = null
let username = null
let messages = null
let fileUploadElement = null
let messageTextElement = null

let initialized = false

document.addEventListener('DOMContentLoaded', scriptStartupHandler)
if (!initialized) {
  scriptStartupHandler()
}

function scriptStartupHandler() {
  if (!initialized) {
    messages = document.getElementById('messages')
    fileUploadElement = document.getElementById('file-upload')
    messageTextElement = document.getElementById('message-text')
  }

  initialized = true
}

function connect() {
  username = document.getElementById('username').value
  ws = new WebSocket(`ws://localhost:8000/socket/${username}`)
  ws.onmessage = handleWsMessage
}

function handleWsMessage(event) {
  let eventData = JSON.parse(event.data)
  let message = document.createElement('li')

  message.classList.add(
    eventData.owner === username ? 'my-message' : 'receiver-message'
  )

  let messageContent = null

  switch (eventData.type) {
    case 'text':
      messageContent = createTextMessageContent(eventData)
      break

    case 'upload':
      messageContent = createUploadMessageContent(eventData)
      break
  }

  authorNode = document.createTextNode(`${eventData.owner}:`)
  message.appendChild(authorNode)
  message.appendChild(messageContent)
  messages.appendChild(message)
  messages.scrollTop = messages.scrollHeight
}

function createTextMessageContent(event) {
  return document.createTextNode(event.content)
}

function createUploadMessageContent(event) {
  let imageElement = document.createElement('img')
  imageElement.setAttribute('src', event.content)

  return imageElement
}

function sendMessage() {
  let input = messageTextElement.value
  let message = {
    "content": input
  }
  ws.send(JSON.stringify(message))
  messageTextElement.value = ''
}

async function uploadFile() {
  let file = fileUploadElement.files[0]

  let formData = new FormData()
  formData.append('file', file)

  await fetch(`/upload-file/${username}`, {
    method: 'POST',
    body: formData,
  })
}
