import { useState } from 'react';

import './ResumeUpload.css';

export default function ResumeUpload({
  activeChat,
  setChats,
}) {

  const [file, setFile] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const uploadResume = async () => {

    if (!file) return;

    if (!activeChat?.id) {

      alert('No active chat found');

      return;
    }

    const formData =
      new FormData();

    formData.append(
      'file',
      file
    );

    formData.append(
      'chatId',
      Number(activeChat.id)
    );

    setLoading(true);

    try {

      const response =
        await fetch(
          'http://127.0.0.1:8000/resume/upload',
          {
            method: 'POST',
            body: formData,
          }
        );

      const data =
        await response.json();

      console.log(data);

      setChats((prev) =>
        prev.map((chat) =>
          chat.id === activeChat.id
            ? {
                ...data.chat,
                id: activeChat.id,
              }
            : chat
        )
      );

      // CLEAR FILE
      setFile(null);

    } catch (err) {

      console.error(
        "Resume Upload Error:",
        err
      );

    } finally {

      setLoading(false);
    }
  };

  return (

    <div className="resume-upload">

      <label className="upload-btn">

        Upload Resume

        <input
          type="file"
          accept=".pdf"
          hidden
          onChange={(e) =>
            setFile(
              e.target.files[0]
            )
          }
        />

      </label>

      {file && (

        <>
          <span className="file-name">
            {file.name}
          </span>

          <button
            className="analyze-btn"
            onClick={uploadResume}
          >
            {loading
              ? 'Uploading...'
              : 'Analyze'}
          </button>
        </>
      )}
    </div>
  );
}

