import { useEffect, useState } from 'react';
import './App.css';

import Sidebar from './components/Sidebar/Sidebar';
import ChatWindow from './components/ChatWindow/ChatWindow';
import ChatService from './services/ChatService';

function App() {

  const [chats, setChats] = useState([]);

  const [activeChatId, setActiveChatId] =
    useState(null);

  const [input, setInput] =
    useState('');

  const [loading, setLoading] =
    useState(false);

  useEffect(() => {
    loadChats();
  }, []);

  const loadChats = async () => {

    try {

      const response =
        await ChatService.getChatHistory();

      const chatsArray = Object.entries(
        response.chats || {}
      )
        .map(([id, chat]) => ({
          id,
          ...chat,
        }))
        .reverse();

      setChats(chatsArray);

      if (chatsArray.length > 0) {

        const savedChatId =
          localStorage.getItem(
            'activeChatId'
          );

        const chatExists =
          chatsArray.some(
            (chat) =>
              String(chat.id) ===
              String(savedChatId)
          );

        if (
          savedChatId &&
          chatExists
        ) {

          setActiveChatId(
            savedChatId
          );

        } else {

          setActiveChatId(
            chatsArray[0].id
          );

          localStorage.setItem(
            'activeChatId',
            chatsArray[0].id
          );
        }
      }

    } catch (err) {

      console.error(err);

    }
  };  
  
  const activeChat = chats.find(
    (chat) =>
      String(chat.id) ===
      String(activeChatId)
  );

  // MARK LAST BOT MESSAGE AS ANIMATED

  const markMessageAnimated =
    () => {

      setChats((prev) =>
        prev.map((chat) => {

          if (
            String(chat.id) !==
            String(activeChatId)
          ) {
            return chat;
          }

          const updatedMessages =
            [...chat.messages];

          for (
            let i =
              updatedMessages.length - 1;
            i >= 0;
            i--
          ) {

            if (
              updatedMessages[i]
                .sender === 'bot'
            ) {

              updatedMessages[i] = {
                ...updatedMessages[i],
                animated: true,
              };

              break;
            }
          }

          return {
            ...chat,
            messages:
              updatedMessages,
          };
        })
      );
    };

  const handleChatSelect =
    (chatId) => {

      setActiveChatId(chatId);

      localStorage.setItem(
        'activeChatId',
        chatId
      );
    };

  const createNewChat =
    async () => {

      try {

        const response =
          await ChatService.createChat();

        const newChat = {

          id: response.chat_id,

          ...response.chat,
        };

        setChats((prev) => [
          newChat,
          ...prev,
        ]);

        setActiveChatId(
          response.chat_id
        );

        localStorage.setItem(
          'activeChatId',
          response.chat_id
        );

      } catch (err) {

        console.error(err);

      }
    };

  const sendMessage =
    async () => {

      if (
        !input.trim() ||
        !activeChatId
      ) {
        return;
      }

      const currentInput =
        input;

      const optimisticMessage = {

        sender: 'user',

        text: currentInput,
      };

      setChats((prev) =>
        prev.map((chat) =>
          String(chat.id) ===
          String(activeChatId)
            ? {
                ...chat,
                messages: [
                  ...(chat.messages ||
                    []),
                  optimisticMessage,
                ],
              }
            : chat
        )
      );

      setInput('');

      setLoading(true);

      try {

        const response =
          await ChatService.sendMessage(
            activeChatId,
            currentInput
          );

        setChats((prev) =>
          prev.map((chat) => {

            if (
              String(chat.id) !==
              String(activeChatId)
            ) {
              return chat;
            }

            const updatedMessages =
              response.chat.messages.map(
                (
                  msg,
                  index,
                  arr
                ) => {

                  const isLastBot =
                    msg.sender ===
                      'bot' &&
                    index ===
                      arr.length - 1;

                  return {

                    ...msg,

                    animated:
                      !isLastBot,
                  };
                }
              );

            return {

              ...response.chat,

              id: activeChatId,

              messages:
                updatedMessages,
            };
          })
        );

      } catch (err) {

        console.error(err);

      } finally {

        setLoading(false);

      }
    };

  return (

    <div className="app">

      <Sidebar
        chats={chats}
        activeChatId={
          activeChatId
        }
        setActiveChatId={
          handleChatSelect
        }
        createNewChat={
          createNewChat
        }
      />

      <ChatWindow
        activeChat={
          activeChat
        }
        input={input}
        setInput={setInput}
        sendMessage={
          sendMessage
        }
        loading={loading}
        setChats={setChats}
        markMessageAnimated={
          markMessageAnimated
        }
      />

    </div>
  );
}

export default App;