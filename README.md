# StudyFlow AI

A Streamlit study planner app.

## Run locally

```bash
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

## Deploy

1. Create a GitHub repository.
2. Upload `app.py`, `requirements.txt`, `.gitignore`, and this README.
3. Open https://share.streamlit.io and sign in with GitHub.
4. Create an app, select the repository, branch `main`, and entrypoint `app.py`.
5. Deploy.

Do not commit API keys, `.streamlit/secrets.toml`, or `studyflow_data.json`.

## Important deployment notes

- This version asks for a Gemini API key in the app sidebar. Do not put a key in the source code or GitHub.
- The app currently stores task data in a local JSON file. Streamlit Community Cloud does not guarantee local-file persistence. This version is suitable for a demo, but add a persistent database and per-user authentication/data separation before inviting multiple people to use it with personal tasks.
