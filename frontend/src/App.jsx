
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
            <h1>AI RAG Chatbot</h1>

            <FileUpload
                onReady={handleReady}
                onProcessing={handleProcessing}
            />

            <ChatWindow
                isReady={isReady}
                uploadStarted={uploadStarted}
            />
        </div>
    );
}

export default App;
