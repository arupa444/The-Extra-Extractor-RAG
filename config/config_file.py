import os

class Config:

    @staticmethod
    def makeDirectories(dirName: str) -> None:
        os.makedirs(dirName, exist_ok=True)