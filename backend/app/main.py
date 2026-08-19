from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.linear_model import LinearRegression
import numpy as np
app=FastAPI(title='MealMind Demo API')
inventory=[{'ingredient':'Rice','current_stock':35,'forecasted_requirement':56},{'ingredient':'Tomatoes','current_stock':12,'forecasted_requirement':28},{'ingredient':'Milk','current_stock':15,'forecasted_requirement':42}]
@app.get('/api/inventory')
def get_inventory(): return inventory
@app.get('/api/procurement')
def procurement(): return [{**i,'recommended_purchase':max(i['forecasted_requirement']-i['current_stock'],0)} for i in inventory]
@app.get('/api/spoilage')
def spoilage(): return [{'ingredient':'Milk','risk_score':95,'risk_level':'Critical'},{'ingredient':'Tomatoes','risk_score':82,'risk_level':'High'}]
@app.get('/api/waste-patterns')
def waste(): return {'weekly_waste_kg':186,'estimated_cost':14880,'highest_day':'Sunday','highest_meal':'Dinner'}
historical_demand={
 'Breakfast':[218,225,209,238,245,232,249,254,240,260,252,267,258,273],
 'Lunch':[302,318,291,336,347,328,355,366,342,372,360,381,369,390],
 'Dinner':[264,278,255,295,305,289,312,321,300,328,317,336,324,343],
}
def linear_regression_forecast(values,horizon):
    """A small, explainable time-index Linear Regression forecast for the MVP."""
    values=np.asarray(values,dtype=float)
    if len(values)<2:
        baseline=round(float(values.mean())) if len(values) else 0
        return [baseline]*horizon,'moving_average'
    x=np.arange(len(values)).reshape(-1,1)
    model=LinearRegression().fit(x,values)
    future=np.arange(len(values),len(values)+horizon).reshape(-1,1)
    return [max(0,round(float(value))) for value in model.predict(future)],'linear_regression'
@app.get('/api/forecast')
def forecast(meal:str='Lunch',horizon:int=7):
    horizon=max(1,min(horizon,14)); history=historical_demand.get(meal,historical_demand['Lunch'])
    predictions,method=linear_regression_forecast(history,horizon)
    return {'meal':meal,'horizon':horizon,'historical':history,'predictions':predictions,'next_day':predictions[0],'average':round(sum(predictions)/len(predictions)),'confidence':'87%','model':'Linear Regression' if method=='linear_regression' else 'Moving Average fallback'}
class Scenario(BaseModel): customers:int=300;procurement_adjustment:float=0;preparation_adjustment:float=0;demand_change:float=0
@app.post('/api/simulator')
def simulate(s:Scenario):
 d=round(s.customers*(1+s.demand_change/100));p=round(d*(1+s.preparation_adjustment/100));w=max(0,round((p-d)*.36));return {'estimated_meal_demand':d,'expected_waste_kg':w,'estimated_waste_cost':w*80}
