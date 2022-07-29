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
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
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


def timeline_plotting(filepath: str):
    """
    Loads CSV files and saves them in a data array format for Timeline plots. 
    """
    df = pd.read_csv(filepath, skipinitialspace=True)

    # TODO: make the pod_state_filter as a parameter
    df = df[df['pod_state_filter'] == 'Stateless']

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

    plt.plot(created_grouped.index, created_grouped.values)
    plt.plot(scheduled_grouped.index, scheduled_grouped.values)
    plt.plot(run_grouped.index, run_grouped.values)
    plt.plot(watched_grouped.index, watched_grouped.values)
    
    plt.show()


def histogram_plotting(filepath: str, num_bins):
    """
    Loads CSV files and saves them in a data array format for Timeline plots. 
    """
    df = pd.read_csv(filepath, skipinitialspace=True)

    # TODO: make the pod_state_filter as a parameter
    df = df[df['pod_state_filter'] == 'Stateless']

    created_df = df[df['Transition']=='{create schedule 0s}'].sort_values('diff')
    run_df = df[df['Transition']=='{schedule run 0s}'].sort_values('diff')
    watched_df = df[df['Transition']=='{run watch 0s}'].sort_values('diff') 

    fig = make_subplots(rows=3, cols=1)

    fig = make_subplots(rows=3, cols=1)
    fig = gobj.Figure()
    fig.add_trace(gobj.Histogram(x=created_df['diff'], nbinsx=num_bins))
    fig.update_layout(
    autosize=False,
    width=1600,
    height=800)
    
    fig.show()
    
    fig = make_subplots(rows=3, cols=1)
    fig = gobj.Figure()
    fig.add_trace(gobj.Histogram(x=run_df['diff'], nbinsx=num_bins))
    fig.update_layout(
    autosize=False,
    width=1600,
    height=800)
    
    fig.show()
    
    fig = make_subplots(rows=3, cols=1)
    fig = gobj.Figure()
    fig.add_trace(gobj.Histogram(x=watched_df['diff'], nbinsx=num_bins))
    fig.update_layout(
    autosize=False,
    width=1500,
    height=800)
    
    fig.show()

def _histogram_statistics():
    # TODO 
    ...

def _create_histogram(df: pd.DataFrame):
    sns.set(style="whitegrid")
    ax1 = sns.histplot(data=df['diff'], bins=100)
    ax2 = plt.twinx()
    ax2 = sns.histplot(data=df['diff'], bins=100, cumulative=True, element="poly", fill=False)
    return ax1, ax2

def _sum_rows(series: pd.Series) -> pd.Series:
    for i in range(1, len(series)):
        series.iloc[i] = series.iloc[i] + series.iloc[i-1]
    return series

def _is_valid_file(parser, arg):
        if not os.path.exists(arg):
            parser.error("The specified file does not exist.\n")
        else:
            return arg

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

    args = parser.parse_args()

    if args.input:
        # TODO: Implement an argument to select plot types
        # timeline_plotting(args.input)
        histogram_plotting(args.input, num_bins=200)


if __name__ == "__main__":
    main()
