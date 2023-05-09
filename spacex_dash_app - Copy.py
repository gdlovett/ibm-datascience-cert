# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=[{'label':'All Sites', 'value':'ALL'},
                                                    {'label':'CCAFS LC-40', 'value':'CCAFS LC-40'},
                                                    {'label':'CCAFS SLC-40', 'value':'CCAFS SLC-40'},
                                                    {'label':'KSC LC-39A', 'value':'KSC LC-39A'},
                                                    {'label':'VAFB SLC-4E', 'value':'VAFB SLC-4E'}],
                                            value='ALL',
                                            placeholder='Select a Launch Site here',
                                            searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site

                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                # min and max of slider values
                                                min=0, max=10000,
                                                # interval of the slider
                                                step=1000,
                                                # default selected range
                                                value=[min_payload,max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])
#-----------------------------------------------
# TASK 2B: ADD A CALLBACK TO RENDER PIE CHART

# add callback decorator
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)

# function to get the graph
def get_pie_chart(entered_site):
    '''
    Function takes the entered launch site from the dropdown
    menu and returns a pie chart for that site (or all sites)
    showing the number and percent of successful vs failing 
    rocket launches.

    if ALL sites selected, use all rows in the df to 
    render and return a pie chart to show successes by
    launch site.
    
    if a specific site is selected, filter the df to
    only include that site, then return pie chart of that
    site's total success vs failure launches
    '''

    # initialize filtered dataframe
    filtered_df = spacex_df

    # if ALL, keep df as is and create a pie chart which shows
    # the percent of total successes for each site (eg 
    # VAFB's successes are 20% of the successes of all sites)
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class',
                    names='Launch Site',
                    title='Total Success Launches by Site')
        return fig
        
    # if a specific site is selected, filter the df to include
    # only that site, and then create a pie chart to show
    # the percentage of success vs failure in that site. 
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]

        fig = px.pie(filtered_df, values=filtered_df['class'].value_counts().values,
                    names=filtered_df['class'].value_counts().index,
                    title=f'Total Success Launches for Site {entered_site}')
        return fig
        
#-----------------------------------------------------------
# TASK 1: ADD A LAUNCH SITE DROP-DOWN INPUT COMPONENT

# We have four different launch sites and we would like to 
# first see which one has the largest success count. Then,
# we would like to select one specific site and check its 
# detailed success rate (class=0 vs. class=1).

# As such, we will need a dropdown menu to let us select 
# different launch sites.

#----------------------------------------------------------
# TASK 2:
# Add a callback function to render the pie chart based
# on selected site dropdown, changing with every selection 
# for `site-dropdown` as input, `success-pie-chart` as output

# The Dash callback function is a type of Python function which
# will be called automatically by Dash whenever receiving a 
# new input, such as a click or dropdown selection. 
#-----------------------------------------------------------
# TASK 3:
# Add a range slider.
# 
# We want to find out if variable payload is correlated
# to mission outcome. We want to create a slider
# to select different ranges of payload mass 
# which will generate different scatterplots showing
# payload vs launch outcome 
# 
# -------------------------------------------------------
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart',
            component_property='figure'
    ),
    # two input components
    [
        # receive the launch site
        Input(
            component_id='site-dropdown', component_property='value'
        ),
        # receive selected payload range
        Input(
            component_id='payload-slider', component_property='value'
        )
    ]
)
def get_scatter_plot(launch_site, payload_range):
    '''
    launch_site = dropdown selection
    payload_range = payload range indicated by slider placement

    Function will return a scatterplot for the 
    selected launch site (or ALL) showing
    payload on the x axis and outcome on the y axis.
    '''
    # create variables to show the min and max
    # of the selected range
    min_selected_range, max_selected_range = payload_range
    
    # initialize filtered df
    # only include rows with a payload mass in 
    # the selected range
    condition = (spacex_df['Payload Mass (kg)'] >= min_selected_range) & (spacex_df['Payload Mass (kg)'] <= max_selected_range)
    filtered_df = spacex_df[condition]

    # if ALL sites selected, render scatterplot
    # to display payload vs class for all sites.
    if launch_site == 'ALL':
        fig = px.scatter(filtered_df,
                        x='Payload Mass (kg)',
                        y='class',
                        color='Booster Version Category',
                        title='Correlation between Payload and Success for all sites')
        return fig
    else:
        # if a specific site is selected, filter
        # the df to only include data from that site
        filtered_df = filtered_df[filtered_df['Launch Site']==launch_site]
        # create a scatterplot of the payload mass
        # vs success for that site
        fig = px.scatter(filtered_df,
                        x='Payload Mass (kg)',
                        y='class',
                        color='Booster Version Category',
                        title=f'Correlation between Payload and Success for Site {launch_site}')
        return fig
# Run the app
if __name__ == '__main__':
    app.run_server()


# FINAL QUESTIONS - FINDING INSIGHTS

# 1. Which site has the most successful launches?
#   KSC with 10
# 
# 2. which site has the highest success rate?
#   CCAFS-SLC with 42% success
# 
# 3. which payload range(s) has the highest success rate
#   2k-6k
# 
# 4. which payload ranges has the lowest success rate
#   500-2000 and 5500-9000
# 
# 5. which f9 booster version has the highest success rate
#   b5 because 1 launch and it was a success
#   with n bigger than 1 it would be ft 