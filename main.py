from logging import error
from fastapi import FastAPI, File, UploadFile
from fastapi import FastAPI, HTTPException, responses
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import os
import uuid
from pathlib import Path
import threading
import logging
from file_processing import file_process, getCompanyInfo

app = FastAPI()
origins = ["*"]

get_company_info_thread= threading.Thread(target=getCompanyInfo, args=())
logging.info("Starting getCompanyInfo Thread")
get_company_info_thread.start()

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)


@app.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...)):
    error = None
    try:
        ext = file.filename.split(".")[-1]
        if ext == "csv":
            random_uuid = uuid.uuid4()
            if not os.path.exists("tmp"):
                os.makedirs("tmp")
            file_location = "tmp/"+str(random_uuid)+".csv"
            with open(file_location, "wb+") as file_object:
                shutil.copyfileobj(file.file, file_object)
            file_process.put(file_location)
        else:
            error = "File is not Supported"  
    except IOError:
        error = "Could not open/read file: "+ file.filename+" "+file_location
    if error is not None:
        return {"error":error}
    return {"file_token_id":str(random_uuid)}

@app.get("/file/{token_id}")
async def file_read(token_id: str):
    try:
        if token_id:
            ipath = Path("tmp/"+str(token_id)+".csv")
            print(str(ipath))
            if os.path.isfile(ipath):
                return {"message": "File is still in processed"}
            else:
                opath = Path("output/out_"+str(token_id)+".csv")
                print(str(opath))
                if os.path.isfile(opath):
                    response = FileResponse(opath, media_type="text/csv")
                    response.headers["Content-Disposition"] = "attachment;filename=updated_"+token_id+".csv"
                    return response 
                   
                else:
                    return {"message": "file associated to token not exist"}
        
    except Exception as e:
        return {"error":str(e)}
    