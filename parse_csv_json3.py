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
                        save_im=False,
                        plot_dist=False):
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

                        cv2.putText(im, 'frame_ID:'+str(frame_id), (10,10), cv2.FONT_HERSHEY_SIMPLEX,0.45, (0, 255, 0), 1, cv2.LINE_AA)
                        tailing_objs = frame_data.get('tailingObj', [])
                        vanish_objs = frame_data.get('vanishLineY', [])
                        ADAS_objs = frame_data.get('ADAS', [])
                        detect_objs = frame_data.get('detectObj', {})

                        if detect_objs:
                            # Draw detectObj bounding boxes
                            for obj_type, obj_list in detect_objs.items():
                                for obj in obj_list:
                                    label = obj.get(f'detectObj.label', '')
                                    x1 = obj.get(f'detectObj.x1', 0)
                                    y1 = obj.get(f'detectObj.y1', 0)
                                    x2 = obj.get(f'detectObj.x2', 0)
                                    y2 = obj.get(f'detectObj.y2', 0)
                                    confidence = obj.get(f'detectObj.confidence', 0.0)
                                    
                                    # Draw bounding box
                                    cv2.rectangle(im, (x1, y1), (x2, y2), color=(255,128,0), thickness=1)
                                    cv2.putText(im, f'{label} {confidence:.2f}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1, cv2.LINE_AA)

                        if tailing_objs:
                            distance_to_camera = tailing_objs[0].get('tailingObj.distanceToCamera', None)
                            tailingObj_confidence = tailing_objs[0].get('tailingObj.confidence', None)
                            tailingObj_x1 = tailing_objs[0].get('tailingObj.x1', None)
                            tailingObj_y1 = tailing_objs[0].get('tailingObj.y1', None)
                            tailingObj_x2 = tailing_objs[0].get('tailingObj.x2', None)
                            tailingObj_y2 = tailing_objs[0].get('tailingObj.y2', None)
                            print(f"tailingObj_confidence:{tailingObj_confidence}")
                            print(f"tailingObj_x1:{tailingObj_x1}")
                            print(f"tailingObj_y1:{tailingObj_y1}")
                            print(f"tailingObj_x2:{tailingObj_x2}")
                            print(f"tailingObj_y2:{tailingObj_y2}")
                            tailingObj_label = tailing_objs[0].get('tailingObj.label', None)

                            # Draw bounding box on the image
                            cv2.rectangle(im, (tailingObj_x1, tailingObj_y1), (tailingObj_x2, tailingObj_y2), color=(0,255,255), thickness=2)
                            

                            #if tailingObj_label=='VEHICLE':
                                # Put text on the image
                            #cv2.putText(im, f'{tailingObj_label} {tailingObj_confidence:.2f}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1, cv2.LINE_AA)
                            cv2.putText(im, 'Distance:' + str(round(distance_to_camera,3)) + 'm', (tailingObj_x1, tailingObj_y1-25), cv2.FONT_HERSHEY_SIMPLEX,0.45, (0, 255, 255), 1, cv2.LINE_AA)

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
                            cv2.putText(im, 'VanishLineY:' + str(round(vanishlineY,3)), (10,30), cv2.FONT_HERSHEY_SIMPLEX,0.45, (0, 255, 0), 1, cv2.LINE_AA)
                       
                        if ADAS_objs:
                            ADAS_FCW = ADAS_objs[0].get('FCW',None)
                            ADAS_LDW = ADAS_objs[0].get('LDW',None)
                            print(f'ADAS_FCW:{ADAS_FCW}')
                            print(f'ADAS_LDW:{ADAS_LDW}')
                            if ADAS_FCW==True:
                                cv2.putText(im, 'Collision Warning', (150,50), cv2.FONT_HERSHEY_SIMPLEX,0.8, (0, 128, 255), 2, cv2.LINE_AA)
                            if ADAS_LDW==True:
                                cv2.putText(im, 'Departure Warning', (150,80), cv2.FONT_HERSHEY_SIMPLEX,0.8, (128, 0, 255), 2, cv2.LINE_AA)


                        if show_im:
                            # 按下任意鍵則關閉所有視窗
                            cv2.imshow("im",im)
                            if ADAS_FCW==True or ADAS_LDW==True:
                                cv2.waitKey(500)
                            else:
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
    
    if plot_dist:
        # Plotting the data
        plt.figure(figsize=(200, 100))
        plt.plot(frame_ids_1, distances_1, label='GT:10m')

        plt.xlabel('FrameID')
        plt.ylabel('tailingObj.distanceToCamera')
        plt.title('Distance to Camera over Frames')
        plt.legend()
        plt.grid(True)

        plt.show()


    return frame_ids, distances

if __name__=="__main__":
    SHOW_AI_RESULT_IMAGE = True
    SAVE_AI_RESULT_IMAGE = True
    SHOW_DISTANCE_PLOT = True
    # Paths to your CSV files
    csv_file_1 = 'test-live-2024-07-22-11-43.csv' #live mode

    image_dir = "/home/ali/Projects/datasets/2024-7-23-11-38"
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
                                                    save_im = SAVE_AI_RESULT_IMAGE,
                                                    plot_dist = SHOW_DISTANCE_PLOT)

    