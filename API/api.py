
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
import tempfile
import traceback
import uvicorn  # Required to run app in __main__
from Versioning_Analyzer import get_rich_comparision

app = FastAPI()

def save_temp_file(upload_file: UploadFile) -> str:
    suffix = os.path.splitext(upload_file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(upload_file.file, tmp)
        return tmp.name

@app.get("/")
async def health_check():
    return {"message": "Pitch Deck Comparison API is running."}

@app.post("/compare-pitch-decks")
async def compare_pitch_decks(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    allowed_types = [".pdf", ".txt", ".readme"]

    if not any(file1.filename.lower().endswith(ext) for ext in allowed_types):
        raise HTTPException(status_code=400, detail="file1 must be .pdf, .txt or .readme")
    if not any(file2.filename.lower().endswith(ext) for ext in allowed_types):
        raise HTTPException(status_code=400, detail="file2 must be .pdf, .txt or .readme")

    # Save to temp files
    file1_path = save_temp_file(file1)
    file2_path = save_temp_file(file2)

    try:
        result = get_rich_comparision(file1_path, file2_path)
        res={"summary":result}
        return JSONResponse(content=res)

    except Exception as e:
        traceback_str = traceback.format_exc()
        return JSONResponse(
            status_code=500,
            content={
                "error": "An error occurred during comparison.",
                "details": str(e),
                "trace": traceback_str
            }
        )

    finally:
        # Clean up temp files
        try:
            os.remove(file1_path)
            os.remove(file2_path)
        except Exception:
            pass  # Failsafe cleanup
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)