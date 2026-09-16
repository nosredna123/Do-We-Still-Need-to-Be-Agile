import React from "react";
import "./Message.css";

function Message({ text, role, avatar }) {
  return (
    <div className={`chat-message ${role}`}>
      {avatar && <img src={avatar} alt={role} className="message-avatar" />}
      <div className="message-bubble">{text}</div>
    </div>
  );
}

export default Message;
