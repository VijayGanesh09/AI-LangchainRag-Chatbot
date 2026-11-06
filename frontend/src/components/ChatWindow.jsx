import { useState, useEffect, useRef } from "react";
import axios from "axios";
import Message from "./Message";

const API_URL = "http://127.0.0.1:5000";

function ChatWindow({ isReady, uploadStarted }) {
    const [question, setQuestion] = useState("");
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);

    const messagesEndRef = useRef(null);

    // Automatically scroll to the latest message
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth"
        });
    }, [messages, loading]);

    const sendMessage = async () => {
        if (!question.trim() || !isReady || loading) {
            return;
        }

        const userQuestion = question.trim();

        const updatedMessages = [
            ...messages,
            {
                role: "user",
                content: userQuestion
            }
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
                        "Something went wrong. Please try again."
                }
            ]);

        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    };

    return (
        <main className="chat-window">

            {/* Chat Header */}
            <header className="chat-header">
                <div>
                    <h2>AI Assistant</h2>
                    <p>
                        Ask questions and get intelligent answers
                    </p>
                </div>

                <div className={`chat-status ${
                    isReady ? "status-ready" : "status-waiting"
                }`}>
                    <span className="status-dot"></span>
                    {isReady
                        ? "Ready"
                        : uploadStarted
                        ? "Preparing"
                        : "Waiting for document"}
                </div>
            </header>

            {/* Chat Messages */}
            <section className="chat-body">

                {messages.length === 0 && (
                    <div className="welcome-screen">
                        <div className="welcome-icon">
                            ✦
                        </div>

                        <h2>
                            How can I help you today?
                        </h2>

                        <p>
                            {isReady
                                ? "Your document is ready. Ask me anything about its contents."
                                : uploadStarted
                                ? "Your document is being processed. The chat will be available shortly."
                                : "Upload a document from the sidebar to get started."}
                        </p>

                        {isReady && (
                            <div className="suggestion-list">
                                <div
                                    className="suggestion-card"
                                    onClick={() => setQuestion(
                                        "Give me a summary of this document."
                                    )}
                                >
                                    <span>✦</span>
                                    <p>Summarize this document</p>
                                </div>

                                <div
                                    className="suggestion-card"
                                    onClick={() => setQuestion(
                                        "What are the main topics covered?"
                                    )}
                                >
                                    <span>⌕</span>
                                    <p>Find the main topics</p>
                                </div>

                                <div
                                    className="suggestion-card"
                                    onClick={() => setQuestion(
                                        "Explain the important concepts."
                                    )}
                                >
                                    <span>✧</span>
                                    <p>Explain key concepts</p>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {messages.map((message, index) => (
                    <Message
                        key={index}
                        message={message}
                    />
                ))}

                {loading && (
                    <div className="thinking-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                        <p>Thinking...</p>
                    </div>
                )}

                <div ref={messagesEndRef} />

            </section>

            {/* Message Composer */}
            <footer className="chat-footer">
                <div className="chat-composer">

                    <input
                        type="text"
                        value={question}
                        onChange={(event) =>
                            setQuestion(event.target.value)
                        }
                        onKeyDown={handleKeyDown}
                        placeholder={
                            isReady
                                ? "Message AI Assistant..."
                                : uploadStarted
                                ? "Preparing your document..."
                                : "Upload a document to start chatting..."
                        }
                        disabled={!isReady || loading}
                    />

                    <button
                        className="send-button"
                        onClick={sendMessage}
                        disabled={
                            !isReady ||
                            loading ||
                            !question.trim()
                        }
                        aria-label="Send message"
                    >
                        ↑
                    </button>

                </div>

                <p className="composer-note">
                    AI can make mistakes. Verify important information.
                </p>
            </footer>

        </main>
    );
}

export default ChatWindow;