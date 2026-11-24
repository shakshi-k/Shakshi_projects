
# Importing the modules

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import math
import random

from pyparsing import col

# Format of date 
format_str = "%Y-%m-%d %H:%M:%S"
format_time = "%H:%M:%S"

# Step 1 ##################################################################################################

class Create_dataset:
    def __init__(self):
        self.df_Traffic = pd.DataFrame()
        self.df_Weather = pd.DataFrame()
        self.df_Incident = pd.DataFrame()
        # Store weather conditions for each timestamp
        self.weather_conditions = {}

    ##################################################################################################

    def time_stamp(self):
        data_list_old = pd.date_range(start="2026-01-01 00:00:00", end="2026-01-16 00:15:00", periods=1345)
        data_list = data_list_old.floor("s")
        return data_list

    ##################################################################################################

    def Weather_data(self):
        data_list = self.time_stamp()
        dict_data = {
            "time_stamp": [], "rainfall_mm": [], "visibility_km": [], "temperature": []
        }

        count = 0
        for i in range(1, 15):  # Days
            for j in range(1, 25):  # Hour
                for k in range(1, 5):  # Timestamp
                    if count == 1344:
                        break

                    start_timestamp = data_list[count]
                    dict_data["time_stamp"].append(start_timestamp)

                    # Generate rainfall independently (0-25mm)
                    rainfall = np.random.randint(0, 26)
                    dict_data["rainfall_mm"].append(rainfall)

                    # Visibility inversely correlated with rainfall
                    if rainfall >= 16:  
                        visibility = np.random.randint(0, 6)
                    else:
                        visibility = np.random.randint(5, 11)
                    
                    dict_data["visibility_km"].append(visibility)

                    hour_of_day = (count % 96) / 4  # 0-23 hours

                    if 12 <= hour_of_day <= 16:  # Afternoon 
                        temperature = np.random.randint(35, 41)  # Hot
                    elif 0 <= hour_of_day <= 6:  # Night 
                        temperature = np.random.randint(15, 21)  # Cool
                    else:  # Morning/Evening
                        temperature = np.random.randint(25, 35)  # Moderate

                    dict_data["temperature"].append(temperature)

                    # Store weather for traffic generation
                    self.weather_conditions[start_timestamp] = {
                        'rainfall': rainfall,
                        'visibility': visibility
                    }

                    count += 1

        self.df_Weather = pd.DataFrame(dict_data)
        self.df_Weather.to_csv("Weather.csv", index=False)  # Save to CSV

    ##################################################################################################

    def Traffic_sensor_data(self):

        data_list = self.time_stamp()

        # Updated peak hours: 8-11 AM and 6-10 PM
        peak_hrs = [["08:00:00", "10:59:59"], ["18:00:00", "21:59:59"]]
        peak_hours = []
        for lst in peak_hrs:
            start = datetime.strptime(lst[0], format_time).time()
            end = datetime.strptime(lst[1], format_time).time()
            peak_hours.append([start, end])
        
        dict_data = {
            "road_id": [], "sensor": [], "time_stamp": [], 
            "vehicle_count": [], "avg_speed": [], "lane_occupancy": []
        }

        count = 0
        for i in range(1, 15):  # Days
            for j in range(1, 25):  # Hour
                for k in range(1, 5):  # Timestamp
                    if count == 1344:
                        break

                    start_timestamp = data_list[count]
                    count += 1
                    
                    start_obj = datetime.strptime(str(start_timestamp), format_str)
                    time_start_str = start_obj.strftime("%H:%M:%S")
                    time_start = datetime.strptime(time_start_str, "%H:%M:%S").time()
                    time_start = start_obj.replace(microsecond=0).time()

                    # Check if weekend (Saturday=5, Sunday=6)
                    is_weekend = start_obj.weekday() >= 5

                    # Get weather for this timestamp
                    weather = self.weather_conditions.get(start_timestamp, {'visibility': 10, 'rainfall': 0})
                    visibility = weather['visibility']
                    
                    for r in range(1, 9):
                        for s in range(1, 4):
                            dict_data["road_id"].append(f"road_{r}") 
                            dict_data["sensor"].append(f"sensor_{s}")
                            dict_data["time_stamp"].append(start_timestamp)

                            is_peak = False
                            for start, end in peak_hours:
                                if start <= time_start <= end:
                                    is_peak = True
                                    break

                            # Generate base values based on peak hours
                            if is_peak:
                                base_speed = np.random.randint(15, 36)
                                vehicle_count = np.random.randint(601, 801)
                            else:
                                base_speed = np.random.randint(36, 91)
                                vehicle_count = np.random.randint(50, 601)

                            # Increase traffic on weekends (more vehicles)
                            if is_weekend:
                                vehicle_count = int(vehicle_count * np.random.uniform(1.2, 1.4))  # 20-40% more traffic
                                vehicle_count = min(vehicle_count, 800)

                            # Apply weather impact on speed (low visibility → lower speed)
                            if visibility < 3:
                                speed_reduction = np.random.uniform(0.4, 0.6)  # 40-60% reduction
                            elif visibility < 6:
                                speed_reduction = np.random.uniform(0.2, 0.4)  # 20-40% reduction
                            else:
                                speed_reduction = 0  # No reduction
                            
                            final_speed = int(base_speed * (1 - speed_reduction))
                            final_speed = np.clip(final_speed, 15, 90)  # Keep in valid range
                            
                            dict_data["vehicle_count"].append(vehicle_count)
                            dict_data["avg_speed"].append(final_speed)

                            lane_occ = (vehicle_count / 800) * 100  # Convert to percentage
                            dict_data["lane_occupancy"].append(round(lane_occ, 2))

        self.df_Traffic = pd.DataFrame(dict_data)
        self.df_Traffic.to_csv("Traffic_sensor_data.csv", index=False)  # Save to CSV

    ##################################################################################################

    def Incident_data(self):
        data_list = self.time_stamp()
        incidents = ["Signal-failure", "Construction", "Accident"]
        
        dict_data = {
            "time_stamp": [], "road_id": [], "incident_type": [], "severity": []
        }

        time_stamp_list = data_list.tolist()
        percentage = 0.02
        percent = math.ceil(len(data_list) * percentage)
        choice_list = random.choices(time_stamp_list, k = percent)

        for time_stamp in choice_list:
            dict_data["time_stamp"].append(time_stamp)

            road_id = np.random.randint(1, 9)
            road = f"road_{road_id}"
            dict_data["road_id"].append(road)

            incident_type = random.choices(incidents, weights=[5, 5, 5])
            dict_data["incident_type"].append(incident_type[0])
            
            severity_value = np.random.randint(0, 4)
            dict_data["severity"].append(severity_value)

        self.df_Incident = pd.DataFrame(dict_data)
        self.df_Incident.to_csv("Incident_data.csv", index=False)

        
# Step 2 and step 4 ##################################################################################################

class Create_dataframe:
    def __init__(self):
        self.df_Traffic = pd.DataFrame()
        self.df_Weather = pd.DataFrame()
        self.df_Incident = pd.DataFrame()

    def Make_dataframes(self):
    
        Traffic_sensor_data = pd.read_csv("Traffic_sensor_data.csv")
        Weather_data = pd.read_csv("Weather.csv")
        Incident_data = pd.read_csv("Incident_data.csv")

        
        Traffic_sensor_data = Traffic_sensor_data.loc[:, ~Traffic_sensor_data.columns.str.contains('^Unnamed')]
        Weather_data = Weather_data.loc[:, ~Weather_data.columns.str.contains('^Unnamed')]
        Incident_data = Incident_data.loc[:, ~Incident_data.columns.str.contains('^Unnamed')]

        self.df_Traffic = pd.DataFrame(Traffic_sensor_data)
        self.df_Weather = pd.DataFrame(Weather_data)
        self.df_Incident = pd.DataFrame(Incident_data)

        print(self.df_Traffic.shape)
        print(self.df_Weather.shape)
        print(self.df_Incident.shape)

        # Convert timestamp columns to datetime
        self.df_Traffic["time_stamp"] = pd.to_datetime(self.df_Traffic["time_stamp"])
        self.df_Weather["time_stamp"] = pd.to_datetime(self.df_Weather["time_stamp"])
        self.df_Incident["time_stamp"] = pd.to_datetime(self.df_Incident["time_stamp"])

        # Save the processed dataframes
        self.df_Traffic.to_csv("Traffic_sensor_data.csv", index=False) 
        self.df_Weather.to_csv("Weather.csv", index=False)
        self.df_Incident.to_csv("Incident_data.csv", index=False)

    def Merge_datasets(self):
        merged_df = pd.merge(self.df_Traffic, self.df_Weather, on="time_stamp", how="left")
        merged_df_final = pd.merge(merged_df, self.df_Incident, on=["time_stamp", "road_id"], how="left")
        merged_df_final = merged_df_final.replace({np.nan: "None"})
        merged_df_final.index.name = "Index"
        print(merged_df_final.shape)

        merged_df_final.to_csv("Merged_data.csv", index=False)

class Data_cleaning:
    def __init__(self):
        self.df_merged = pd.read_csv("Merged_data.csv")


    def Data_corruption(self):

        '''####### Missing value timestamp
        self.df_merged["time_stamp"] = pd.to_datetime(self.df_merged["time_stamp"])

        missing = np.random.randint(1, 32256, size=(50,))
        self.df_merged.loc[self.df_merged.iloc[:, 0].isin(missing), 'time_stamp'] = np.nan
        #print(self.df_merged.isnull().sum())'''
        
        ####### Duplicate value sensor
        duplicate = np.random.randint(1, 32256, size=(10,))
        self.df_merged = pd.concat([self.df_merged, self.df_merged.loc[duplicate]], ignore_index=True)
        # print(self.df_merged[-50:])

        ####### Outliers
        indice_outlier = np.random.randint(1, 32256, size=(20,))
        self.df_merged.loc[self.df_merged.iloc[:, 0].isin(indice_outlier), 'avg_speed'] = np.random.randint(91, 121)
        # print(self.df_merged["avg_speed"].value_counts())

        indice_outlier_v = np.random.randint(1, 32256, size=(20,))
        self.df_merged.loc[self.df_merged.iloc[:, 0].isin(indice_outlier_v), 'vehicle_count'] = np.random.randint(-50, 0)
        # print(self.df_merged["vehicle_count"].value_counts()) 


        ####### Dtype conversion of rainfall
        self.df_merged["rainfall_mm"] = self.df_merged["rainfall_mm"].astype("str")
        # print(self.df_merged.dtypes)

        self.df_merged.to_csv("corrupted_data.csv")
        
    def Data_cleaning(self):
        df_cleaned = pd.read_csv("corrupted_data.csv", index_col=0)

        # dtype conversion
        df_cleaned["rainfall_mm"] = pd.to_numeric(df_cleaned["rainfall_mm"])

        # outlier
        df_cleaned.loc[df_cleaned["avg_speed"] > 90, "avg_speed"] = int(df_cleaned["avg_speed"].mean())
        df_cleaned.loc[df_cleaned["vehicle_count"] < 0, "vehicle_count"] = int(df_cleaned["vehicle_count"].mean())

        # Data duplication
        #print(df_cleaned.shape)
        df_cleaned.drop_duplicates(ignore_index=True, inplace=True)
        #print(df_cleaned.shape)


        





# Main Function ##################################################################################################

def main():
    print("------------------------------------------")
    print("Creating dataset")
    Create_dataset_1 = Create_dataset()
    Create_dataset_1.Weather_data()
    Create_dataset_1.Traffic_sensor_data()
    Create_dataset_1.Incident_data()
    print("Datasets Created")
    print("------------------------------------------")

    Create_dataframe_1 = Create_dataframe()
    Create_dataframe_1.Make_dataframes()

    print("Merging datasets")
    Create_dataframe_1.Merge_datasets()
    print("Datasets Merged")
    print("------------------------------------------")

    Data_cleaning_1 = Data_cleaning()
    Data_cleaning_1.Data_corruption()
    Data_cleaning_1.Data_cleaning()




if __name__ == "__main__":
    main()


