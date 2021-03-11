from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData

engine = create_engine('sqlite:///hello.db', echo = True)
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    conn = engine.connect()
    meta = MetaData()

    students = Table(
        'students', meta,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        Column('lastname', String),
    )
    meta.create_all(engine)
    
    ins = students.insert().values(name='Test1', lastname='Test1')
    result = conn.execute(ins)
    
    app.run(ssl_context=('adhoc'))
