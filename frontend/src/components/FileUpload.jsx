
import { useEffect, useRef, useState } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:5000";

function FileUpload({ onReady, onProcessing }) {
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState("");
    const [status, setStatus] = useState("idle");
    const [uploadProgress, setUploadProgress] = useState(0);

    const timerRef = useRef(null);

    useEffect(() => {
        return () => {
            if (timerRef.current) {
                clearTimeout(timerRef.current);
            }
        };
    }, []);

    const handleFileChange = (event) => {
        const selectedFile = event.target.files[0];

        setFile(selectedFile || null);
        setMessage("");
        setStatus("idle");
        setUploadProgress(0);
    };

    const checkStatus = async (jobId) => {
        try {
            const response = await axios.get(
                `${API_URL}/status/${jobId}`
            );

            const data = response.data;

            if (data.status === "ready") {
                setStatus("ready");
                setMessage("Document is ready! You can start chatting.");
                onReady();
                return;
            }

            if (data.status === "failed") {
                setStatus("failed");
                setMessage(
                    data.error || "Document processing failed."
                );
                return;
            }

            setStatus("processing");
            setMessage("PDF uploaded successfully!");

            timerRef.current = setTimeout(
                () => checkStatus(jobId),
                2000
            );

        } catch (error) {
            setStatus("failed");
            setMessage(
                "Unable to check document processing status."
            );
        }
    };

    const handleUpload = async () => {
        if (!file) {
            setMessage("Please select a PDF first.");
            return;
        }

        if (timerRef.current) {
            clearTimeout(timerRef.current);
        }

        onProcessing();

        setStatus("uploading");
        setMessage("");
        setUploadProgress(0);

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await axios.post(
                `${API_URL}/upload`,
                formData,
                {
                    onUploadProgress: (progressEvent) => {
                        if (progressEvent.total) {
                            const percentage = Math.round(
                                (progressEvent.loaded * 100) /
                                progressEvent.total
                            );

                            setUploadProgress(percentage);
                        }
                    }
                }
            );

            const { job_id } = response.data;

            setUploadProgress(100);
            setStatus("processing");
            setMessage("PDF uploaded successfully!");

            checkStatus(job_id);

        } catch (error) {
            setStatus("failed");
            setMessage(
                error.response?.data?.error || "PDF upload failed."
            );
        }
    };

    return (
        <div className="file-upload">

            <h2>Upload your PDF</h2>

            <input
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleFileChange}
                disabled={
                    status === "uploading" ||
                    status === "processing"
                }
            />

            <button
                onClick={handleUpload}
                disabled={
                    !file ||
                    status === "uploading" ||
                    status === "processing"
                }
            >
                {status === "uploading"
                    ? "Uploading..."
                    : status === "processing"
                    ? "Uploaded"
                    : "Upload PDF"}
            </button>

            {/* Initial message before uploading */}
            {status === "idle" && (
                <p className="status-message">
                    {file
                        ? `Selected: ${file.name}. Click Upload PDF to continue.`
                        : "Select a PDF and upload it to start chatting."}
                </p>
            )}

            {/* Actual PDF upload progress */}
            {status === "uploading" && (
                <div className="progress-container">

                    <div className="progress-info">
                        <span>Uploading PDF</span>
                        <span>{uploadProgress}%</span>
                    </div>

                    <div className="progress-track">
                        <div
                            className="progress-fill"
                            style={{
                                width: `${uploadProgress}%`
                            }}
                        />
                    </div>

                </div>
            )}

            {/* Upload completed, background processing continues */}
            {status === "processing" && (
                <p className="status-message">
                    PDF uploaded successfully!
                </p>
            )}

            {/* All document processing completed */}
            {status === "ready" && (
                <p className="status-message ready">
                    Document is ready! You can start chatting.
                </p>
            )}

            {/* Error message */}
            {status === "failed" && (
                <p className="status-message failed">
                    {message}
                </p>
            )}

        </div>
    );
}

export default FileUpload;
