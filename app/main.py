from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import supabase
from pydantic import BaseModel
class RaiseUpdateRequest(BaseModel):
    version: str
    features: list[str]
    
app = FastAPI(title="Nemo Control Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.api_route("/", methods=["GET", "HEAD"])
def home():
    return {
        "status": "running",
        "service": "Nemo Control Server"
    }
    
@app.get("/version")
def get_latest_version():

    try:

        response = (
            supabase
            .table("updates")
            .select("version")
            .eq("is_latest", True)
            .single()
            .execute()
        )

        return {
            "status": "success",
            "latest_version": response.data["version"]
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }
        
@app.post("/raise-update")
def raise_update(request: RaiseUpdateRequest):

    try:

        # Make all previous versions non-latest
        supabase.table("updates") \
            .update({"is_latest": False}) \
            .eq("is_latest", True) \
            .execute()

        # Insert new version
        supabase.table("updates") \
            .insert({
                "version": request.version,
                "features": request.features,
                "is_latest": True
            }) \
            .execute()

        return {
            "status": "success",
            "message": "Update created successfully."
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }
@app.get("/update/{version}")
def get_update(version: str):

    try:

        response = (
            supabase
            .table("updates")
            .select("*")
            .eq("version", version)
            .single()
            .execute()
        )

        return {
            "status": "success",
            "data": response.data
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }