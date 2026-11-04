function Message({ message }) {
  return (
    <div className={`message ${message.role}`}>
      <strong>
        {message.role === "user" ? "You" : "AI Bot"}
      </strong>
      <p>{message.content}</p>
    </div>
  );
}

export default Message;