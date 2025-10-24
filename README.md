# Flask Text Tool (TensorFlow backend)

## Features
- Register & Login (no SQL; users stored in users.json)
- Protected tool page with Summarize & Paraphrase (uses T5 via TensorFlow)
- Bootstrap 5 UI

## Run
1. Create venv:
   python -m venv venv
   source venv/bin/activate    # Linux / macOS
   venv\Scripts\activate     # Windows

2. Install requirements:
   pip install -r requirements.txt

3. Run:
   python app.py

4. Open http://127.0.0.1:5000

**Notes**
- The first time you use Summarize/Paraphrase, transformers will download the T5 model (few hundred MB).
- If you face memory or GPU issues, consider using `t5-small` (we already use t5-small) or a rule-based fallback.
