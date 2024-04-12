# Fight Data Visualization
Denis Oh

## Description

This project processes and visualizes CAN bus data from a scale model aircraft, focusing on pilot control inputs and onboard inertial measurement unit (IMU) data. The script extracts specific signals from designated CAN message IDs and plots these signals in a series of graphs.

## Features

- Parses CAN bus data from a CSV file.
- Extracts signals such as pilot control inputs (roll, pitch, yaw, throttle) and IMU data (pitch angle, pitch rate, etc.).
- Visualizes the extracted data in a series of graphs with time as the x-axis.

## Usage Instructions

To run this program, you need Python 3 installed on your system. The project also depends on several Python libraries, including pandas, matplotlib, and numpy.

### Setting Up a Virtual Environment

It's recommended to use a virtual environment to manage dependencies. To set up and activate a virtual environment:

python3 -m venv venv
source venv/bin/activate 
**On Windows** use `venv\Scripts\activate`

### Installing Dependencies

Once your environment is set up and activated, install the required dependencies using:

pip install -r requirements.txt

### Running the Program

To run the program, execute the main script (this may take some time):

python3 main.py

Upon running the script, separate windows will pop up displaying the visualized data. There are four main visualization windows:

Window 1: Pitch Input, Pitch Angle, Pitch Rate
Window 2: Roll Input, Roll Angle, Roll Rate
Window 3: Yaw Input, Yaw Angle, Yaw Rate
Window 4: Hover Throttle, Pusher Throttle, Prop Spin
Each window will contain three subplots, each plotting one of the above-mentioned data against time.
