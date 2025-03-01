"""
Script to run the FastAPI server.
"""

import uvicorn
from app.main import app

# This is needed for Vercel deployment
# The app variable is imported and exposed for serverless functions

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
