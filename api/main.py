from typing import Union

from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile
from fastapi import File, UploadFile
import os
from fastapi.responses import JSONResponse

from fastapi import APIRouter, Depends, Query
from api.authentication import validate_credentials
import uuid
from inference_realesrgan import create_upscale_image

from fastapi.responses import FileResponse

# get the current working directory
BASE_DIR = os.getcwd()



app = FastAPI()


# create a fuction that genrate names the file uniquely with datetime
def generate_filename(file_name):

    file_name = file_name.lower()
    ext = file_name.split(".")[-1]
    new_file_name = str(file_name)+str(uuid.uuid4()) + "." + ext
    return new_file_name



@app.post("/upload")
def upload(file: UploadFile = File(...), outscale: int = Query(...), denoise_strength: int = Query(...),username=Depends(validate_credentials)):
    if outscale < 0:
        return JSONResponse(status_code=400, content= {"message": "Outscale must be positive"})
    if denoise_strength < 0 or denoise_strength > 1:
        return JSONResponse(status_code=400, content= {"message": "Denoise strength must be between 0 and 1"})
        # return {"message": "Denoise strength must be between 0 and 1"}

    # get the name of the file
    # try :

    save_directory = BASE_DIR+"/output_images"
    # create the directory if it doesn't exist
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)


    save_filename = generate_filename(file.filename)

    # Create the save path by joining the directory and filename
    save_path = os.path.join(save_directory, save_filename)

    with open(save_path, 'wb') as f:
        while contents := file.file.read(1024 * 1024):
            f.write(contents)


    create_upscaled_image_file_path=create_upscale_image(save_path,save_directory,"png",denoise_strength,outscale)
    res= FileResponse(create_upscaled_image_file_path)
    return res

    # except Exception:
    #     return JSONResponse(status_code=400, content= {"message": "There was an error uploading the file"})


    # finally:
    #     file.file.close()

    #     # res= FileResponse(create_upscaled_image_file_path)
    #     # # delte the files
    #     # os.remove(save_path)
    #     # # os.remove(create_upscaled_image_file_path)
    #     # return res



@app.get("/")
async def status(username=Depends(validate_credentials)):
    return {"status": "ok"}

