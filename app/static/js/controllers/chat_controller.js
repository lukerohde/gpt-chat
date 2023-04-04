import { Controller } from "stimulus";

export default class extends Controller {
  static targets = ["messageList", "userList", "chatForm"];

  socket = null;
  currentRecipient = 0;
  
  connect() {
    this.handleMessageReceivedBound = this.handleMessageReceived.bind(this);
    this.initializeWebSocket();
    this.scrollToBottom();
    this.currentRecipient = this.element.dataset.currentRecipient;
  }

  disconnect() {
    // Close the WebSocket connection when the controller is disconnected
    if (this.socket) {
      this.socket.removeEventListener('message', this.handleMessageReceivedBound);
      this.socket.close();
      this.socket = null;
    }
  }

  initializeWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const host = window.location.host;
    const wsPath = protocol + host;

    this.socket = new WebSocket(wsPath + `/ws?session_key=${sessionKey}`);
    this.socket.addEventListener('message', this.handleMessageReceivedBound);
  }

  handleMessageReceived(event) {
    let data = JSON.parse(event.data);
    this.messageListTarget.insertAdjacentHTML("beforeend", data['message']);
    this.scrollToBottom();
    hljs.highlightAll();
  }

  async userClicked(event) {
    event.preventDefault();
    
    const selectedUserId = event.target.dataset.userId;
    this.currentRecipient = selectedUserId

    let newUrl = `/${selectedUserId}/`
    window.history.replaceState({ userId: selectedUserId }, "", newUrl);
    this.chatFormTarget.action = newUrl;

    this.disableInput();
    this.userListTarget.querySelector(".active")?.classList.remove("active");
    
    const response = await fetch(newUrl, {
      headers: {
        "X-Requested-With": "XMLHttpRequest"
      }
    });
    const data = await response.json();
    this.messageListTarget.innerHTML = data.html;
    
    event.target.classList.add("active");
    this.scrollToBottom();
    this.enableInput();
  }  

  async submitForm(event) {
    event.preventDefault();

    // Prepare the form data
    const formData = new FormData(event.target);

    // Submit the form via AJAX
    const response = await fetch(event.target.action, {
      method: 'POST',
      body: formData,
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      },
      credentials: 'same-origin'
    });

    if (response.ok) {
      // Clear the input field
      this.element.querySelector('#chat-input').value = '';
    } else {
      console.error('Error submitting the form:', response.statusText);
    }
  }

  scrollToBottom() {
    this.messageListTarget.scrollTo({
      top: this.messageListTarget.scrollHeight,
      behavior: "smooth"
    });
  }

  enableInput() {
    document.getElementById('chat-input').disabled = false;
    document.getElementById('btn-send').disabled = false;
    document.getElementById('chat-input').focus();
  }

  disableInput() {
    document.getElementById('chat-input').disabled = true;
    document.getElementById('btn-send').disabled = true;
  }
}
