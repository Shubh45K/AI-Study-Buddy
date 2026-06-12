import os
import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify

import google.generativeai as genai

from PIL import Image
import PyPDF2
from docx import Document


# ==================================
# LOAD ENV
# ==================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(
    api_key=GEMINI_API_KEY
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# ==================================
# APP
# ==================================

app = Flask(__name__)

# ==================================
# FOLDERS
# ==================================

UPLOAD_FOLDER = "uploads"
DATABASE_FOLDER = "database"
BACKUP_FOLDER = "backup"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATABASE_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

DB_PATH = "database/chat_history.db"

# ==================================
# DATABASE
# ==================================

def create_database():

    conn = sqlite3.connect(DB_PATH)

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS chats(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            bot_response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


create_database()

# ==================================
# SAVE CHAT
# ==================================

def save_chat(user, bot):

    conn = sqlite3.connect(DB_PATH)

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO chats
        (user_message, bot_response)
        VALUES (?,?)
        """,
        (user, bot)
    )

    conn.commit()
    conn.close()


# ==================================
# BACKUP
# ==================================

def backup_chat(user, bot):

    file_path = "backup/chat_backup.json"

    data = []

    if os.path.exists(file_path):

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

        except:
            data = []

    data.append({

        "user": user,
        "bot": bot,

        "timestamp":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    })

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


# ==================================
# PDF READER
# ==================================

def read_pdf(path):

    text = ""

    with open(path, "rb") as file:

        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:

            extracted = page.extract_text()

            if extracted:
                text += extracted

    return text[:15000]


# ==================================
# DOCX READER
# ==================================

def read_docx(path):

    doc = Document(path)

    text = ""

    for para in doc.paragraphs:

        text += para.text + "\n"

    return text[:15000]


# ==================================
# TXT READER
# ==================================

def read_txt(path):

    with open(
        path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        return file.read()[:15000]


# ==================================
# GEMINI TEXT
# ==================================

def ask_gemini(prompt):

    response = model.generate_content(
        prompt
    )

    return response.text


# ==================================
# HOME
# ==================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==================================
# CHAT
# ==================================

@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    try:

        user_message = request.form.get(
            "message",
            ""
        )

        document = request.files.get(
            "document"
        )

        image = request.files.get(
            "image"
        )

        prompt = user_message

        # =========================
        # DOCUMENT PROCESSING
        # =========================

        if document:

            file_path = os.path.join(
                UPLOAD_FOLDER,
                document.filename
            )

            document.save(
                file_path
            )

            ext = document.filename.lower()

            file_text = ""

            if ext.endswith(".pdf"):

                file_text = read_pdf(
                    file_path
                )

            elif ext.endswith(".docx"):

                file_text = read_docx(
                    file_path
                )

            elif ext.endswith(".txt"):

                file_text = read_txt(
                    file_path
                )

            prompt += f"""

Analyze this study document.

{file_text}

User Question:
{user_message}

"""

        # =========================
        # IMAGE PROCESSING
        # =========================

        if image:

            image_path = os.path.join(
                UPLOAD_FOLDER,
                image.filename
            )

            image.save(
                image_path
            )

            img = Image.open(
                image_path
            )

            vision_response = model.generate_content([
                """
                Analyze this image.
                Explain the content clearly.
                Solve questions if present.
                Extract notes if possible.
                """,
                img
            ])

            ai_response = (
                vision_response.text
            )

        else:

            ai_response = ask_gemini(
                prompt
            )

        save_chat(
            user_message,
            ai_response
        )

        backup_chat(
            user_message,
            ai_response
        )

        return jsonify({

            "response":
            ai_response

        })

    except Exception as e:

        print(e)

        return jsonify({

            "response":
            f"Error: {str(e)}"

        })


# ==================================
# HISTORY
# ==================================

@app.route("/history")
def history():

    conn = sqlite3.connect(
        DB_PATH
    )

    cur = conn.cursor()

    cur.execute("""

        SELECT
        user_message,
        bot_response,
        created_at

        FROM chats

        ORDER BY id DESC

    """)

    rows = cur.fetchall()

    conn.close()

    history = []

    for row in rows:

        history.append({

            "user":
            row[0],

            "bot":
            row[1],

            "time":
            row[2]

        })

    return jsonify(history)


# ==================================
# CLEAR HISTORY
# ==================================

@app.route(
    "/clear-history",
    methods=["POST"]
)
def clear_history():

    conn = sqlite3.connect(
        DB_PATH
    )

    cur = conn.cursor()

    cur.execute(
        "DELETE FROM chats"
    )

    conn.commit()

    conn.close()

    return jsonify({

        "message":
        "History Cleared"

    })


# ==================================
# RUN
# ==================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )