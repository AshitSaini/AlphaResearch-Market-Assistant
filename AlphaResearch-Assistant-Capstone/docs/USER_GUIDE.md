# User Guide

## 1. Start the Application

Run:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

## 2. Login

Use the visible demo credentials on the login page:

- Login ID: `sainiashit31@gmail.com`
- Password: `admin@123`

## 3. Ask Questions

Type a question in the chat box and press Enter.

Example questions:

- What are the top compliance regulations critical for brokers?
- Explain T+1 settlement workflow.
- What is MTF in broking?
- What are DPDP requirements for brokers?
- How do PMLA/AML obligations apply to brokers?
- Compare equity trading and derivatives trading.

## 4. Use Follow-Up Questions

The assistant remembers the recent conversation. You can ask:

- Summarize above in 10 lines.
- Simplify this in 100 words.
- Explain the previous answer in simple language.
- Convert above into action points.

## 5. Use SOP Cards

Click an SOP card to ask about that workflow. The system sends a clean domain prompt to the backend and keeps the chat display professional.

## 6. Upload Documents

Use the upload control in the top-right area to index a circular or internal document.

Supported formats:

- PDF
- DOCX
- XLSX
- CSV
- TXT
- Markdown
- JSON
- YAML

If a PDF creates zero chunks, it is likely scanned or image-only and requires OCR before upload.

## 7. Clear Chat

Use the clear chat icon to remove the current chat history and reset the local conversation session.

## 8. Rate Responses

Use the star/rating interaction below a response. The app acknowledges the rating and treats it as quality feedback for the user experience.

## 9. Logout

Use the exit-door icon in the top-right area to return to the login screen.

## 10. Important Usage Notes

- The assistant answers using the indexed knowledge base and uploaded documents.
- For best compliance answers, ingest official SEBI/NSE/BSE/MCX circulars with metadata.
- The assistant is for educational and operational support. It is not legal, tax, investment, or regulatory approval advice.
