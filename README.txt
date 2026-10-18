MACROSNAP - SETUP

1. Open PowerShell in this folder.
2. Create virtual environment:
   python -m venv venv

3. Activate it:
   .\venv\Scripts\Activate.ps1

4. Install packages:
   pip install -r requirements.txt

5. Create:
   .streamlit\secrets.toml

6. Copy values from:
   .streamlit\secrets.toml.example

7. Add your real Gemini and Twilio credentials.

8. Run:
   streamlit run app.py

9. Open:
   http://localhost:8501

IMPORTANT:
- Never upload .streamlit/secrets.toml to GitHub.
- The Gemini model name in app.py may need to be changed to a model
  currently available in your Google AI Studio account.
