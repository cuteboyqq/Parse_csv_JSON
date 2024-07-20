import csv
import json
import matplotlib.pyplot as plt

def extract_distance_data(file_path):
    frame_ids = []
    distances = []

    with open(file_path, 'r') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            # Debug print for each row
            print(f"Row: {row}")

            # Join the row into a single string
            row_str = ','.join(row)
            
            # Find the position of 'json:'
            json_start = row_str.find('json:')
            if json_start != -1:
                json_data = row_str[json_start + 5:].strip()
                if json_data.startswith('"') and json_data.endswith('"'):
                    json_data = json_data[1:-1]  # Remove enclosing double quotes
                
                # Replace any double quotes escaped with backslashes
                json_data = json_data.replace('\\"', '"')
                
                try:
                    data = json.loads(json_data)
                    print(f"Parsed JSON: {data}")

                    for frame_id, frame_data in data['frame_ID'].items():
                        frame_ids.append(int(frame_id))
                        tailing_objs = frame_data.get('tailingObj', [])
                        if tailing_objs:
                            distance_to_camera = tailing_objs[0].get('tailingObj.distanceToCamera', None)
                            if distance_to_camera is not None:
                                distances.append(distance_to_camera)
                            else:
                                distances.append(float('nan'))  # Handle missing values
                        else:
                            distances.append(float('nan'))  # Handle missing values
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                except Exception as e:
                    print(f"Unexpected error: {e}")

    return frame_ids, distances

# Paths to your CSV files
csv_file_1 = 'golden_date_ImageMode_10m.csv' #live mode
csv_file_2 = 'golden_date_ImageMode_20m.csv' #image mode
csv_file_3 = 'golden_date_ImageMode_30m.csv' #image mode
csv_file_4 = 'golden_date_ImageMode_40m.csv' #image mode
csv_file_5 = 'golden_date_ImageMode_50m.csv' #image mode

# Extract data from both files
frame_ids_1, distances_1 = extract_distance_data(csv_file_1)
frame_ids_2, distances_2 = extract_distance_data(csv_file_2)
frame_ids_3, distances_3 = extract_distance_data(csv_file_3)
frame_ids_4, distances_4 = extract_distance_data(csv_file_4)
frame_ids_5, distances_5 = extract_distance_data(csv_file_5)

# Plotting the data
plt.figure(figsize=(200, 100))
plt.plot(frame_ids_1, distances_1, label='GT:10m')
plt.plot(frame_ids_2, distances_2, label='GT:20m')
plt.plot(frame_ids_3, distances_3, label='GT:30m')
plt.plot(frame_ids_4, distances_4, label='GT:40m')
plt.plot(frame_ids_5, distances_5, label='GT:50m')


plt.xlabel('FrameID')
plt.ylabel('tailingObj.distanceToCamera')
plt.title('Distance to Camera over Frames')
plt.legend()
plt.grid(True)

plt.show()
