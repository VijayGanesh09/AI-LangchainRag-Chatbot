
import os
import uuid
import threading

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from app.config import UPLOAD_FOLDER
from app.ingestion import load_and_split_pdf
from app.vectorstore import create_vector_store
from app.rag_chain import generate_answer


# ==========================================
# FLASK CONFIGURATION
# ==========================================

app = Flask(__name__)
CORS(app)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf"}

processing_status = {}
status_lock = threading.Lock()

BATCH_SIZE = 32

# Currently active document
active_document_id = None

# Prevent simultaneous uploads
upload_lock = threading.Lock()


# ==========================================
# WIDGET DIRECTORY
# ==========================================

WIDGET_FOLDER = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "frontend",
        "dist-widget"
    )
)


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def update_status(job_id, **updates):

    with status_lock:

        if job_id in processing_status:
            processing_status[job_id].update(updates)


# ==========================================
# BACKGROUND PDF PROCESSING
# ==========================================

def process_pdf_in_background(
    job_id,
    first_chunks,
    remaining_chunks
):

    global active_document_id

    try:

        total_chunks = len(first_chunks)

        # Insert first batch and clear previous vectors
        create_vector_store(
            first_chunks,
            reset=True
        )

        batch = []

        # Process remaining chunks
        for chunk in remaining_chunks:

            batch.append(chunk)
            total_chunks += 1

            if len(batch) >= BATCH_SIZE:

                # Insert without clearing previous batches
                create_vector_store(
                    batch,
                    reset=False
                )

                batch = []

                update_status(
                    job_id,
                    chunks_processed=total_chunks
                )

        # Insert final remaining batch
        if batch:

            create_vector_store(
                batch,
                reset=False
            )

        # Mark document as ready
        with status_lock:

            active_document_id = job_id

            processing_status[job_id].update({
                "status": "ready",
                "chunks_processed": total_chunks,
                "message": "Document is ready to chat"
            })

        print("PDF processing completed successfully.")
        print("Document ID:", job_id)
        print("Total chunks:", total_chunks)

    except Exception as e:

        print("Background processing error:", str(e))

        update_status(
            job_id,
            status="failed",
            error=str(e),
            message="Document processing failed"
        )

    finally:

        upload_lock.release()


# ==========================================
# PDF UPLOAD API
# ==========================================

@app.route("/upload", methods=["POST"])
def upload_file():

    global active_document_id

    if "file" not in request.files:

        return jsonify({
            "error": "No file provided"
        }), 400

    file = request.files["file"]

    if file.filename == "":

        return jsonify({
            "error": "No file selected"
        }), 400

    if not allowed_file(file.filename):

        return jsonify({
            "error": "Only PDF files are allowed"
        }), 400

    # Allow only one document to process at a time
    if not upload_lock.acquire(blocking=False):

        return jsonify({
            "error": "Another document is currently being processed. Please wait."
        }), 409

    worker_started = False
    file_path = None

    try:

        filename = secure_filename(file.filename)

        if not filename:

            return jsonify({
                "error": "Invalid filename"
            }), 400

        # Generate unique document ID
        job_id = str(uuid.uuid4())

        stored_filename = f"{job_id}_{filename}"

        file_path = os.path.join(
            UPLOAD_FOLDER,
            stored_filename
        )

        file.save(file_path)

        # Generate PDF chunks lazily
        chunk_iterator = iter(
            load_and_split_pdf(file_path, job_id)
        )

        # Read first two chunks
        first_chunks = []

        for _ in range(2):

            try:

                first_chunks.append(
                    next(chunk_iterator)
                )

            except StopIteration:

                break

        # Validate PDF content
        if not first_chunks:

            os.remove(file_path)

            return jsonify({
                "error": "No readable text found in PDF"
            }), 400

        # Register processing job
        with status_lock:

            processing_status[job_id] = {
                "status": "processing",
                "chunks_processed": 0,
                "message": "Preparing your document"
            }

            # Prevent chat against an older document
            active_document_id = None

        # Start background processing
        worker = threading.Thread(
            target=process_pdf_in_background,
            args=(
                job_id,
                first_chunks,
                chunk_iterator
            ),
            daemon=True
        )

        worker.start()

        worker_started = True

        return jsonify({

            "message": "PDF uploaded successfully",
            "filename": filename,
            "job_id": job_id,
            "document_id": job_id,
            "status": "processing"

        }), 200

    except Exception as e:

        print("Upload error:", str(e))

        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        # Background worker releases the lock
        # after processing finishes
        if not worker_started:
            upload_lock.release()


# ==========================================
# DOCUMENT STATUS API
# ==========================================

@app.route("/status/<job_id>", methods=["GET"])
def get_processing_status(job_id):

    with status_lock:

        status = processing_status.get(job_id)

        if status is not None:
            status = status.copy()

    if status is None:

        return jsonify({
            "error": "Processing job not found"
        }), 404

    return jsonify(status), 200


# ==========================================
# CHAT API
# ==========================================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True)

    if not data or not isinstance(data, dict):

        return jsonify({
            "error": "Invalid request data"
        }), 400

    question = data.get("question")

    if not isinstance(question, str) or not question.strip():

        return jsonify({
            "error": "Please provide a valid question"
        }), 400

    # Get active document
    with status_lock:

        document_id = active_document_id

        active_jobs = [
            job
            for job in processing_status.values()
            if job["status"] == "processing"
        ]

    if active_jobs:

        return jsonify({
            "error": "Please wait until document processing is complete"
        }), 409

    if not document_id:

        return jsonify({
            "error": "Please upload and process a document first"
        }), 400

    history = data.get("history", [])

    if not isinstance(history, list):
        history = []

    try:

        # Generate answer using document-specific retrieval
        result = generate_answer(
            question.strip(),
            document_id,
            history
        )

        if isinstance(result, dict):

            return jsonify({
                "answer": result.get("answer", ""),
                "sources": result.get("sources", [])
            }), 200

        return jsonify({
            "answer": result,
            "sources": []
        }), 200

    except Exception as e:

        print("Chat error:", str(e))

        return jsonify({
            "error": str(e)
        }), 500


# ==========================================
# HOME API
# ==========================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "AI RAG Chatbot Backend is running"
    })


# ==========================================
# WIDGET JAVASCRIPT API
# ==========================================

@app.route("/widget.js", methods=["GET"])
def serve_widget():

    return send_from_directory(
        WIDGET_FOLDER,
        "widget.js"
    )


# ==========================================
# WIDGET CSS API
# ==========================================

@app.route("/widget.css", methods=["GET"])
def serve_widget_css():

    return send_from_directory(
        WIDGET_FOLDER,
        "widget.css"
    )


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000,
        use_reloader=False
    )
