
import { useState } from "react";
import axios from "axios";
import Message from "./Message";

const API_URL = "http://127.0.0.1:5000";

function ChatWindow({ isReady, uploadStarted }) {
    const [question, setQuestion] = useState("");
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);

    const sendMessage = async () => {
        if (!question.trim() || !isReady || loading) {
            return;
        }

        const userQuestion = question.trim();

        const updatedMessages = [
            ...messages,
            { role: "user", content: userQuestion }
        ];

        setMessages(updatedMessages);
        setQuestion("");
        setLoading(true);

        try {
            const response = await axios.post(
                `${API_URL}/chat`,
                {
                    question: userQuestion,
                    history: messages
                }
            );

            setMessages([
                ...updatedMessages,
                {
                    role: "assistant",
                    content: response.data.answer
                }
            ]);

        } catch (error) {
            setMessages([
                ...updatedMessages,
                {
                    role: "assistant",
                    content:
                        error.response?.data?.error ||
                        "Something went wrong."
                }
            ]);

        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chat-window">

            <h2>Chat with your PDF</h2>

            {!uploadStarted && !isReady && (
                <p className="chat-waiting">
                    Upload a PDF to start chatting.
                </p>
            )}

            {uploadStarted && !isReady && (
                <p className="chat-waiting">
                    Your document is being prepared. Chat will be available shortly.
                </p>
            )}

            {isReady && messages.length === 0 && (
                <p className="chat-waiting">
                    Your document is ready! Ask your first question.
                </p>
            )}

            <div className="messages">
                {messages.map((message, index) => (
                    <Message
                        key={index}
                        message={message}
                    />
                ))}

                {loading && <p>Thinking...</p>}
            </div>

            <div className="chat-input">

                <input
                    type="text"
                    value={question}
                    onChange={(event) =>
                        setQuestion(event.target.value)
                    }
                    onKeyDown={(event) => {
                        if (event.key === "Enter") {
                            sendMessage();
                        }
                    }}
                    placeholder={
                        isReady
                            ? "Ask something about your PDF..."
                            : uploadStarted
                            ? "Preparing your document..."
                            : "Select and upload a PDF first..."
                    }
                    disabled={!isReady || loading}
                />

                <button
                    onClick={sendMessage}
                    disabled={
                        !isReady ||
                        loading ||
                        !question.trim()
                    }
                >
                    {loading ? "Sending..." : "Send"}
                </button>

            </div>

        </div>
    );
}

export default ChatWindow;
