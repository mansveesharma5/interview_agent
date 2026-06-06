const API_URL = 'http://127.0.0.1:8000';

const ChatService = {

  // GET CHAT HISTORY
  async getChatHistory() {

    const response = await fetch(
      `${API_URL}/chat/all`
    );

    return await response.json();
  },

  // CREATE CHAT
  async createChat() {

    const response = await fetch(
      `${API_URL}/chat/create`,
      {
        method: 'POST',
      }
    );

    return await response.json();
  },

  // SEND MESSAGE
  async sendMessage(
    chatId,
    message
  ) {

    const response = await fetch(
      `${API_URL}/chat`,
      {
        method: 'POST',

        headers: {
          'Content-Type':
            'application/json',
        },

        body: JSON.stringify({
          chatId,
          message,
        }),
      }
    );

    return await response.json();
  },
  // DOWNLOAD REPORT
  async downloadReport(chatId) {

    window.open(
      `${API_URL}/report/${chatId}`,
      '_blank'
    );
  },
  // STOP INTERVIEW
  async stopInterview(chatId) {

    const response = await fetch(
      `${API_URL}/interview/stop/${chatId}`,
      {
        method: "POST"
      }
    );

    return await response.json();
  },
};

export default ChatService;