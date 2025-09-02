from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
import json
app = FastAPI()
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal


class Patient(BaseModel):
    id: Annotated[str, Field(..., description="Id is Required", examples=['P001'])]
    name: Annotated[str, Field(..., description="Name of the Patient")]
    city: Annotated[str, Field(..., description="City where the Patient is living ")]
    age: Annotated[int, Field(..., gt=0, lt=100, description="Age is required for this")]
    gender: Annotated[Literal['male', 'female'], Field(..., description="Please enter the Gender")]
    height: Annotated[float, Field(..., gt=0, description="Height is Required")]
    weight: Annotated[float, Field(..., gt=0, description="Weight is required")]
    
    @computed_field
    @property
    def bmi(self)-> float:
        bmi = round(self.weight/(self.height)**2, 2)
        return bmi
    
    
    @computed_field
    @property
    def verdict(self)-> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 24:
            return "normal"
        elif self.bmi > 24.5 & self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"
        
        
def load():
    with open('patients.json', 'r') as f:
        data = json.load(f)
        return data
def save(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)    
    
@app.get("/")
def hello():
    return {'message': 'Hello FastAPI'}

@app.get("/about")
def about():
    return {"Message": "Aarish is a fast Learner"}

@app.get("/timepass")
def timepass():
    return {'Time-Pass': 'Watching Reels in Instagram'}

@app.get("/view")
def view():
    data = load()
    return data

@app.get("/patient/{patient_id}")
def getPatientById(patient_id: str = Path(..., description='Please Enter the Patient ID', example="P001")):
    data = load()
    
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Error No Patient is available with this ID")

@app.get("/sort")
def sort(sort_by: str = Query(..., description="It can be height, weight, or bmi"), order: str = Query(description="asc or desc")):
    if sort_by not in ['height', 'weight', 'bmi']:
        raise HTTPException(status_code=400, detail="Please enter a valid data")
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail="Please enter a valid order")

    data = load()
    
    sorted_order = True if order=='desc' else False
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sorted_order )

    return sorted_data

@app.post("/create")
def create(patient:Patient):
    #loading the data
    data = load()
    
    # check for the existing ID
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Id Already exist")
    
    #add in the patient
    data[patient.id] = patient.model_dump(exclude=['id'])

    #saving the patient
    save(data)
    
    return JSONResponse(status_code=200, content={'message': 'successfully saved the data in the database'})


#update patient

#delete
@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    data = load()
    
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    del data[patient_id]
    
    return JSONResponse(status_code=200, content={'message': 'Successfully deleted the patient'})