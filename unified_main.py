# unified_main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the two FastAPI apps from their respective modules.
# This assumes cmschat/main.py and model/main.py each have an 'app' instance.
from cmschat.main import app as cmschat_app
from model.api_with_model import app as uditi_app

# Create the unified FastAPI app. This will be the main application instance
# that the server (uvicorn) runs.
app = FastAPI(
    title="Unified Crew Chatbot API",
    description="Combines CMS Chat and UDITI APIs into one service",
    version="1.0.0"
)

# Add CORS middleware to the unified app. This is crucial for handling
# requests from different origins (e.g., a frontend application running
# on a different domain).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. For production, specify your domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the two separate applications. This means that any requests to
# `/cmschat` will be handled by the `cmschat_app`, and any requests to
# `/model` will be handled by the `uditi_app`.
# The `/uditi` endpoint in the `read_root` function has been corrected to `/model`.
app.mount("/cmschat", cmschat_app)
app.mount("/model", uditi_app)

# Root endpoint for the unified app. This is the endpoint that
# shows the status and available sub-endpoints.
@app.get("/")
def read_root():
    return {
        "message": "Unified API is running",
        "endpoints": {
            "CMS Chat API": "/cmschat",
            "UDITI API": "/model"  # Corrected endpoint to match the mounting path
        }
    }

if __name__ == "__main__":
    import uvicorn
    # This block runs the application using uvicorn when the script is executed directly.
    # The 'reload=True' flag enables automatic reloading on code changes during development.
    uvicorn.run("unified_main:app", host="127.0.0.1", port=8000, reload=True)
