# Link Biter
# For usage read README.md
#
# Made by Frankom
#

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import sqlite3
import re
import validators

connection = sqlite3.connect('database.db')
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS links(url text, alias text)")
connection.commit()

app = FastAPI(docs_url=None, redoc_url=None)

class Link(BaseModel):
    url: str
    alias: str

with open('index.html', 'r') as f:
    html_conent = f.read()

@app.get('/', response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=html_conent, status_code=200)

@app.post('/api/cut')
async def cut(data: Link):
    if bool(re.match('^[a-zA-Z0-9]*$', data.alias)) and validators.url(data.url):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        if data.alias == '404' or cursor.execute("SELECT url FROM links WHERE alias = ?", (data.alias,)).fetchone() != None:
            connection.commit()
            return {'err':2}
        else:
            cursor.execute("INSERT INTO links VALUES(?,?)", (data.url, data.alias))
            connection.commit()
        #return {"url: "+data.url, "alias: "+data.alias}
        return {'err':0}
    else:
        return {'err':1}

@app.get('/404')
async def error():
    return HTMLResponse(content="<body style='background-color: darkgoldenrod;'><h2>not found</h2></body>", status_code=404)

@app.get('/{alias}', response_class=RedirectResponse)
async def redirect(alias: str):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    link = cursor.execute("SELECT url FROM links WHERE alias = ?", (alias,)).fetchone()
    if link == [] or link == None:
        return './404'
    else:
        return link[0]