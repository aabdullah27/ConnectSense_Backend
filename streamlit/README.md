# ConnectSense Streamlit Frontend

This is a Streamlit-based frontend for the ConnectSense RAG system. It provides a user-friendly interface to interact with the FastAPI backend.

## Features

- Check the status of the vector index
- Ask questions about your documents
- View chat history

## Installation

1. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

1. Make sure the FastAPI backend is running:

```bash
# From the root directory
python run.py
```

2. Run the Streamlit app:

```bash
# From the streamlit directory
streamlit run app.py
```

3. Open your browser and navigate to http://localhost:8501

## Deployment

You can deploy the Streamlit app to Streamlit Cloud:

1. Push your code to a GitHub repository
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Set the main file path to `streamlit/app.py`
5. Set the environment variable `API_URL` to your FastAPI backend URL (e.g., your Vercel deployment URL)

## Configuration for Deployment

When deploying, make sure to:

1. Set the `API_URL` environment variable to point to your deployed FastAPI backend
2. If you're running locally but connecting to a deployed backend, you can enter the backend URL in the "API URL" field in the sidebar

## Configuration

If your FastAPI backend is running on a different URL, you can change the `API_URL` variable in the `app.py` file.

## Troubleshooting

- If you encounter connection errors, make sure the FastAPI backend is running and accessible.
- If the index status shows as not ready, the system may not have indexed any documents yet.
- If you're not getting relevant answers, check if your documents are properly indexed.
