import os
from app.models.common import UPLOAD_FOLDER
def getFileName(filename, profile):
    split = filename.split(".")
    file_num = 0
    if os.path.exists(os.path.join(UPLOAD_FOLDER, profile)):
        files = os.listdir(os.path.join(UPLOAD_FOLDER, profile))
        file_num = len(files)

    return split[0] + "_" + str(file_num) + "." + split[1]