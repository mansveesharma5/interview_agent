import { useEffect, useRef } from 'react';
import './ChatWindow.css';

import MessageBubble from '../MessageBubble/MessageBubble';
import TypingLoader from '../TypingLoader/TypingLoader';
import ResumeUpload from '../ResumeUpload/ResumeUpload';
import ChatService from '../../services/ChatService';

export default function ChatWindow({
  activeChat,
  input,
  setInput,
  sendMessage,
  loading,
  setChats,
  markMessageAnimated,
}) {

  const messagesEndRef = useRef(null);

  const textareaRef = useRef(null);

  useEffect(() => {

    messagesEndRef.current?.scrollIntoView({
      behavior: 'smooth',
    });

  }, [activeChat?.messages, loading]);

  if (!activeChat) {

    return (
      <div className="chat-window empty">
        <div className="empty-chat">
          <h1>
            AI Interview Preparation Agent
          </h1>

          <p>
            Start a new conversation 🚀
          </p>
        </div>
      </div>
    );
  }

  const lastBotIndex =
    activeChat.messages
      ?.map((msg, index) =>
        msg.sender === 'bot'
          ? index
          : -1
      )
      .filter(
        (index) => index !== -1
      )
      .pop();

  const handleSend = () => {

    sendMessage();

    if (textareaRef.current) {

      textareaRef.current.style.height =
        '24px';
    }
  };

  return (
    <div className="chat-window">

      {/* HEADER */}

      <div className="chat-header">

        <div>

          <h2>
            AI Interview Preparation Agent
          </h2>

          <p>
            Crack interviews with AI 🚀
          </p>

          {
            activeChat?.mock_interview && (

              <div className="progress-text">

                Question {
                  activeChat.question_number
                } / 10

              </div>

            )
          }

        </div>

        <div className="header-actions">

          <ResumeUpload
            activeChat={activeChat}
            setChats={setChats}
          />

          {
            activeChat?.mock_interview && (

              <button
                className="stop-btn"
                onClick={async () => {

                  const result =
                    await ChatService.stopInterview(
                      activeChat.id
                    );

                  setChats((prev) => {

                    const updated = {
                      ...prev
                    };

                    updated[
                      activeChat.id
                    ] = result.chat;

                    return updated;
                  });

                }}
              >
                🛑 Stop Interview
              </button>

            )
          }

          {
            !activeChat?.mock_interview &&
            activeChat?.scores?.length > 0 && (

              <button
                className="report-btn"
                onClick={() =>
                  ChatService.downloadReport(
                    activeChat.id
                  )
                }
              >
                📄 Download Report
              </button>

            )
          }

        </div>

      </div>

      {/* MESSAGES */}

      <div className="messages-container">

        <div className="messages-wrapper">

          {
            activeChat.messages?.map(
              (msg, index) => (

                <MessageBubble
                  key={index}
                  message={msg}
                  isLatestBot={
                    msg.sender === 'bot' &&
                    index === lastBotIndex
                  }
                  onTypingComplete={
                    markMessageAnimated
                  }
                />

              )
            )
          }

          {/* ANALYTICS DASHBOARD */}

          {
            !activeChat?.mock_interview &&
            activeChat?.scores?.length > 0 && (

              <div className="analytics-card">

                <h3>
                  📊 Performance Analytics
                </h3>

                <div className="analytics-summary">

                  <div>
                    <strong>
                      Average Score:
                    </strong>

                    {" "}
                    {
                      activeChat.average_score ||
                      (
                        activeChat.scores.reduce(
                          (a, b) => a + b,
                          0
                        ) /
                        activeChat.scores.length
                      ).toFixed(1)
                    }
                    /10
                  </div>

                  <div>
                    <strong>
                      Progress:
                    </strong>

                    {" "}
                    {
                      activeChat.progress || 0
                    }%
                  </div>

                  <div>
                    <strong>
                      Recommendation:
                    </strong>

                    {" "}
                    {
                      activeChat.recommendation ||
                      "Pending"
                    }
                  </div>

                </div>

                <div className="score-list">

                  {
                    activeChat.scores.map(
                      (score, index) => (

                        <div
                          key={index}
                          className="score-row"
                        >

                          <span>
                            Q{index + 1}
                          </span>

                          <div
                            className="score-bar"
                          >

                            <div
                              className="score-fill"
                              style={{
                                width:
                                  `${score * 10}%`
                              }}
                            />

                          </div>

                          <span>
                            {score}
                          </span>

                        </div>

                      )
                    )
                  }

                </div>

              </div>

            )
          }

          {loading && (
            <TypingLoader />
          )}

          <div
            ref={messagesEndRef}
          />

        </div>

      </div>

      {/* INPUT */}

      <div className="chat-input-wrapper">

        <div className="chat-input-section">

          <textarea

            ref={textareaRef}

            rows="1"

            placeholder="Message Interview AI..."

            value={input}

            onChange={(e) => {

              setInput(
                e.target.value
              );

              e.target.style.height =
                'auto';

              e.target.style.height =
                `${e.target.scrollHeight}px`;
            }}

            onKeyDown={(e) => {

              if (
                e.key === 'Enter' &&
                !e.shiftKey
              ) {

                e.preventDefault();

                handleSend();
              }
            }}
          />

          <button
            onClick={handleSend}
          >
            Send
          </button>

        </div>

      </div>

    </div>
  );
}