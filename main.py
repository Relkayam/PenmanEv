"""
----------------------------------------------------------------------
Project: Penman Evaporation Calculator
Filename: main.py
Author: Roy Elkayam
Created: 2025-04-08
Description: Calculates daily potential evaporation using the Penman equation
----------------------------------------------------------------------
"""

import pandas as pd
import matplotlib.pyplot as plt
from penman_calculation import PenmanEvaporation

def data_preparation(df):
    df = df.copy()
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%m/%Y %H:%M')
    df = df.set_index('datetime')

    # Define aggregation functions for each column
    agg_functions = {
        'temperature': 'mean',  # average
        'global_radiation': 'mean',  # average
        'precipitation': 'sum',  # sum
        'relative_humidity': 'mean',  # average
        'wind_speed': 'mean'  # average
    }

    daily_df = df.resample('D').agg(agg_functions)
    daily_df['global_radiation'] = daily_df['global_radiation'] * 0.0864  # Convert W/m² to MJ/m²/day
    # Optional: Round the averages to a reasonable number of decimal places
    # daily_df['temperature'] = daily_df['temperature'].round(2)
    # daily_df['relative_humidity'] = daily_df['relative_humidity'].round(1)
    # daily_df['wind_speed'] = daily_df['wind_speed'].round(2)

    daily_df['datetime'] = daily_df.index
    return daily_df

def plot_evaporation_results(df, save_path=None):
    """
    Create visualization of evaporation results
    """
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

    # Plot 1: Temperature and Humidity
    ax1_twin = ax1.twinx()
    line1 = ax1.plot(df.index, df['temperature'], 'r-', label='Temperature (°C)', linewidth=1)
    line2 = ax1_twin.plot(df.index, df['relative_humidity'], 'b-', label='Relative Humidity (%)', linewidth=1)

    ax1.set_ylabel('Temperature (°C)', color='r')
    ax1_twin.set_ylabel('Relative Humidity (%)', color='b')
    ax1.set_title('Weather Conditions')
    ax1.grid(True, alpha=0.3)

    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')

    # Plot 2: Wind Speed and Global Radiation
    ax2_twin = ax2.twinx()
    line3 = ax2.plot(df.index, df['wind_speed'], 'g-', label='Wind Speed (m/s)', linewidth=1)
    line4 = ax2_twin.plot(df.index, df['global_radiation'], 'orange', label='Global Radiation (W/m²)', linewidth=1)

    ax2.set_ylabel('Wind Speed (m/s)', color='g')
    ax2_twin.set_ylabel('Global Radiation (W/m²)', color='orange')
    ax2.set_title('Wind and Radiation')
    ax2.grid(True, alpha=0.3)

    lines = line3 + line4
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc='upper left')

    # Plot 3: Evaporation
    ax3.plot(df.index, df['penman_evaporation'], 'purple', label='Evaporation (mm/d)', linewidth=2)
    ax3.set_ylabel('Evaporation (mm/d)')
    ax3.set_xlabel('Time')
    ax3.set_title('Penman Potential Evaporation')
    ax3.grid(True, alpha=0.3)
    ax3.legend()

    # Add precipitation if available
    if 'precipitation' in df.columns:
        ax3_twin = ax3.twinx()
        ax3_twin.bar(df.index, df['precipitation'], alpha=0.3, color='blue',
                     label='Precipitation (mm)', width=0.01)
        ax3_twin.set_ylabel('Precipitation (mm)', color='blue')
        ax3_twin.invert_yaxis()  # Invert precipitation axis
        ax3_twin.legend(loc='upper right')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    plt.show()



# Example usage
if __name__ == "__main__":
    print("Penman Evaporation Calculator for our 10-minute Weather Data")
    print("=" * 60)

    df = pd.read_csv('data/ims_data.csv')
    # print(df.info())
    df = data_preparation(df)

    print("Calculating Penman evaporation...")

    # Initialize calculator for a location at 31.96°N latitude (Soreq 2 basin)
    penman = PenmanEvaporation(latitude_deg=31.96, elevation=30, albedo=0.08)

    # Function to calculate evaporation for each row
    def calculate_row_evaporation(row):
        return penman.calculate_daily_evaporation(
            datetime_obj=row.name,
            t_mean=row['temperature'],
            rh_mean=row['relative_humidity'],
            rs=row['global_radiation'],
            u=row['wind_speed']
        )


    # Apply the function to each row to calculate evaporation
    df['penman_evaporation'] = df.apply(calculate_row_evaporation, axis=1)


    # Display summary statistics
    print("\nEvaporation Statistics:")
    print(f"Mean evaporation: {df['penman_evaporation'].mean():.3f} mm/h")
    print(f"Max evaporation: {df['penman_evaporation'].max():.3f} mm/h")

    # print("\nGenerating plots...(1000 rows samples)")

    # df = df.iloc[:1000]
    plot_evaporation_results(df)

