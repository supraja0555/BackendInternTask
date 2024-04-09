from fastapi import FastAPI, HTTPException, Body, Query
from typing import List
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

client = AsyncIOMotorClient("mongodb+srv://koradasupraja5:WCgbiO6wLZci99O7@backendinterntask.byilkcs.mongodb.net/?retryWrites=true&w=majority&appName=BackendInternTask")
db = client["students_db"]
collection = db["students"]

class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str = Field(..., description="Name of the student")
    age: int = Field(..., gt=0, description="Age of the student")
    address: Address = Field(..., description="Address of the student")

@app.post("/students", status_code=201, response_model=dict, summary="Create Students", description="API to create a student in the system. All fields are mandatory and required while creating the student in the system.")
async def create_student(student: Student = Body(..., description="Student details")):
    """
    Create Students:
    API to create a student in the system.
    """
    inserted_student = collection.insert_one(student.dict())
    return {"id": str(inserted_student.inserted_id)}

@app.get("/students", response_model=List[Student], summary="List students", description="An API to find a list of students. You can apply filters on this API by passing the query parameters as listed below.")
async def list_students(country: str = Query(None, description="To apply filter of country. If not given or empty, this filter should be applied."), age: int = Query(None, description="Only records which have age greater than equal to the provided age should be present in the result. If not given or empty, this filter should be applied.")):
    """
    List students:
    An API to find a list of students.
    """
    query = {}
    if country:
        query["address.country"] = country
    if age is not None:
        query["age"] = {"$gte": age}
    students = list(collection.find(query, {"_id": 0}))
    return students

@app.get("/students/{id}", response_model=Student, summary="Fetch student", description="API to fetch details of a specific student based on the provided ID.")
async def get_student(id: str):
    """
    Fetch student:
    API to fetch details of a specific student based on the provided ID.
    """
    student = collection.find_one({"_id": id}, {"_id": 0})
    if student:
        return student
    else:
        raise HTTPException(status_code=404, detail="Student not found")

@app.patch("/students/{id}", status_code=204, summary="Update student", description="API to update the student's properties based on information provided. Not mandatory that all information would be sent in PATCH, only what fields are sent should be updated in the Database.")
async def update_student(id: str, student: Student = Body(..., description="Updated student details")):
    """
    Update student:
    API to update the student's properties based on information provided.
    """
    updated_student = collection.update_one({"_id": id}, {"$set": student.dict()})
    if updated_student.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

@app.delete("/students/{id}", status_code=200, summary="Delete student", description="API to delete a student based on the provided ID.")
async def delete_student(id: str):
    """
    Delete student:
    API to delete a student based on the provided ID.
    """
    deleted_student = collection.delete_one({"_id": id})
    if deleted_student.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    else:
        return {"message": "Student deleted successfully"}