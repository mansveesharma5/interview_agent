import './MessageBubble.css';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import TypingText from '../TypingText/TypingText';

export default function MessageBubble({
  message,
  isLatestBot,
  onTypingComplete,
}) {

  // =========================
  // RESUME CARD
  // =========================

  if (
    message.type ===
    'resume_uploaded'
  ) {

    return (

      <div className="resume-success-card">

        <div className="resume-icon">
          📄
        </div>

        <div>

          <h4>
            {message.fileName}
          </h4>

          <p>
            Resume Uploaded Successfully ✅
          </p>

        </div>

      </div>

    );
  }

  // =========================
  // INTERVIEW REPORT CARD
  // =========================

  const isReport =

    message.text?.includes(
      'MOCK INTERVIEW REPORT'
    ) ||

    message.text?.includes(
      'INTERVIEW STOPPED'
    );

    if (isReport) {

    const scoreMatch =
      message.text.match(
        /Average Score:\s*([\d.]+)/
      );

    const topicMatch =
      message.text.match(
        /Topic:\s*(.*)/
      );

    const recommendationMatch =
      message.text.match(
        /Recommendation:\s*(.*)/
      );

    const questionMatch =
      message.text.match(
        /Questions Attempted:\s*(\d+)/
      );

    const score =
      scoreMatch
        ? parseFloat(scoreMatch[1])
        : 0;

    const topic =
      topicMatch?.[1] || "-";

    const recommendation =
      recommendationMatch?.[1] || "-";

    const questions =
      questionMatch?.[1] || "0";

    const progress =
      Math.min(
        score * 10,
        100
      );

    return (

      <div className="message bot-message">

        <div className="report-card">

          <h2>
            🎯 Interview Performance
          </h2>

          <div className="report-row">
            <span>
              Topic
            </span>

            <strong>
              {topic}
            </strong>
          </div>

          <div className="report-row">
            <span>
              Questions
            </span>

            <strong>
              {questions}/10
            </strong>
          </div>

          <div className="report-row">
            <span>
              Average Score
            </span>

            <strong>
              {score}/10
            </strong>
          </div>

          <div className="progress-container">

            <div
              className="progress-fill"
              style={{
                width: `${progress}%`
              }}
            />

          </div>

          <div className="report-row">

            <span>
              Recommendation
            </span>

            <span
              className={`badge ${
                score >= 8
                  ? "excellent"
                  : score >= 6
                  ? "good"
                  : "improve"
              }`}
            >
              {recommendation}
            </span>

          </div>

        </div>

      </div>

    );
  }

  // =========================
  // NORMAL MESSAGE
  // =========================

  return (

    <div
      className={`message ${
        message.sender === 'user'
          ? 'user-message'
          : 'bot-message'
      }`}
    >

      <div className="message-content">

        {
          isLatestBot &&
          !message.animated ? (

            <TypingText
              text={message.text}
              speed={20}
              onComplete={
                onTypingComplete
              }
            />

          ) : (

            <ReactMarkdown
              remarkPlugins={[
                remarkGfm,
              ]}
            >
              {message.text}
            </ReactMarkdown>

          )
        }

      </div>

    </div>

  );
}