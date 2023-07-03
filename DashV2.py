import base64
import dash
from dash import html, dcc, ctx
from dash.dependencies import Input, Output, State
import pandas as pd
import csv
import xml.etree.ElementTree as ET

def update_svg(svg_path, csv_path):
    # Read the CSV file
    county_data = {}
    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            fips_code = row[1]
            result = row[2] if len(row) > 1 else ''
            county_data[fips_code] = result

    # Parse the SVG file
    tree = ET.parse(svg_path)
    root = tree.getroot()

    # Add fill clause to the style of each path
    for path in root.findall('.//{http://www.w3.org/2000/svg}path'):
        fips_code = path.get('id')[1:]
        if fips_code in county_data:
            result = county_data[fips_code]
            fill_color = get_fill_color(result)
            style = path.get('style')
            new_style = f"{style};fill:{fill_color}"
            path.set('style', new_style)

    # Write the modified SVG file
    modified_svg_path = svg_path.replace('.svg', '_modified.svg')
    tree.write(modified_svg_path, encoding='UTF-8', xml_declaration=True)

def get_fill_color(result):
    color_scale = {
        0.01: '#e0e0ff',
        0.025: '#bfbfef',
        0.05: '#a3a3e0',
        0.075: '#8585d1',
        0.1: '#6666c1',
        0.15: '#4848b4',
        0.2: '#2727a3',
        0.25: '#050593',
        0.3334: '#000082',
        0.5: '#00006e',
        0.75: '#00005a',
        1.0: '#00004b',
        1.01: '#ffe0e0',
        1.025: '#efbfbf',
        1.05: '#e0a3a3',
        1.075: '#d18585',
        1.1: '#c16666',
        1.15: '#b24747',
        1.2: '#a32727',
        1.25: '#930505',
        1.3334: '#7f0000',
        1.5: '#6d0000',
        1.75: '#590000',
        2.0: '#490000',
        2.01: '#e0ffe0',
        2.025: '#bbeabb',
        2.05: '#a0dba0',
        2.075: '#84cc84',
        2.1: '#64bc64',
        2.15: '#46Af46',
        2.2: '#259e25',
        2.25: '#058e05',
        2.3334: '#007c00',
        2.5: '#006b00',
        2.75: '#005600',
        float('inf'): '#004700'
    }
    
    result = float(result)
    for limit, color in color_scale.items():
        if result <= limit:
            return color
    return '#ffffff'

svg_file_path = '/Users/andrewpark/Desktop/Personal/Code/Politics/countychange.svg'
csv_file_path = '/Users/andrewpark/Desktop/Personal/Code/Politics/results.csv'

df1 = pd.read_csv("/Users/andrewpark/Desktop/Personal/Code/Politics/DS68.csv")
df2 = pd.read_csv("/Users/andrewpark/Desktop/Personal/Code/Politics/RS68.csv")
df3 = pd.read_csv("/Users/andrewpark/Desktop/Personal/Code/Politics/OS68.csv")

dem_corrdf = pd.read_csv("/Users/andrewpark/Desktop/Personal/Code/Politics/DC68.csv")
gop_corrdf = pd.read_csv("/Users/andrewpark/Desktop/Personal/Code/Politics/RC68.csv")
oth_corrdf = pd.read_csv("/Users/andrewpark/Desktop/Personal/Code/Politics/OC68.csv")

df_fips = pd.read_csv("/Users/andrewpark/Desktop/Personal/Code/Politics/ALtoIA.csv")
df4 = pd.read_csv("/Users/andrewpark/Desktop/Personal/Code/Politics/2020Data.csv", dtype={"county_fips": str})

dem_array, gop_array, oth_array = df1.values.tolist(), df2.values.tolist(), df3.values.tolist()
dem_array2, gop_array2, oth_array2 = dem_corrdf.values.tolist(), gop_corrdf.values.tolist(), oth_corrdf.values.tolist()
for i in range(len(dem_array2)):
    del dem_array2[i][0]
    del gop_array2[i][0]
    del oth_array2[i][0]

fips_codes = df_fips.values.tolist()
final_fips = [item for sublist in fips_codes for item in sublist]
for i in range(len(final_fips)):
    if (final_fips[i] < 10000):
        final_fips[i] = "0" + str(final_fips[i])
    else:
        final_fips[i] = str(final_fips[i])

fips_states = {"Alabama": "01","Alaska":"02",
"Arizona": "04",
"Arkansas": "05",
"California": "06",
"Colorado": "08",
"Connecticut": "09",
"Delaware": "10",
"DC": "11",
"Florida": "12",
"Georgia": "13",
"Hawaii": "15",
"Idaho": "16",
"Illinois": "17",
"Indiana": "18",
"Iowa": "19",
"Kansas": "20",
"Kentucky": "21",
"Louisiana": "22",
"Maine": "23",
"Maryland": "24",
"Massachusetts": "25",
"Michigan": "26",
"Minnesota": "27",
"Mississippi": "28",
"Missouri": "29",
"Montana": "30",
"Nebraska": "31",
"Nevada": "32",
"New Hampshire": "33",
"New Jersey": "34",
"New Mexico": "35",
"New York": "36",
"North Carolina": "37",
"North Dakota": "38",
"Ohio": "39",
"Oklahoma": "40",
"Oregon": "41",
"Pennsylvania": "42",
"Rhode Island": "44",
"South Carolina": "45",
"South Dakota": "46",
"Tennessee": "47",
"Texas": "48",
"Utah": "49",
"Vermont": "50",
"Virginia": "51",
"Washington": "53",
"West Virginia": "54",
"Wisconsin": "55",
"Wyoming": "56",}
demdata, gopdata, othdata = df4['per_dem'].tolist(), df4['per_gop'].tolist(), df4['per_oth'].tolist()
demswing_amounts, gopswing_amounts, othswing_amounts = [], [], []

def generate_svg_image(svg_code):
    return f"data:image/svg+xml;base64,{base64.b64encode(svg_code.encode()).decode()}"

app = dash.Dash(__name__)

# Default input values
correlation_threshold = 0.5
state = "Your State"
county = "Your County"
dem_swing = 0.0
rep_swing = 0.0
oth_swing = 0.0
swing_counties = []

# Callback to update SVG image and input values
@app.callback(
    Output('svg-image', 'src'),
    Output('correlation-threshold', 'value'),
    Output('state', 'value'),
    Output('county', 'value'),
    Output('dem-swing', 'value'),
    Output('rep-swing', 'value'),
    Output('oth-swing', 'value'),
    Input('submit-button', 'n_clicks'),
    Input('session-button', 'n_clicks'),
    Input('reset-button','n_clicks'),
    State('correlation-threshold', 'value'),
    State('state', 'value'),
    State('county', 'value'),
    State('dem-swing', 'value'),
    State('rep-swing', 'value'),
    State('oth-swing', 'value')
)

def update_svg_image(button1, button2, button3, threshold, state_input, county_input, dem_input, rep_input, oth_input):
    global swing_counties
    global demdata
    global gopdata
    global othdata
    if ctx.triggered_id is None:
        return dash.no_update, correlation_threshold, state, county, dem_swing, rep_swing, oth_swing
    if ctx.triggered_id == 'session-button':
        swing_counties = []
        demdata, gopdata, othdata = findemdata.copy(), fingopdata.copy(), finothdata.copy()
        demtemp, goptemp, othtemp = findemdata.copy(), fingopdata.copy(), finothdata.copy()
        margin, margin2 = [0]*len(findemdata), [0]*len(findemdata)

        for i in range(len(findemdata)): # for EACH of ALL county
            margin[i] = max(findemdata[i], fingopdata[i], finothdata[i]) - (1-max(findemdata[i], fingopdata[i], finothdata[i])-min(findemdata[i], fingopdata[i], finothdata[i]))
            if max(findemdata[i], fingopdata[i], finothdata[i]) == findemdata[i]:
                margin2[i] = min(1,margin[i])
            elif max(findemdata[i], fingopdata[i], finothdata[i]) == fingopdata[i]:
                margin2[i] = min(2,margin[i]+1) # gop = +1
            else:
                margin2[i] = min(3,margin[i]+2)  # ind = +2
        
        df5 = {"fips": final_fips, "margin": margin2}
        dict2 = pd.DataFrame(df5)
        dict2.to_csv("results.csv")
        update_svg(svg_file_path, csv_file_path)
        
        with open('/Users/andrewpark/Desktop/Personal/Code/Politics/countychange_modified.svg', 'r') as file:
            svg_code = file.read()

        updated_svg_code = svg_code

        src = generate_svg_image(updated_svg_code)
        return src, threshold, state_input, county_input, dem_input, rep_input, oth_input 
    if ctx.triggered_id == 'reset-button':
        correlation_threshold = 0
        state = "Alabama"
        county = "Autauga"
        dem_swing = 0.0
        rep_swing = 0.0
        oth_swing = 0.0
        swing_counties = []
        findemdata, fingopdata, finothdata = df4['per_dem'].tolist(), df4['per_gop'].tolist(), df4['per_oth'].tolist()
        margin, margin2 = [0]*len(findemdata), [0]*len(findemdata)

        for i in range(len(findemdata)): # for EACH of ALL county
            margin[i] = max(findemdata[i], fingopdata[i], finothdata[i]) - (1-max(findemdata[i], fingopdata[i], finothdata[i])-min(findemdata[i], fingopdata[i], finothdata[i]))
            if max(findemdata[i], fingopdata[i], finothdata[i]) == findemdata[i]:
                margin2[i] = min(1,margin[i])
            elif max(findemdata[i], fingopdata[i], finothdata[i]) == fingopdata[i]:
                margin2[i] = min(2,margin[i]+1) # gop = +1
            else:
                margin2[i] = min(3,margin[i]+2)  # ind = +2
        
        df5 = {"fips": final_fips, "margin": margin2}
        dict2 = pd.DataFrame(df5)
        dict2.to_csv("results.csv")
        update_svg(svg_file_path, csv_file_path)
        
        with open('/Users/andrewpark/Desktop/Personal/Code/Politics/countychange_modified.svg', 'r') as file:
            svg_code = file.read()

        updated_svg_code = svg_code

        src = generate_svg_image(updated_svg_code)
        return src, threshold, state_input, county_input, dem_input, rep_input, oth_input 
    
    #finding county_rowcolumn
    chosen_state = state_input
    starting_fips = fips_states[chosen_state] + "001"
    starting_search = 0
    for i in range(len(final_fips)):
        if (final_fips[i] == starting_fips):
            starting_search = i
    county_rowcolumn = 0
    for i in range(len(dem_array)):
        if (dem_array[starting_search+i][0] == county_input):
            county_rowcolumn = starting_search+i
            break
    demswing_amounts.append(dem_input)
    gopswing_amounts.append(rep_input)
    othswing_amounts.append(oth_input)

    swing_counties.append(county_rowcolumn)
    correlation_threshold = threshold 

    dem_slopes, gop_slopes, oth_slopes = [], [], []
    for i in swing_counties:
        demappending = dem_array[i].copy()
        del demappending[0]
        dem_slopes.append(demappending)
        gopappending = gop_array[i].copy()
        del gopappending[0]
        gop_slopes.append(gopappending)
        othappending = oth_array[i].copy()
        del othappending[0]
        oth_slopes.append(othappending)

    dem_correlations, gop_correlations, oth_correlations = [], [], []
    for i in swing_counties:
        demcorrelation_list, gopcorrelation_list, othcorrelation_list = [], [], []
        for j in range(len(dem_array2)):
            if (j <= i):
                demcorrelation_list.append(dem_array2[i][j])
                gopcorrelation_list.append(gop_array2[i][j])
                othcorrelation_list.append(oth_array2[i][j])
            else:
                demcorrelation_list.append(dem_array2[j][i])
                gopcorrelation_list.append(gop_array2[j][i])
                othcorrelation_list.append(oth_array2[j][i])
        dem_correlations.append(demcorrelation_list)
        gop_correlations.append(gopcorrelation_list)
        oth_correlations.append(othcorrelation_list)
    
    demswingdata, gopswingdata, othswingdata = [0]*len(dem_slopes[0]), [0]*len(dem_slopes[0]), [0]*len(dem_slopes[0])
    demtemp, goptemp, othtemp = demdata.copy(), gopdata.copy(), othdata.copy()
    count = 0
    for j in swing_counties: # for the counties we're changing
        demtemp[j] += (demswing_amounts[count]/100)
        goptemp[j] += (gopswing_amounts[count]/100)
        othtemp[j] += (othswing_amounts[count]/100)
        demswingdata[j] = (demswing_amounts[count]/100)
        gopswingdata[j] = (gopswing_amounts[count]/100)
        othswingdata[j] = (othswing_amounts[count]/100)
        count += 1
        
    for i in range(len(dem_slopes[0])): # for EACH of ALL county
        if i in swing_counties:
            continue
        demsum, gopsum, othsum = 0, 0, 0
        demcorrelation, gopcorrelation, othcorrelation = 0, 0, 0
        for j in range(len(dem_slopes)): # for each county we're changing
            if ((abs(dem_correlations[j][i]) >= correlation_threshold)):
                demsum += (demswing_amounts[j] * dem_slopes[j][i]) * (abs(dem_correlations[j][i])**2)
            if ((abs(gop_correlations[j][i]) >= correlation_threshold)):
                gopsum += (gopswing_amounts[j] * gop_slopes[j][i]) * (abs(gop_correlations[j][i])**2)
            if ((abs(oth_correlations[j][i]) >= correlation_threshold)):
                othsum += (othswing_amounts[j] * oth_slopes[j][i]) * (abs(oth_correlations[j][i])**2)      
            demcorrelation += abs(dem_correlations[j][i])**2
            gopcorrelation += abs(gop_correlations[j][i])**2
            othcorrelation += abs(oth_correlations[j][i])**2
        demtemp[i] += (demsum / demcorrelation) / 100
        demswingdata[i] = (demsum / demcorrelation) / 100
        goptemp[i] += (gopsum / gopcorrelation) / 100
        gopswingdata[i] = (gopsum / gopcorrelation) / 100
        othtemp[i] += (othsum / othcorrelation) / 100
        othswingdata[i] = (othsum / othcorrelation) / 100
        for j in range(len(dem_slopes)): # for each county we're changing
            if (demtemp[i] < 0):
                demtemp[i] = 0
            if (goptemp[i] < 0):
                goptemp[i] = 0
            if (othtemp[i] < 0):
                othtemp[i] = 0  
    
    findemdata,fingopdata,finothdata = [0]*len(dem_slopes[0]), [0]*len(dem_slopes[0]), [0]*len(dem_slopes[0])
    margin, margin2, drmargin = [0]*len(dem_slopes[0]), [0]*len(dem_slopes[0]), [0]*len(dem_slopes[0]) 

    for i in range(len(demtemp)): # for EACH of ALL county
        findemdata[i] = demtemp[i]/(demtemp[i]+goptemp[i]+othtemp[i])  
        fingopdata[i] = goptemp[i]/(demtemp[i]+goptemp[i]+othtemp[i]) 
        finothdata[i] = othtemp[i]/(demtemp[i]+goptemp[i]+othtemp[i])
        margin[i] = max(findemdata[i], fingopdata[i], finothdata[i]) - (1-max(findemdata[i], fingopdata[i], finothdata[i])-min(findemdata[i], fingopdata[i], finothdata[i]))
        if max(findemdata[i], fingopdata[i], finothdata[i]) == findemdata[i]:
            margin2[i] = min(1,margin[i])
        elif max(findemdata[i], fingopdata[i], finothdata[i]) == fingopdata[i]:
            margin2[i] = min(2,margin[i]+1) # gop = +1
        else:
            margin2[i] = min(3,margin[i]+2)  # ind = +2
        drmargin[i] = fingopdata[i]-findemdata[i]
    
    df5 = {"fips": final_fips, "margin": margin2}
    dict2 = pd.DataFrame(df5)
    dict2.to_csv("results.csv")
    update_svg(svg_file_path, csv_file_path)
       
    with open('/Users/andrewpark/Desktop/Personal/Code/Politics/countychange_modified.svg', 'r') as file:
        svg_code = file.read()

    updated_svg_code = svg_code

    src = generate_svg_image(updated_svg_code)
    return src, threshold, state_input, county_input, dem_input, rep_input, oth_input

# Define app layout
app.layout = html.Div([
    html.Div([
            html.P("Correlation Threshold:"),
            dcc.Input(id='correlation-threshold', type='number', value=correlation_threshold, step=0.1),
            html.P("State:"),
            dcc.Input(id='state', type='text', value=state),
            html.P("County:"),
            dcc.Input(id='county', type='text', value=county),
            html.P("Dem Swing:"),
            dcc.Input(id='dem-swing', type='number', value=dem_swing, step=0.1),
            html.P("Rep Swing:"),
            dcc.Input(id='rep-swing', type='number', value=rep_swing, step=0.1),
            html.P("Oth Swing:"),
            dcc.Input(id='oth-swing', type='number', value=oth_swing, step=0.1),
            html.Button('Submit', id='submit-button', n_clicks=0),
            html.Button('New Swing', id='session-button', n_clicks=0),
            html.Button('Reset', id='reset-button', n_clicks=0),
        ],
        className='inputs-container',
        style={'width': '30%', 'float': 'left'}
    ),
    html.Div([
            html.P(id='import-message'),
            html.Img(id='svg-image'),
        ],
        className='image-container',
        style={'width': '70%', 'float': 'right'}
    ),
], className='container')

# run app
if __name__ == '__main__':
    app.run_server(debug=True)