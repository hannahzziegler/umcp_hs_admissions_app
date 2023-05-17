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
    counties = [
        "Allegany County",
        "Anne Arundel County",
        "Baltimore County",
        "Calvert County",
        "Caroline County",
        "Carroll County",
        "Cecil County",
        "Charles County",
        "Dorchester County",
        "Frederick County",
        "Garrett County",
        "Harford County",
        "Howard County",
        "Kent County",
        "Montgomery County",
        "Prince George's County",
        "Queen Anne's County",
        "St. Mary's County",
        "Somerset County",
        "Talbot County",
        "Washington County",
        "Wicomico County",
        "Worcester County"
    ]

    if request.method == 'POST':
        search_term = request.form['search_term']
        county_filter = request.form['county']

        query = (
            Admissions
            .select()
            .where(
                (fn.lower(Admissions.school).contains(search_term.lower())) &
                (Admissions.county.contains(county_filter))
            )
            .order_by(Admissions.county, Admissions.school, Admissions.year)
        )

        results = []
        current_school = None
        current_school_results = []

        for result in query:
            if result.school != current_school:
                if current_school:
                    results.append((current_school, current_school_results))
                current_school = result.school
                current_school_results = []
            current_school_results.append(result)

        if current_school:
            results.append((current_school, current_school_results))

    else:
        results = None
        search_term = None
        county_filter = None
        # Query database for data based on search term

    return render_template('index.html', search_term=search_term, results=results, county_filter=county_filter, counties=counties)
    

if __name__ == '__main__':
    # Fire up the Flask test server
    app.run(debug=True, use_reloader=True)