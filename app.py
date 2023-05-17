from flask import Flask, render_template, request
from peewee import *
import csv
import folium
from folium import plugins
import pandas as pd
import numpy as np
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

    # load data
    high_schools = pd.read_csv('static/db_hs_umcp.csv')

    # folium map basics
    start_latlon = (38.3, -76.6413)
    folium_map = folium.Map(
        location=start_latlon, 
        zoom_start=8,
        tiles="CartoDB Positron",

    )

    # color dictionary
    high_schools_colors = {
        school: color 
        for school, color in zip(high_schools["classification"].unique(), ["#A5D6D9", "#DD8627"])  # Default color for missing values (NaN))
    }

    default_color = "#FFFFFF"  # Default color for missing values (NaN)
    high_schools_colors[np.nan] = default_color

    # markers + popups
    for index, row in high_schools.iterrows():
        if pd.notnull(row["lat"]) and pd.notnull(row["lon"]):
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=4,
                color=high_schools_colors[row["classification"]],
                fill=True,
                fill_color=high_schools_colors[row["classification"]],
                fill_opacity = 0.5,
                popup = f"<b>School:</b> {row['school']}<br><b>Applied:</b> {row['applied']}<br><b>Admitted:</b> {row['admitted']}<br><b>Acceptance Rate:</b> {row['acceptance_rate']} <b>County:</b> {row['county']}", max_width=300).add_to(folium_map)

    # legend
    legend_css = """
<style>
    .leaflet-control-attribution {
        background-color: transparent;
        height: auto;
        line-height: normal;
    }
</style>
"""

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

    return render_template('index.html', search_term=search_term, results=results, county_filter=county_filter, counties=counties, folium_map=folium_map._repr_html_())
    

if __name__ == '__main__':
    # Fire up the Flask test server
    app.run(debug=True, use_reloader=True)