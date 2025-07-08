from pydantic import BaseModel
class Book(BaseModel):
    name: str
    author: str
    year_of_publication: str
    publishing_house: str
    number_of_pages: str
    description: str
    cover_image: str