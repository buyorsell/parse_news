import warnings
import fastapi
from app.parser import crawl_commersant


def warn(*args, **kwargs):
    pass


warnings.warn = warn

app = fastapi.FastAPI()

@app.get('/')
def parse():
	crawl_commersant("https://www.kommersant.ru/archive/rubric/4")
	crawl_commersant("https://www.kommersant.ru/archive/rubric/3")
	raise fastapi.HTTPException(200)
