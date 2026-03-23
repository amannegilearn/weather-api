from enum import IntEnum
from typing import List,Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class Priority(IntEnum):
    LOW = 3
    MEDIUM = 2
    HIGH = 1

class TodoBase(BaseModel):
    todo_name : str = Field(..., min_length=3,max_length=512,description='Name of todo' )
    todo_description:str = Field(..., description='Description of todo')
    priority : Priority = Field(default=Priority.LOW,description='Priority of todo' )

class Todocreate(TodoBase):
        pass

class Todo(TodoBase):
    todo_id:int = Field(...,description='unique identifier ')

class Todoupdate(BaseModel):
    todo_name : Optional[str] = Field(..., min_length=3,max_length=512,description='Name of todo' )
    todo_description:Optional[str] = Field(..., description='Description of todo')
    priority : Optional[Priority] = Field(default=Priority.LOW,description='Priority of todo' )

all_todos = [
    Todo(todo_id= 1, todo_name= 'sports', todo_description= 'go to the gym',priority=Priority.HIGH),
    Todo(todo_id=2, todo_name= 'read',todo_description= 'read 10 pages',priority=Priority.LOW),
    Todo(todo_id=3, todo_name= 'shop',todo_description='go to shopping',priority=Priority.LOW),
    Todo(todo_id=4, todo_name= 'study',todo_description='study 2 hrs',priority=Priority.MEDIUM),
    Todo(todo_id= 5, todo_name ='meditate', todo_description= '5 min meditate',priority=Priority.MEDIUM)
]

@app.get('/')
def home():
    return {"message": "hello world"} 


@app.get('/todos',response_model=Todo)
def get_todos():
    return all_todos


@app.get('/todos/{todo_id}',response_model=Todo)
def get_todo(todo_id: int):
    for todo in all_todos:
        if todo.todo_id == todo_id:
            return {"result": todo}
    return {"error": "Todo not found"}

@app.post('/todos',response_model=Todo)
def create_todo(todo: Todocreate):
    new_todo_id = max(t.todo_id for t in all_todos) + 1  

    new_todo = Todo(todo_id = new_todo_id, todo_name= todo.todo_name, todo = todo.todo_description , priority=todo.priority)

    all_todos.append(new_todo)
    return new_todo

@app.put('/todos/{todo_id}',response_model=Todo)
def update_todo(todo_id: int, updated_todo: Todoupdate):
    for todo in all_todos:
        if todo.todo_id == todo_id:  
            todo.todo_name = updated_todo['todo_name']
            todo.todo_description = updated_todo['todo_description']
            return todo

    return {"error": "Todo not found"}

@app.delete('/todos/{todo_id}')
def delete_todo(todo_id: int):
    for index, todo in enumerate(all_todos):  
        if todo['todo_id'] == todo_id:
            return all_todos.pop(index)

    return {"error": "Todo not found"}