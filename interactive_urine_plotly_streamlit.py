import streamlit as st
import plotly as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

def read_data(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    sodium_data, urine_data, desmopressin_data = [], [], []
    current_data = None

    for line in lines:
        line = line.strip()
        if 'SODIUM LEVEL' in line:
            current_data = sodium_data
        elif 'Urine Voided Volume' in line or 'Urine Output' in line:
            current_data = urine_data
        elif 'desmopressin' in line:
            current_data = desmopressin_data
        elif current_data is not None and line:
            current_data.append(line)

    return sodium_data, urine_data, desmopressin_data

def process_data(data):
    dates, values = [], []
    for line in data:
        if line:
            parts = line.split()
            try:
                date = datetime.strptime(parts[0] + ' ' + parts[1], "%m/%d/%Y %H:%M")
            except ValueError:
                continue

            value = float(parts[2])
            dates.append(date)
            values.append(value)
    return dates, values

# Read and process data from the file
sodium_data, urine_data, desmopressin_data = read_data("moredata.txt")
sodium_dates, sodium_values = process_data(sodium_data)
urine_dates, urine_volumes = process_data(urine_data)
desmopressin_dates, desmopressin_doses = process_data(desmopressin_data)

# Create DataFrames
sodium_df = pd.DataFrame({'Date': sodium_dates, 'Level': sodium_values})
urine_df = pd.DataFrame({'Date': urine_dates, 'Volume': urine_volumes})
desmopressin_df = pd.DataFrame({'Date': desmopressin_dates, 'Dose': desmopressin_doses})

# Create a Plotly figure
fig = go.Figure()

# Add Urine Volume trace (interactive)
fig.add_trace(go.Scatter(x=urine_df['Date'], y=urine_df['Volume'],
                         mode='markers+lines',
                         name='Urine Voided Volume',
                         hoverinfo='y+x'))

# Add Sodium Level bars on secondary y-axis
fig.add_trace(go.Bar(x=sodium_df['Date'], y=sodium_df['Level'],
                     name='Sodium Level',
                     marker_color='green',
                     yaxis='y2'))

# Add Desmopressin Doses as vertical lines
for date, dose in zip(desmopressin_df['Date'], desmopressin_df['Dose']):
    fig.add_trace(go.Scatter(x=[date, date], y=[0, max(urine_df['Volume'])],
                             mode='lines', line=dict(color='red', width=2, dash='dash'),
                             name=f'Desmopressin {dose} microgram'))

# Update layout with a secondary y-axis for Sodium Level
fig.update_layout(
    title='Urine Output, Desmopressin Dose, and Sodium Levels Over Time',
    xaxis_title='Date',
    yaxis_title='Urine Volume (mL)',
    yaxis2=dict(
        title='Sodium Level',
        overlaying='y',
        side='right',
        range=[130, 160]
    ),
    hovermode='closest',
    barmode='group'
)

st.plotly_chart(fig)

# Show plot
#fig.show()

# Save the plot as an HTML file
#fig.write_html("urine_output_plot.html")
