import { Controller } from "stimulus";

export default class extends Controller {
  static targets = ["messageList", "userList"];

  socket = null;
  currentRecipient = 0;

  connect() {
    this.initializeWebSocket();
    this.scrollToBottom();

    $('#chat-input').keypress( (e) => {
        if (!e.shiftKey && e.keyCode == 13)
            $('#btn-send').click();
    });

    $('#btn-send').click( () => {
        if ($('#chat-input').val().length > 0) {
            this.sendMessage(currentRecipient, $('#chat-input').val());
            $('#chat-input').val('');
        }
    });
  }

  initializeWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const host = window.location.host;
    const wsPath = protocol + host;

    this.socket = new WebSocket(wsPath + `/ws?session_key=${sessionKey}`);
    this.socket.addEventListener('message', this.handleMessageReceived.bind(this));
  }

  handleMessageReceived(event) {
    this.getMessageById(event.data);
  }

  async userClicked(event) {
    event.preventDefault();
    
    const selectedUserId = event.target.dataset.userId;
    this.currentRecipient = selectedUserId

    let newUrl = `/chat/${selectedUserId}/`
    console.log(newUrl);
    window.history.replaceState({ userId: selectedUserId }, "", newUrl);

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

  sendMessage(recipient, body) {
      $.post('/api/v1/message/', {
          recipient: recipient,
          body: body
      }).fail(function () {
          alert('Error! Check console!');
      });
  }


  getMessageById(message) {
    let id = JSON.parse(message).message
    $.getJSON(`/api/v1/message/${id}/`, (data) => {
        if (data.user === currentRecipient ||
            (data.recipient === currentRecipient && data.user == currentUser)) {
            this.drawMessage(data);
            hljs.highlightAll();
        }

        this.scrollToBottom();
    });
  }

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
