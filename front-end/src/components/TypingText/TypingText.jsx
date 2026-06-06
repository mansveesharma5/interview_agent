import {
  useEffect,
  useState,
} from 'react';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function TypingText({
  text,
  onComplete,
  speed = 20,
}) {

  const [displayText,
    setDisplayText] =
    useState('');

  useEffect(() => {

    if (!text) return;

    setDisplayText('');

    const words =
      text.split(' ');

    let index = 0;

    const interval =
      setInterval(() => {

        if (
          index >= words.length
        ) {

          clearInterval(
            interval
          );

          if (
            onComplete
          ) {
            onComplete();
          }

          return;
        }

        setDisplayText(
          (prev) =>
            prev
              ? prev +
                ' ' +
                words[index]
              : words[index]
        );

        index++;

      }, speed);

    return () =>
      clearInterval(
        interval
      );

  }, [
    text,
    speed,
    onComplete,
  ]);

  return (

    <ReactMarkdown
      remarkPlugins={[
        remarkGfm,
      ]}
    >
      {displayText}
    </ReactMarkdown>

  );
}