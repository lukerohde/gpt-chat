import { Controller } from "stimulus";

export default class extends Controller {
  static targets = ["messageList", "userList", "chatForm"];

  socket = null;
  currentRecipient = 0;

  connect() {
    this.initializeWebSocket();
    this.scrollToBottom();
    this.currentRecipient = this.element.dataset.currentRecipient;
  }

  initializeWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const host = window.location.host;
    const wsPath = protocol + host;

    this.socket = new WebSocket(wsPath + `/ws?session_key=${sessionKey}`);
    this.socket.addEventListener('message', this.handleMessageReceived.bind(this));
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

  // TODO is this form post worth it compared to an ajax post?
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

      // Update the message list or perform other actions if necessary
      // ...
    } else {
      console.error('Error submitting the form:', response.statusText);
    }
  }

  // TODO work out why this doesn't work anymore
  // async submitForm(event) {
  //   event.preventDefault();

  //   $.post('/api/v1/message/', {
  //       recipient: this.currentRecipient,
  //       body: "yo yo"
  //   }).fail(function () {
  //       alert('Error! Check console!');
  //   });
  // }

  scrollToBottom(){
    $(this.messageListTarget).animate({
      scrollTop: $(this.messageListTarget).prop("scrollHeight"),
    });
  }

  enableInput() {
    $('#chat-input').prop('disabled', false);
    $('#btn-send').prop('disabled', false);
    $('#chat-input').focus();
  }

  disableInput() {
    $('#chat-input').prop('disabled', true);
    $('#btn-send').prop('disabled', true);
  }
}
