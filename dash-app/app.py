import pandas as pd
from dash import Dash, html, dcc
import dash_ag_grid as dag
import plotly.express as px
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "parks_and_open_space.csv"

df = pd.read_csv(DATA_FILE)
df.columns = [col.strip() for col in df.columns]

# Try to find likely columns for park name and area
name_col = "Park Name"
area_col = "Total Area in Hectares"

# Make sure the area column is numeric for graphing
df[area_col] = pd.to_numeric(df[area_col], errors="coerce")

# Create a bar graph of the top 10 largest parks by area
graph_df = df[[name_col, area_col]].dropna().sort_values(by=area_col, ascending=False).head(10)

fig = px.bar(
    graph_df,
    x=name_col,
    y=area_col,
    title="Top 10 Largest Parks / Open Spaces by Area"
)

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Winnipeg Parks and Open Space Dashboard"),

    html.H3("Dataset Grid"),
    dag.AgGrid(
        rowData=df.to_dict("records"),
        columnDefs=[{"field": col} for col in df.columns],
        defaultColDef={
            "sortable": True,
            "filter": True,
            "resizable": True
        },
        style={"height": "500px", "width": "100%"},
    ),

    html.H3("Meaningful Graph"),
    dcc.Graph(figure=fig)
])

if __name__ == "__main__":
    app.run(debug=True)