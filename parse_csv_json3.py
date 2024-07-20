import csv
import json
import matplotlib.pyplot as plt
import os
import cv2

def extract_distance_data(file_path,
                        image_dir,
                        image_base_name,
                        image_format,
                        save_im_dir,
                        show_im=False,
                        save_im=False):
    frame_ids = []
    distances = []

    with open(file_path, 'r') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            # Debug print for each row
            # print(f"Row: {row}")

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
                    # print(f"Parsed JSON: {data}")

                    for frame_id, frame_data in data['frame_ID'].items():
                        frame_ids.append(int(frame_id))
                        print(f"frame_id:{frame_id}")
                        
                        # Get image path
                        im_file = image_base_name + frame_id + "." + image_format
                        im_path = os.path.join(image_dir,im_file)
                        print(im_path)
                        im = cv2.imread(im_path)

                        cv2.putText(im, 'frame_ID:'+str(frame_id), (10,10), cv2.FONT_HERSHEY_SIMPLEX,0.45, (255, 0, 255), 1, cv2.LINE_AA)
                        tailing_objs = frame_data.get('tailingObj', [])
                        vanish_objs = frame_data.get('vanishLineY', [])
                        if tailing_objs:
                            distance_to_camera = tailing_objs[0].get('tailingObj.distanceToCamera', None)
                            tailingObj_x1 = tailing_objs[0].get('tailingObj.x1', None)
                            tailingObj_y1 = tailing_objs[0].get('tailingObj.y1', None)
                            tailingObj_x2 = tailing_objs[0].get('tailingObj.x2', None)
                            tailingObj_y2 = tailing_objs[0].get('tailingObj.y2', None)
                            print(f"tailingObj_x1:{tailingObj_x1}")
                            print(f"tailingObj_y1:{tailingObj_y1}")
                            print(f"tailingObj_x2:{tailingObj_x2}")
                            print(f"tailingObj_y2:{tailingObj_y2}")
                            tailingObj_label = tailing_objs[0].get('tailingObj.label', None)

                            # Draw bounding box on the image
                            cv2.rectangle(im, (tailingObj_x1, tailingObj_y1), (tailingObj_x2, tailingObj_y2), color=(255,0,0), thickness=1)
                            

                            if tailingObj_label=='VEHICLE':
                                # Put text on the image
                                cv2.putText(im, 'V:' + str(round(distance_to_camera,3)), (tailingObj_x1, tailingObj_y1-10), cv2.FONT_HERSHEY_SIMPLEX,0.45, (0, 0, 255), 1, cv2.LINE_AA)

                            if distance_to_camera is not None:
                                distances.append(distance_to_camera)
                            else:
                                distances.append(float('nan'))  # Handle missing values
                        else:
                            distances.append(float('nan'))  # Handle missing values
                        if vanish_objs:
                            vanishlineY = vanish_objs[0].get('vanishlineY', None)
                            print(f'vanishlineY:{vanishlineY}')
                            x2 = im.shape[1]
                            cv2.line(im, (0, vanishlineY), (x2, vanishlineY), (0, 255, 0), thickness=1)
                            cv2.putText(im, 'VL:' + str(round(vanishlineY,3)), (10,30), cv2.FONT_HERSHEY_SIMPLEX,0.45, (0, 0, 255), 1, cv2.LINE_AA)
                       
                        if show_im:
                            # 按下任意鍵則關閉所有視窗
                            cv2.imshow("im",im)
                            cv2.waitKey(100)
                            # cv2.destroyAllWindows()
                        if save_im:
                            os.makedirs(save_im_dir,exist_ok=True)
                            im_file = image_base_name + str(frame_id) + "." + image_format
                            save_im_path = os.path.join(save_im_dir,im_file)
                            if not os.path.exists(save_im_path):
                                cv2.imwrite(save_im_path,im)
                            else:
                                print(f'image exists :{save_im_path}')
                            
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                except Exception as e:
                    print(f"Unexpected error: {e}")

    return frame_ids, distances

if __name__=="__main__":
    SHOW_AI_RESULT_IMAGE = True
    SAVE_AI_RESULT_IMAGE = True
    SHOW_DISTANCE_PLOT = True
    # Paths to your CSV files
    csv_file_1 = 'golden_date_ImageMode_30m.csv' #live mode

    image_dir = "/home/ali/Projects/datasets/Golden_Data/car_30m"
    image_base_name = "RawFrame_"
    image_format = "png"
    save_im_dir = "/home/ali/Projects/datasets/AI_result_image"

    # Extract data from both files
    frame_ids_1, distances_1 = extract_distance_data(csv_file_1,
                                                    image_dir,
                                                    image_base_name,
                                                    image_format,
                                                    save_im_dir,
                                                    show_im = SHOW_AI_RESULT_IMAGE,
                                                    save_im = SAVE_AI_RESULT_IMAGE)

    if SHOW_DISTANCE_PLOT:
        # Plotting the data
        plt.figure(figsize=(200, 100))
        plt.plot(frame_ids_1, distances_1, label='GT:30m')

        plt.xlabel('FrameID')
        plt.ylabel('tailingObj.distanceToCamera')
        plt.title('Distance to Camera over Frames')
        plt.legend()
        plt.grid(True)

        plt.show()
