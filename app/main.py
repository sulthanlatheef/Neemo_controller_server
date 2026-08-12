from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import supabase
from pydantic import BaseModel
class RaiseUpdateRequest(BaseModel):
    version: str
    features: list[str]
class RaiseUpdateRequest(BaseModel):
    version: str
    features: list[str]


class RequestCountRequest(BaseModel):
    user_id: str
    count: int
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
@app.post("/sync-request-count")
def sync_request_count(request: RequestCountRequest):

    try:

        from datetime import date

        today = date.today().isoformat()

        # --------------------------------------------------------
        # CHECK TODAY'S EXISTING ROW
        # --------------------------------------------------------

        response = (
            supabase
            .table("daily_request_counts")
            .select("*")
            .eq("user_id", request.user_id)
            .eq("date", today)
            .execute()
        )

        existing_rows = response.data or []

        # --------------------------------------------------------
        # UPDATE EXISTING ROW
        # --------------------------------------------------------

        if len(existing_rows) > 0:

            existing_data = existing_rows[0]

            new_count = (
                existing_data["total_requests"]
                + request.count
            )

            (
                supabase
                .table("daily_request_counts")
                .update({
                    "total_requests": new_count
                })
                .eq("user_id", request.user_id)
                .eq("date", today)
                .execute()
            )

            return {
                "status": "success",
                "message": "Request count updated.",
                "total_requests": new_count
            }

        # --------------------------------------------------------
        # CREATE NEW ROW
        # --------------------------------------------------------

        supabase.table(
            "daily_request_counts"
        ).insert({
            "user_id": request.user_id,
            "total_requests": request.count,
            "date": today
        }).execute()

        return {
            "status": "success",
            "message": "Request count created.",
            "total_requests": request.count
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }
@app.get("/get_neemo_user_name/{user_id}")
def get_neemo_user_name(user_id: str):

    try:

        response = (
            supabase
            .table("neemo_user_info")
            .select("user_name, actual_name")
            .eq("user_id", user_id.upper())
            .single()
            .execute()
        )

        if not response.data:
            return {
                "status": "error",
                "message": "User not found."
            }

        return {
            "status": "success",
            "data": {
                "user_name": response.data["user_name"],
                "actual_name": response.data["actual_name"]
            }
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }