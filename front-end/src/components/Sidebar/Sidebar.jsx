import './Sidebar.css';

export default function Sidebar({

  chats,

  activeChatId,

  setActiveChatId,

  createNewChat,
}) {

  return (

    <div className="sidebar">

      {/* Logo */}

      <div className="sidebar-top">

        <div className="logo-section">

          <div className="logo">
            🤖
          </div>

          <div>

            <h2>Interview AI</h2>

            <p>
              Your AI Interview Partner ✨
            </p>

          </div>

        </div>

        {/* New Chat */}

        <button
          className="new-chat-btn"

          onClick={createNewChat}
        >
          + New Chat
        </button>

      </div>

      {/* Recent Chats */}

      <div className="recent-chats">

        <h3>Recent Chats</h3>

        <div className="chat-list">

          {chats.map((chat) => (

            <div
              key={chat.id}

              className={`chat-item ${
                activeChatId === chat.id
                  ? 'active'
                  : ''
              }`}

              onClick={() =>
                setActiveChatId(chat.id)
              }
            >
              {chat.title}
            </div>

          ))}

        </div>

      </div>

    </div>
  );
}