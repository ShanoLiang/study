import revisitpy as rvt
import numpy as np
import pandas as pd
import altair as alt
import generate_curves
import vl_convert as vlc
import itertools
import revisitpy_server as rs
import time
# Meta Data
study_metadata = rvt.studyMetadata(
    authors=["Shano Liang"],
    organizations=["VIS Lab"],
    title='Opacity Judgment Study',
    description='',
    date='2025-03-06',
    version='1.0'
)


# UI Config
ui_config = rvt.uiConfig(
  contactEmail="sliang1@wpi.edu",
  logoPath="./assets/revisitLogoSquare.svg",
  sidebar=True,
  withProgressBar=False,
  nextOnEnter=True
)

# Introduction
introduction = rvt.component(type='markdown', path='./assets/introduction.md', component_name__= 'introduction')

# Snippet of the introduction component.
print(introduction)


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

def plot_side_by_side(seed=None, num_curves=3, opacityGroup=[0.3,0.6]):
    """
    Generate and display two Altair charts side by side with different opacities.
    """
    chart1 = plot_altair_curve(seed=seed, num_curves=num_curves, opacity=opacityGroup[0])
    chart2 = plot_altair_curve(seed=seed, num_curves=num_curves, opacity=opacityGroup[1])
    return alt.hconcat(chart1, chart2)

def create_vega_spec(visType, seed, num_curves=3, opacityGroup=[0.3,0.6]):
    """
    Generate a Vega spec from the Altair chart by converting it to Vega-Lite and then to Vega.
    """
    if visType == 'altairPlot':
        chart = plot_side_by_side(seed=seed, num_curves=num_curves, opacityGroup = opacityGroup)
    else:
        raise ValueError("Unsupported visualization type. Use 'altairPlot'.")
    
    vega_lite_spec = chart.to_json()
    vega_spec = vlc.vegalite_to_vega(vega_lite_spec, vl_version="5.20")
    return vega_spec

def component_function(seed=None, numPoints=None, opacityGroup=None):
    if(seed is not None and numPoints is not None and opacityGroup is not None):
        vega_spec = create_vega_spec(seed=seed, numPoints=numPoints, opacityGroup=opacityGroup)
            
        # Update signals with new signals for the final vega spec.
        vega_spec['config']["signals"] = [
            {
                "name": "revisitAnswer",
                "value": {},
                "on": [
                    {
                        "events": "@concat_0_group:click",
                        "update": "{responseId: 'vegaDemoResponse1', response: 'left'}"
                    },
                    {
                        "events": "@concat_1_group:click",
                        "update": "{responseId: 'vegaDemoResponse1', response: 'right'}"
                    },
                    {
                        "events": {"source": "window", "type": "keydown"},
                        "update": "event.key === 'ArrowLeft' ? {responseId: 'vegaDemoResponse1', response: 'left'} : event.key === 'ArrowRight' ? {responseId: 'vegaDemoResponse1', response: 'right'} : revisitAnswer"
                    },
                ]
            }
        ]
        
        # Add signal based bordering
        for entry in vega_spec['marks']:
            if entry['name'] == 'concat_0_group':
                condition = 'left'
            else:
                condition = 'right'
            entry['encode']['update']['stroke'] = {
                "signal": f"revisitAnswer.response === '{condition}' ? 'blue' : null"
            },
            entry['encode']['update']['strokeWidth'] = {
                "signal": f"revisitAnswer.response === '{condition}' ? 3 : 0"
            }
        
        return rvt.component(
            type='vega',
            config=vega_spec,
            component_name__=f'{seed}-{numPoints}-{opacityGroup[0]},{opacityGroup[1]}',
            response=[
                rvt.response(
                    id='vegaDemoResponse1',
                    prompt='You Selected: ',
                    location='sidebar',
                    type='reactive',
                    required=True
                )
            ]
        )

    return rvt.component(
        type='questionnaire',
        component_name__='blank-component'
    )

# Generate all combinations of two values between 1 and 10
combinations = itertools.combinations(range(1, 11), 2)

# Create the dataset with values divided by 10
dataSet = [{'opacityGroup': [x / 10, y / 10]} for x, y in combinations]
# Create the dataset with values divided by 10


main_sequence = rvt.sequence(order='fixed')

main_sequence.permute(
        factors=[{'seed': 42}, {'seed': 42}],
        order='latinSquare',
    ).permute(
        factors=[{'numPoints': 100}, {'numPoints': 100}],
        order='fixed',
    ).permute(
        factors=dataSet,
        order='random',
    ).component(component_function)
    
sequence = rvt.sequence(order='fixed',components=[introduction]) + main_sequence

study = rvt.studyConfig(
    schema="https://raw.githubusercontent.com/revisit-studies/study/v2.0.0-rc1/src/parser/StudyConfigSchema.json",
    uiConfig=ui_config,
    studyMetadata=study_metadata,
    sequence=sequence
)


def main():
    process = rs.serve()
    while True:
        time.sleep(1)  # Keep running until interrupted

if __name__ == "__main__":
    main()
