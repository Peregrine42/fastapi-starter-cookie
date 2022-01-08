import uuid

from fastapi.param_functions import Depends
from model.user import User_Pydantic
from fastapi.params import File
from fastapi.staticfiles import StaticFiles
from fastapi import APIRouter, Request, UploadFile
from starlette import status
from starlette.responses import (
    HTMLResponse,
    RedirectResponse,
    Response,
)
from helpers.get_current_user import get_current_user

from model.file_backup import FileBackup, FileBackup_Pydantic

router = APIRouter()

router.mount("/static", StaticFiles(directory="static"), name="static")


def looper_page(request, name=None):
    message = ""
    if name:
        message = "Uploaded to: " + name

    return f"""
        <html>
            <head>
                <title>Looper</title>
            </head>

            <body>
                <div>{message}</div>
                <form enctype="multipart/form-data" method="post" action="/looper/upload">
                    <input type="hidden" name="csrftoken" value="{request.scope["csrftoken"]()}"/>  
                    <div><input name="file" type="file"></input></div>
                    <input type="submit"></input>
                </form>
            </body>
        </html>
    """


async def file_list_page(request, rows):
    files = ""
    for file in list(rows):
        files += (
            f"""<img width="50" height="50" src="/looper/files/{file.key}"></img>"""
        )

    return f"""
        <html>
            <head>
                <title>Looper</title>
            </head>

            <body>
                <div>{files}</div>
            </body>
        </html>
    """


@router.get("/", response_class=HTMLResponse)
async def get_sign_in(
    request: Request,
    current_user: User_Pydantic = Depends(get_current_user),
):
    return HTMLResponse(looper_page(request))


@router.post("/upload", response_class=HTMLResponse)
async def create_upload_file(
    request: Request,
    file: UploadFile = File(...),
    current_user: User_Pydantic = Depends(get_current_user),
):
    key = str(uuid.uuid4()) + "." + file.filename

    fb_row = FileBackup(
        key=key, content=file.file.read(), content_type=file.content_type
    )

    await fb_row.save()

    return RedirectResponse("/looper", status_code=status.HTTP_302_FOUND)


@router.get("/files/{key}")
async def get_file(
    key,
    current_user: User_Pydantic = Depends(get_current_user),
):
    fb = await FileBackup_Pydantic.from_queryset_single(FileBackup.get(key=key))

    response = Response(content=fb.content, media_type=fb.content_type)
    response.headers[
        "Content-Disposition"
    ] = f"attachment; filename={'.'.join(fb.key.split('.', 1)[1:])}"

    return response


@router.get("/files", response_class=HTMLResponse)
async def list_files(
    request: Request,
    current_user: User_Pydantic = Depends(get_current_user),
):
    rows = await FileBackup_Pydantic.from_queryset(FileBackup.all())
    return HTMLResponse(await file_list_page(request, rows))
