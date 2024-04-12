import struct
import pandas
import matplotlib.pyplot as plt
import numpy as np

DATA_FILE = 'data/20191118174447_Converted_trace-2019-12-09_12.csv'
TARGET_IDS = ['07E3', '07E4', '0001', '0002', '0003', '0004', '0005', '0006']

# Read data file
def read_data(file_path):
    return pandas.read_csv(file_path, skiprows=30, delimiter=';')


# Parse a row of data into a dictionary of pilot inputs
def parse_message(row):
    message_id = row['ID (hex)']
    parsed_data = {}
    row = row.astype(str)

    # Initialize all fields
    parsed_data['ID (hex)'] = message_id
    for field in ['roll_input', 'pitch_input', 'yaw_input', 'hover_throttle', 'prop_spin', 'pusher_throttle', 'pitch_angle', 'pitch_rate', 'roll_angle', 'roll_rate', 'yaw_angle', 'yaw_rate']:
        parsed_data[field] = None

    # Ensure columns D0 to D7 have two digits
    for i in range(8): 
        col = f'D{i}'
        row[col] = row[col].strip().zfill(2)

    # pilot control inputs
    if message_id == '07E3':
        roll_input = int.from_bytes(bytes.fromhex(row['D0'] + row['D1']), 'big', signed=True)
        pitch_input = int.from_bytes(bytes.fromhex(row['D2'] + row['D3']), 'big', signed=True)
        yaw_input = int.from_bytes(bytes.fromhex(row['D4'] + row['D5']), 'big', signed=True)
        hover_throttle = int.from_bytes(bytes.fromhex(row['D6'] + row['D7']), 'big', signed=False)

        parsed_data['roll_input'] = roll_input
        parsed_data['pitch_input'] = pitch_input
        parsed_data['yaw_input'] = yaw_input
        parsed_data['hover_throttle'] = hover_throttle

    elif message_id == '07E4':
        prop_spin = int.from_bytes(bytes.fromhex(row['D0']), 'big', signed=False)
        pusher_throttle = int.from_bytes(bytes.fromhex(row['D2'] + row['D3']), 'big', signed=True)

        parsed_data['prop_spin'] = prop_spin
        parsed_data['pusher_throttle'] = pusher_throttle

    # IMU data
    elif message_id in ['0001', '0002', '0003', '0004', '0005', '0006']:
        float_data = struct.unpack('>f', bytes.fromhex(''.join(row['D0':'D3'])))[0]

        # Assign to the correct IMU parameter
        imu_param = {
            '0001': 'pitch_angle',
            '0002': 'pitch_rate',
            '0003': 'roll_angle',
            '0004': 'roll_rate',
            '0005': 'yaw_angle',
            '0006': 'yaw_rate'
        }[message_id]

        parsed_data[imu_param] = float_data

    return parsed_data


# Parse each row in a DataFrame
def extract_relevant_data(df):
    processed_data = []

    for index, row in df.iterrows():
        
        parsed_data = parse_message(row)

        parsed_data['timestamp'] = row['Time (ms)']

        if parsed_data['ID (hex)'] in TARGET_IDS:
            processed_data.append(parsed_data)

    # Convert list of dictionaries to DataFrame
    processed_df = pandas.DataFrame(processed_data)

    # Convert timestamp from milliseconds to seconds
    processed_df['timestamp'] = processed_df['timestamp'] / 1000.0

    # Interpolate IMU data (data is sparse)
    imu_columns = ['pitch_angle', 'pitch_rate', 'roll_angle', 'roll_rate', 'yaw_angle', 'yaw_rate']
    processed_df[imu_columns] = processed_df[imu_columns].interpolate(method='linear')

    return processed_df


# Scale a series for it's new min and max values
def scale_series(series, old_min, old_max, new_min, new_max):
    return (new_max - new_min) / (old_max - old_min) * (series - old_min) + new_min


# Plot all relevant data
def plot_data(df):
    # Window 1: Pitch Input, Pitch Angle, Pitch Rate
    fig1, axs1 = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    axs1[0].plot(df['timestamp'], scale_series(df['pitch_input'], -32767, 32768, -30, 30), label='Pitch Input (Scaled Degrees)')
    axs1[0].set_ylabel('Pitch Input (Degrees)')
    axs1[1].plot(df['timestamp'], df['pitch_angle'], label='Pitch Angle (Radians)')
    axs1[1].set_ylabel('Pitch Angle (Radians)')
    axs1[2].plot(df['timestamp'], df['pitch_rate'], label='Pitch Rate (Radians/s)')
    axs1[2].set_ylabel('Pitch Rate (Radians/s)')
    for ax in axs1:
        ax.legend()
        ax.set_xlabel('Time (s)')
    axs1[0].set_title('Pitch Data')

    # Window 2: Roll Input, Roll Angle, Roll Rate
    fig2, axs2 = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    axs2[0].plot(df['timestamp'], scale_series(df['roll_input'], -32767, 32768, -30, 30), label='Roll Input (Scaled Degrees)')
    axs2[0].set_ylabel('Roll Input (Degrees)')
    axs2[1].plot(df['timestamp'], df['roll_angle'], label='Roll Angle (Radians)')
    axs2[1].set_ylabel('Roll Angle (Radians)')
    axs2[2].plot(df['timestamp'], df['roll_rate'], label='Roll Rate (Radians/s)')
    axs2[2].set_ylabel('Roll Rate (Radians/s)')
    for ax in axs2:
        ax.legend()
        ax.set_xlabel('Time (s)')
    axs2[0].set_title('Roll Data')

    # Window 3: Yaw Input, Yaw Angle, Yaw Rate
    fig3, axs3 = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    axs3[0].plot(df['timestamp'], scale_series(df['yaw_input'], -32767, 32768, -60, 60), label='Yaw Input (Scaled Degrees/s)')
    axs3[0].set_ylabel('Yaw Input (Degrees/s)')
    axs3[1].plot(df['timestamp'], df['yaw_angle'], label='Yaw Angle (Radians)')
    axs3[1].set_ylabel('Yaw Angle (Radians)')
    axs3[2].plot(df['timestamp'], df['yaw_rate'], label='Yaw Rate (Radians/s)')
    axs3[2].set_ylabel('Yaw Rate (Radians/s)')
    for ax in axs3:
        ax.legend()
        ax.set_xlabel('Time (s)')
    axs3[0].set_title('Yaw Data')

    # Window 4: Hover Throttle, Pusher Throttle, Prop Spin
    fig4, axs4 = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    axs4[0].plot(df['timestamp'], scale_series(df['hover_throttle'], 0, 65535, 0, 100), label='Hover Throttle (Scaled %)')
    axs4[0].set_ylabel('Hover Throttle (%)')
    axs4[1].plot(df['timestamp'], scale_series(df['pusher_throttle'], -32767, 32768, -100, 100), label='Pusher Throttle (Scaled %)')
    axs4[1].set_ylabel('Pusher Throttle (%)')
    axs4[2].plot(df['timestamp'], scale_series(df['prop_spin'], 0, 255, 0, 1), label='Prop Spin (On/Off)')
    axs4[2].set_ylabel('Prop Spin (On/Off)')
    for ax in axs4:
        ax.legend()
        ax.set_xlabel('Time (s)')
    axs4[0].set_title('Throttle and Prop Spin Data')

    plt.show()


# Main 
if __name__ == '__main__':
    df = read_data(DATA_FILE)

    # Extract and process data into 
    processed_data = extract_relevant_data(df)
    print(processed_data.describe())

    plot_data(processed_data)
