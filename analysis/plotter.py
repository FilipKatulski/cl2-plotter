"""
 * ----------------------------------------------------------------------------
 * "THE BEER-WARE LICENSE" (Revision 42):
 * <filip.katulski@cern.ch> wrote this file.  As long as you retain this notice
 * you can do whatever you want with this stuff. If we meet some day, and you
 * think this stuff is worth it, you can buy me a beer in return.
 * 																Filip Katulski
 * ----------------------------------------------------------------------------
"""

import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse 

def load_and_parse(filepath: str):
    """
    Loads CSV files and saves them in a data array format. 
    """
    df = pd.read_csv(filepath, skipinitialspace=True)
    print(df)
    print(df.columns)

    df = df[df['pod_state_filter'] == 'Stateless']

    created_df = df[df['Transition']=='{create schedule 0s}'].sort_values('from_unix')

    minimal_val = created_df['from_unix'].iloc[0]

    print(minimal_val, type(minimal_val))

    scheduled_df = df[df['Transition']=='{create schedule 0s}'].sort_values('to_unix')

    run_df = df[df['Transition']=='{schedule run 0s}'].sort_values('to_unix')

    watched_df = df[df['Transition']=='{run watch 0s}'].sort_values('to_unix') 

    print(created_df)

    created_df['from_unix'] = created_df['from_unix'] - minimal_val
    scheduled_df['to_unix'] = scheduled_df['to_unix'] - minimal_val
    run_df['to_unix'] = run_df['to_unix'] - minimal_val
    watched_df['to_unix'] = watched_df['to_unix'] - minimal_val 
    print(created_df)
    print(watched_df)

    timeline_plotting(created_df=created_df,scheduled_df=scheduled_df, run_df=run_df, watched_df=watched_df)
    
def timeline_plotting(created_df, scheduled_df, run_df, watched_df):
    """
    Creates Timeline plots. 
    """
    created_grouped = _sum_rows(created_df.groupby('from_unix').size())
    scheduled_grouped = _sum_rows(scheduled_df.groupby('to_unix').size())
    run_grouped = _sum_rows(run_df.groupby('to_unix').size())
    watched_grouped = _sum_rows(watched_df.groupby('to_unix').size())

    plt.plot(created_grouped.index, created_grouped.values)
    plt.plot(scheduled_grouped.index, scheduled_grouped.values)
    plt.plot(run_grouped.index, run_grouped.values)
    plt.plot(watched_grouped.index, watched_grouped.values)
    
    plt.show()

def histogram_plotting():
    """
    Creates histograms. 
    """

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
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='store_true', help="displays autotester script help")
    parser.add_argument('-i', '--input', dest='input', required=False, metavar='FILE', 
    type=lambda x: _is_valid_file(parser, x), 
    help='input yaml file with test configuration or input folder for plotting')

    args = parser.parse_args()

    if args.input:
        load_and_parse(args.input)


if __name__ == "__main__":
    main()
