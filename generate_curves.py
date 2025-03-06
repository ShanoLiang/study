import numpy as np
import matplotlib.pyplot as plt
import json
import os
import time

def generate_smooth_curve(num_points=100, seed=None, wave_combinations=None):
    """
    Generate a smooth random curved line with multiple wave combinations using a fixed seed.

    Parameters:
        num_points (int): Number of data points to generate.
        seed (int, optional): Random seed for reproducibility.
        wave_combinations(list,optional): List of wave combinations for each frequency component.

    Returns:
    - x: X values.
    - y: Y values.
    """
    if seed is not None:
        np.random.seed(seed)  # Set seed for reproducibility
    
    freq_factors = np.random.randint(1, 3, size=4).tolist()
    amp_factors = np.random.uniform(0.5, 10, size=4).tolist()
    noise_level = np.random.uniform(0, 0.02)
    x_shift = np.random.uniform(0, 3)
    y_shift = np.random.uniform(0, 3)

    if wave_combinations is None:
        wave_combinations = [['sin', 'sinc']]

    x = np.linspace(0, 10, num_points)
    y = np.zeros_like(x)

    for a, f, waves in zip(amp_factors, freq_factors, wave_combinations):
        for w in waves:
            if w == 'sin':
                y += a * np.sin(f * (x + x_shift))
            elif w == 'cos':
                y += a * np.cos(f * (x + x_shift))
            elif w == 'sinc':
                y += a * np.sinc(f * ((x + x_shift)))
            elif w == 'tanh':
                y += a * np.tanh(f * ((x + x_shift)))
            elif w == 'exp':
                y += a * np.exp(-0.5 * f * ((x + x_shift)))

    y += (np.random.normal(scale=noise_level, size=len(x)) + y_shift)
        # Stack into a 2D array
    data = np.column_stack((x, y))
    return x, y
