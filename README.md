```markdown
# Salary Visualizer — Streamlit app

What this repo contains
- app.py — the Streamlit app (point Streamlit Cloud to this file)
- requirements.txt — dependencies for Streamlit Cloud
- runtime.txt — pin Python runtime (optional but recommended)
- .streamlit/config.toml — app preferences (theme, server flags)
- .gitignore — recommended ignores

Run locally
1. python -m venv .venv
2. source .venv/bin/activate   # macOS/Linux
   .venv\Scripts\activate      # Windows
3. pip install -r requirements.txt
4. streamlit run app.py

Deploy to Streamlit Cloud
1. Push this repository to GitHub.
2. Go to https://streamlit.io/cloud and sign in with GitHub.
3. Click "New app".
4. Select the repository, branch, and set the main file to `app.py`.
5. Click "Deploy".

Notes & tips
- PNG export: Plotly's fig.to_image() requires the `kaleido` package; include it in requirements.txt (already included).
- Secrets: Add any API keys or credentials in the Streamlit Cloud app settings -> Secrets; access them in code with `st.secrets["MY_KEY"]`.
- Private repo: Streamlit Cloud supports private repos on paid plans — check your plan.
- Logs: use the app's Logs page on Streamlit Cloud for runtime errors.
```
