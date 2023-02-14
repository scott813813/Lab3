"""!
@file step_response_plotter.py
This file contains code which takes in time and position data from the serial port
and outputs plots of the time and position

@author mecha12
@date   13-Feb-2023
"""

import serial # Import serial library
from matplotlib import pyplot # Import pyplot

# Create empty lists of x and y data
mot_1_x_data = []
mot_1_y_data = []

mot_2_x_data = []
mot_2_y_data = []

# Create labels for plots
mot_1_x_label = 'M1: Time, ms'  # Motor 1, x-axis title
mot_1_y_label = 'M1: Location, ticks'  # Motor 1, y-axis title

mot_2_x_label = 'M2: Time, ms'  # Motor 2, x-axis title
mot_2_y_label = 'M2: Location, ticks'  # Motor 2, y-axis title

with serial.Serial('COM11',115200) as s_port: # Fill in correct serial port when found
    s_port.flush() # Clear serial port
    
    while True:
        entry = s_port.readline().decode()
        if entry == 'Stahp\r\n':
            break
        entry = entry.split(',')
        try:    # Check if the values can be converted into a float
            entry[1] = float(entry[1])
            entry[2] = float(entry[2])
            if entry[0] == 'Motor 1': # Determine which motor wrote
                mot_1_x_data.append(entry[1])
                mot_1_y_data.append(entry[2])
            elif entry[0] == 'Motor 2':
                mot_2_x_data.append(entry[1])
                mot_2_y_data.append(entry[2])
        except:     # If not a number, skip line
            pass

    
# Print values for both motors into a supblot
fig, axs = pyplot.subplots(2)
fig.suptitle('Motor Response')

axs[0].plot(mot_1_x_data, mot_1_y_data)
axs[0].set(xlabel=mot_1_x_label, ylabel=mot_1_y_label)

axs[1].plot(mot_2_x_data, mot_2_y_data)
axs[1].set(xlabel=mot_2_x_label, ylabel=mot_2_y_label)
pyplot.show()