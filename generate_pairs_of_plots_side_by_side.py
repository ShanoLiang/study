import numpy as np
import matplotlib.pyplot as plt
import os
import time
import pandas as pd
import altair as alt
import generate_curves

def plot_altair_curve(seed=None, num_curves=3, opacity=0.3):
    """
    Generate and plot multiple smooth random curved lines using Altair with shaded areas.
    Automatically scales the y-axis to fit the minimum and maximum values across all curves.
    """
    if seed is not None:
        np.random.seed(seed)  # Set seed for reproducibility
    
    curves_data = []
    shaded_data = []
    y_min_global = float('inf')
    y_max_global = float('-inf')

    for i in range(num_curves):
        curve_seed = seed + i if seed is not None else None
        x, y = generate_curves.generate_smooth_curve(num_points=100, seed=curve_seed)
        df = pd.DataFrame({'X': x, 'Y': y, 'Curve': f'Curve {i+1}'})
        curves_data.append(df)
        y_min_global = min(y_min_global, np.min(y))
        y_max_global = max(y_max_global, np.max(y))
    
    for df in curves_data:
        df_shade = df.copy()
        df_shade['Y0'] = y_min_global  # Shade from the global minimum y-value up to the curve
        shaded_data.append(df_shade)
    
    all_curves = pd.concat(curves_data)
    all_shaded = pd.concat(shaded_data)
    
    y_scale = alt.Scale(domain=[y_min_global, y_max_global])  # Auto-scale y-axis
    
    line_chart = alt.Chart(all_curves).mark_line().encode(
        x='X:Q',
        y=alt.Y('Y:Q', scale=y_scale),
        color=alt.Color('Curve:N', legend=alt.Legend(title="Curves"))
    )
    
    shaded_chart = alt.Chart(all_shaded).mark_area(opacity=opacity).encode(
        x='X:Q',
        y=alt.Y('Y0:Q', scale=y_scale),
        y2='Y:Q',
        color=alt.Color('Curve:N', legend=None)  # Use the same color as the line but without an extra legend
    )
    
    return (shaded_chart + line_chart).properties(
        width=600,
        height=400,
        title="Curves"
    )

def plot_side_by_side(seed=None, num_curves=3, opacity1=0.3, opacity2=0.6):
    """
    Generate and display two Altair charts side by side with different opacities.
    """
    chart1 = plot_altair_curve(seed=seed, num_curves=num_curves, opacity=opacity1)
    chart2 = plot_altair_curve(seed=seed, num_curves=num_curves, opacity=opacity2)
    return alt.hconcat(chart1, chart2)

# Example usage:
chart = plot_side_by_side(seed=42, num_curves=3, opacity1=0.3, opacity2=0.6)
chart.show()
chart.save("curve_charts.html")
