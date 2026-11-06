
import { useState } from "react";
import FileUpload from "./components/FileUpload";
import ChatWindow from "./components/ChatWindow";
import "./App.css";

function App() {
    const [isReady, setIsReady] = useState(false);
    const [uploadStarted, setUploadStarted] = useState(false);

    const handleProcessing = () => {
        setIsReady(false);
        setUploadStarted(true);
    };

    const handleReady = () => {
        setIsReady(true);
    };

    return (
        <div className="app">

            <header className="app-header">
                <div className="brand">
                    <div className="brand-icon">AI</div>
                    <div>
                        <h1>AI Smart Assistant</h1>
                        <p>Chat with your documents</p>
                    </div>
                </div>

                <div className={`connection-status ${isReady ? "ready" : ""}`}>
                    <span className="status-dot"></span>
                    {isReady ? "Ready" : uploadStarted ? "Processing" : "Waiting"}
                </div>
            </header>

            <div className="app-layout">

                <aside className="sidebar">
                    <FileUpload
                        onReady={handleReady}
                        onProcessing={handleProcessing}
                    />
                </aside>

                <main className="chat-main">
                    <ChatWindow
                        isReady={isReady}
                        uploadStarted={uploadStarted}
                    />
                </main>

            </div>
        </div>
    );
}

export default App;
