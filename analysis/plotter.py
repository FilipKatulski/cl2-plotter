# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <filip.katulski@cern.ch> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.
# 																Filip Katulski
# ----------------------------------------------------------------------------
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as gobj
from plotly.subplots import make_subplots
import argparse
from time import sleep
try:
    from art import text2art
except ModuleNotFoundError:
    print("\n\n'Art' module is not installed\n")
    pass


def display_header():
    """
    Displays python art header.
    """
    try:
        art_1 = text2art("cl2 plotter")
        print(art_1)
        sleep(1)
    except:
        print("\nknb autotester\n\n")
        sleep(1)


def timeline_plotting(filepath: str, state:str, minor_gridx=False, minor_gridy=False):
    """
    Loads CSV files and saves them in a data array format for Timeline plots. 
    """
    df = pd.read_csv(filepath, skipinitialspace=True)

    df = df[df['pod_state_filter'] == state]

    created_df = df[df['Transition']=='{create schedule 0s}'].sort_values('from_unix')
    scheduled_df = df[df['Transition']=='{create schedule 0s}'].sort_values('to_unix')
    run_df = df[df['Transition']=='{schedule run 0s}'].sort_values('to_unix')
    watched_df = df[df['Transition']=='{run watch 0s}'].sort_values('to_unix') 

    minimal_val = created_df['from_unix'].iloc[0]

    created_df['from_unix'] = created_df['from_unix'] - minimal_val
    scheduled_df['to_unix'] = scheduled_df['to_unix'] - minimal_val
    run_df['to_unix'] = run_df['to_unix'] - minimal_val
    watched_df['to_unix'] = watched_df['to_unix'] - minimal_val 

    created_grouped = _sum_rows(created_df.groupby('from_unix').size())
    scheduled_grouped = _sum_rows(scheduled_df.groupby('to_unix').size())
    run_grouped = _sum_rows(run_df.groupby('to_unix').size())
    watched_grouped = _sum_rows(watched_df.groupby('to_unix').size())
    
    fig = gobj.Figure()
    fig.add_scatter(x=created_grouped.index, y=created_grouped.values, mode='lines+markers', marker_symbol='circle',marker_size=9, name='created')
    fig.add_scatter(x=scheduled_grouped.index, y=scheduled_grouped.values, mode='lines+markers', marker_symbol='square',marker_size=9, name='scheduled')
    fig.add_scatter(x=run_grouped.index, y=run_grouped.values, mode='lines+markers', marker_symbol='diamond',marker_size=9, name='run')
    fig.add_scatter(x=watched_grouped.index, y=watched_grouped.values, mode='lines+markers', marker_symbol='x',marker_size=9, name='watch')
    
    fig.update_xaxes(ticks="outside", minor_ticks="outside", showgrid=True)
    fig.update_yaxes(ticks="outside", minor_ticks="outside")
    
    if minor_gridy == True:
        fig.update_yaxes(minor=dict(ticklen=6, tickcolor="black", showgrid=True))
    
    if minor_gridx == True:
        fig.update_xaxes(minor=dict(ticklen=6, tickcolor="black", showgrid=True))
        
    fig.update_layout(title='Timeline', # title of plot
    xaxis_title_text='Time [s]', # xaxis label
    yaxis_title_text='Count', # yaxis label
    autosize=False,
    width=1400,
    height=700)
    
    fig.show()

def _sum_rows(series: pd.Series) -> pd.Series:
    for i in range(1, len(series)):
        series.iloc[i] = series.iloc[i] + series.iloc[i-1]
    return series


def histogram_plotting(filepath: str, phase_change: str, num_bins: int, state: str, cumulative=False, 
    minor_gridx=False, minor_gridy=False, mean=False, std_dev=False):
    """
    Loads CSV files and creates plotly histograms. 
    """
    df = pd.read_csv(filepath, skipinitialspace=True)

    df = df[df['pod_state_filter'] == state]
    
    selected_df = df[df['Transition']==phase_change].sort_values('diff')

    title_text = phase_change[1:]
    title_text = title_text[:-4]
    splitted_title = title_text.split()
    splitted_title.insert(1, 'to')
    title_text = ' '.join(splitted_title)
    
    mean_val = np.mean(selected_df['diff'])
    stdev = np.std(selected_df['diff'])
    
    trace0 = gobj.Histogram(x=selected_df['diff'], nbinsx=num_bins, name= "Difference")
    trace1 = gobj.Histogram(x=selected_df['diff'], nbinsx=num_bins, name="Cumulative", cumulative_enabled=True)
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(trace0)
    
    
    if cumulative == True:
        fig.add_trace(trace1, secondary_y=True)

    if mean == True:
        fig.add_shape(type="line",x0=mean_val, x1=mean_val, y0=-0.01, y1=1 , xref='x', yref='paper',
               line = dict(color = 'blue', dash = 'dash'))
        fig.add_annotation(x=mean_val, y=0.9, xref='x', yref='paper', text="Mean b={:.0f}".format(mean_val)) 
        
    if std_dev == True:
        
        fig.add_shape(type="line",x0=mean_val+stdev, x1=mean_val+stdev, y0=-0.01, y1=1 , xref='x', yref='paper',
               line = dict(color = 'red', dash = 'dash'))
        fig.add_annotation(x=mean_val+stdev, y=0.9, xref='x', yref='paper', text="Std dev σ={:.0f}".format(mean_val+stdev))
        fig.add_shape(type="line",x0=mean_val-stdev, x1=mean_val-stdev, y0=-0.01, y1=1 , xref='x', yref='paper',
               line = dict(color = 'red', dash = 'dash'))
        fig.add_annotation(x=mean_val-stdev, y=0.9, xref='x', yref='paper', text="Std dev -σ={:.0f}".format(mean_val-stdev))
    

    fig.update_xaxes(ticks="outside", minor_ticks="outside", showgrid=True)
    fig.update_yaxes(ticks="outside", minor_ticks="outside")
    
    if minor_gridx == True:
        fig.update_xaxes(minor=dict(ticklen=6, tickcolor="black", showgrid=True))
        
    if minor_gridy == True:
        fig.update_yaxes(minor=dict(ticklen=6, tickcolor="black", showgrid=True))
        
    fig.update_traces(opacity=0.60)
    fig.update_layout(title=title_text, # title of plot
    xaxis_title_text='diff [ms]', # xaxis label
    yaxis_title_text='Count', # yaxis label
    autosize=False,
    width=1400,
    height=700)
    
    fig.show()

def piechart_plotting(filepath: str, state:str):
    """
    Loads CSV files and creates a piechart.
    """
    df = pd.read_csv(filepath, skipinitialspace=True)
    df = df[df['pod_state_filter'] == state]
    
    create_to_schedule_df = df[df['Transition']=='{create schedule 0s}'].sort_values('diff')
    schedule_to_run_df = df[df['Transition']=='{schedule run 0s}'].sort_values('diff')
    run_to_watch_df = df[df['Transition']=='{run watch 0s}'].sort_values('diff') 
    
    create_to_schedule_total = create_to_schedule_df['diff'].sum()
    schedule_to_run_total = schedule_to_run_df['diff'].sum()
    run_to_watch_total = run_to_watch_df['diff'].sum() 
    
    labels = ['create to schedule', 'schedule to run', 'run to watch']
    values = [create_to_schedule_total, schedule_to_run_total, run_to_watch_total]
    
    fig = gobj.Figure(data=[gobj.Pie(labels=labels, values=values)])
    fig.update_layout(title="Distribution of time spent in each phase", # title of plot
    autosize=False,
    width=700,
    height=700)
    
    fig.show()
    

def _is_valid_file(parser, arg):
        if not os.path.exists(arg):
            parser.error("The specified file does not exist.\n")
        else:
            return arg

def _is_valid_state(parser, arg):
    if arg == "Stateless" or arg == "Stateful" or arg == "MatchAll":
        return arg
    else:
        parser.error("The specified Pod state does not exist.\n")

def main():
    """
    The main function that parses arguments and runs specified data analysis. 
    """

    display_header()

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='store_true', help="displays cl2-plotter script help")
    parser.add_argument('-i', '--input', dest='input', required=False, metavar='FILE', 
    type=lambda x: _is_valid_file(parser, x), 
    help='input CSV file with data plotting')

    # TODO:
    # parser.add_argument('-s', '--state', required=True, dest='input')

    args = parser.parse_args()

    if args.input:
        # TODO: Implement an argument to select plot types
        # timeline_plotting(args.input)
        histogram_plotting(args.input, num_bins=200)


if __name__ == "__main__":
    main()
