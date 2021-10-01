import models
import yfinance
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session 
from database import SessionLocal, engine
from pydantic import BaseModel
from models import Stock

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

#where are the html templates
templates = Jinja2Templates(directory= 'templates')


class StockRequest(BaseModel):
	symbol: str 

def get_db():
	try:
		db = SessionLocal()
		yield db
	finally:
		db.close()

@app.get('/')
def home(request: Request):
	"""
	displays the stock screener dashboard / homepage
	"""
	return templates.TemplateResponse('home.html',
		{'request':request,
		}
		)

#get the data from finance mag
def fetch_stock_data(id: int):
	db = SessionLocal()
	stock = db.query(Stock).filter(Stock.id == id).first()
	yahoo_data = yfinance.Ticker(stock.symbol)
	stock.ma200 = yahoo_data.info['twoHundredDayAverage']
	stock.ma50 = yahoo_data.info['fiftyDayAverage']
	stock.price = yahoo_data.info['previousClose']
	stock.forward_pe = yahoo_data.info['forwardPE']
	stock.forward_eps = yahoo_data.info['forwardEps']
	if yahoo_data.info['dividendYield'] is not None:
		stock.dividend_yield = yahoo_data.info['dividendYield'] * 100

	db.add(stock)
	db.commit()

@app.post('/stock')
async def create_stock(stock_request: StockRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
	"""
	create a stock and stores it into the database
	"""
	stock = Stock()
	stock.symbol = stock_request.symbol
	db.add(stock)
	db.commit()

	background_tasks.add_task(fetch_stock_data, stock.id)

	return {
		'code':'success',
		'message':'stock created'
	}