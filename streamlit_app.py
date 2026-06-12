import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
from docx import Document
import io

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
    layout="wide"
)

# =========================
# GEMINI CONFIG
# =========================

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel(
    "gemini-1.5-flash"
)

# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>

.main{
    padding-top:20px;
}

.block-container{
    max-width:1200px;
}

.feature-card{
    background:#1f2937;
    padding:20px;
    border-radius:15px;
    text-align:center;
    color:white;
}

</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================

with st.sidebar:

    st.title("AI Study Buddy")

    st.markdown("---")

    action = st.radio(
        "Study Tools",
        [
            "Chat",
            "Summary",
            "Quiz",
            "Flashcards",
            "Explain"
        ]
    )

    st.markdown("---")

    uploaded_pdf = st.file_uploader(
        "Upload Document",
        type=["pdf","docx","txt"]
    )

    uploaded_image = st.file_uploader(
        "Upload Image",
        type=["png","jpg","jpeg"]
    )

# =========================
# TITLE
# =========================

st.title("AI Study Buddy")

st.caption(
    "Upload notes, create quizzes, flashcards and learn faster using AI."
)

# =========================
# FEATURE CARDS
# =========================

c1,c2,c3,c4 = st.columns(4)

with c1:
    st.info("Summary")

with c2:
    st.info("Quiz")

with c3:
    st.info("Flashcards")

with c4:
    st.info("Explain")

# =========================
# CHAT HISTORY
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# READ DOCUMENT
# =========================

document_text = ""

if uploaded_pdf:

    if uploaded_pdf.name.endswith(".pdf"):

        pdf_reader = PyPDF2.PdfReader(
            uploaded_pdf
        )

        for page in pdf_reader.pages:

            text = page.extract_text()

            if text:
                document_text += text

    elif uploaded_pdf.name.endswith(".txt"):

        document_text = uploaded_pdf.read().decode(
            "utf-8"
        )

    elif uploaded_pdf.name.endswith(".docx"):

        doc = Document(uploaded_pdf)

        document_text = "\n".join(
            [p.text for p in doc.paragraphs]
        )

# =========================
# IMAGE PREVIEW
# =========================

if uploaded_image:

    image = Image.open(uploaded_image)

    st.image(
        image,
        use_container_width=True
    )

# =========================
# CHAT DISPLAY
# =========================

for msg in st.session_state.messages:

    with st.chat_message(
        msg["role"]
    ):
        st.write(
            msg["content"]
        )

# =========================
# PROMPT
# =========================

prompt = st.chat_input(
    "Ask anything about your studies..."
)

if prompt:

    # User Message

    st.session_state.messages.append(
        {
            "role":"user",
            "content":prompt
        }
    )

    with st.chat_message("user"):
        st.write(prompt)

    # =========================
    # ACTION PROMPTS
    # =========================

    final_prompt = prompt

    if document_text:

        if action == "Summary":

            final_prompt = f"""
            Summarize this document:

            {document_text}
            """

        elif action == "Quiz":

            final_prompt = f"""
            Generate 10 MCQ quiz questions
            from this document:

            {document_text}
            """

        elif action == "Flashcards":

            final_prompt = f"""
            Create flashcards from:

            {document_text}
            """

        elif action == "Explain":

            final_prompt = f"""
            Explain this document
            in simple language:

            {document_text}
            """

    # =========================
    # GEMINI RESPONSE
    # =========================

    with st.spinner(
        "Thinking..."
    ):

        try:

            response = model.generate_content(
                final_prompt
            )

            answer = response.text

        except Exception as e:

            answer = f"Error: {e}"

    with st.chat_message(
        "assistant"
    ):
        st.write(answer)

    st.session_state.messages.append(
        {
            "role":"assistant",
            "content":answer
        }
    )