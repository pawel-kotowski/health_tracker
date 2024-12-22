1. Install uv


Ubuntu:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. Run app

```sh
streamlit run health_tracker_streamlit.py
```