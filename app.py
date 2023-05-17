from flask import Flask, render_template, request
from peewee import *
app = Flask(__name__)

db = SqliteDatabase('high_school_admissions.db')

class Admissions(Model):
    id = IntegerField(unique=True)
    school_id = IntegerField()
    school = CharField()
    year = CharField()
    applied = CharField()
    admitted = CharField()
    acceptance_rate = CharField()
    lat = IntegerField()
    lon = IntegerField()
    city = CharField()
    county = CharField()
    state = CharField()
    zip = CharField()
    classification = CharField()

    class Meta:
        table_name = "admissions"
        database = db

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_term = request.form['search_term']
        query = (
            Admissions
            .select()
            .where(fn.lower(Admissions.school).contains(search_term.lower()))
            .order_by(Admissions.year)
        )
        results = list(query)
    else:
        results = None
        search_term = None
        # Query database for data based on search term

    return render_template('index.html', search_term=search_term, results=results)
    

if __name__ == '__main__':
    # Fire up the Flask test server
    app.run(debug=True, use_reloader=True)