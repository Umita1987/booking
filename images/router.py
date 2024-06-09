from fastapi import UploadFile, APIRouter
import shutil
from tasks.tasks import process_pic
router = APIRouter(
    prefix="/images",
    tags=["Download images"]
)

@router.post("/hotels")
async def add_hotel_image(name: int, file: UploadFile):
    im_path = f"static/images/{name}.jpg"
    with open(im_path, "wb+") as file_object:
        # Сохраняем файл в локальное хранилище (на практике обычно сохраняется в удаленное хранилище)
        shutil.copyfileobj(file.file, file_object)
    process_pic.delay(im_path)