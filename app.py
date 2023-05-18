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
    start_latlon = (38.6, -77)
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
            admission_data = high_schools.loc[high_schools['school'] == row['school']]
            admission_data = admission_data.loc[admission_data['year'] == '2022-23']
            
            if not admission_data.empty:
                admission_row = admission_data.iloc[0]
                applied = str(admission_row['applied'])

                applied_truncated = str(applied[:-2])
                
                folium.CircleMarker(
                    location=[row["lat"], row["lon"]],
                    radius=3,
                    color=high_schools_colors[row["classification"]],
                    fill=True,
                    fill_color=high_schools_colors[row["classification"]],
                    fill_opacity=0.5,
                    popup=f"<b>School:</b> {row['school']}<br><b>Applied:</b> {applied_truncated}<br><b>Admitted:</b> {admission_row['admitted']}<br><b>Acceptance Rate:</b> {admission_row['acceptance_rate']} <b>County:</b> {row['county']}",
                    max_width=300
                ).add_to(folium_map)

    # legend
    legend_html = """
    <div style="position: absolute; top: 10px; right: 10px; width: 150px; height: 90px;
                border:2px solid white; z-index:9999; font-size:12px;
                background-color: rgba(255, 255, 255, 0.75); font-family: 'Source Sans Pro', sans-serif;
                ">
    <div style='font-weight: bold; padding: 2px;'>School Type</div>
    <p style="margin:10px"><span style='background-color:#A5D6D9'>&nbsp;&nbsp;&nbsp;&nbsp;</span> Public</p>
    <p style="margin:10px"><span style='background-color:#DD8627'>&nbsp;&nbsp;&nbsp;&nbsp;</span> Private</p>
    </div>
    """
    folium_map.get_root().html.add_child(folium.Element(legend_html))

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

        if search_term:
            high_schools = high_schools[high_schools['school'].str.contains(search_term, case=False)]
        elif county_filter:
            high_schools = high_schools[high_schools['county'] == county_filter]

    else:
        results = None
        search_term = None
        county_filter = None
            # Query database for data based on search term


    return render_template('index.html', search_term=search_term, results=results, county_filter=county_filter, counties=counties, folium_map=folium_map._repr_html_(), high_schools=high_schools)
    

if __name__ == '__main__':
    # Fire up the Flask test server
    app.run(debug=True, use_reloader=True)