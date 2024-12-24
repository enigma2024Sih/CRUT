import streamlit as st
import pandas as pd
import numpy as np

# Utility Functions
def parse_stops(row):
    """Parse stop sequence from route columns."""
    try:
        stops = [row['Starting Point']] + row['Intermediate Stoppages'].split(' - ') + [row['Final Stoppage']]
        return stops
    except AttributeError:
        return []

def find_handover_points(stop_sequence, handover_points):
    """Find handover points in the middle 40-60% of the stop sequence."""
    total_stops = len(stop_sequence)
    midpoint_index_start = int(total_stops * 0.4)
    midpoint_index_end = int(total_stops * 0.6)

    handovers = [
        stop for stop in stop_sequence[midpoint_index_start:midpoint_index_end]
        if stop.upper() in handover_points
    ]
    return handovers[-1] if handovers else None

def classify_occupancy(occupancy):
    """Classify occupancy status based on percentage."""
    if occupancy >= 80:
        return 'Overcrowded'
    elif occupancy <= 30:
        return 'Underutilized'
    else:
        return 'Optimal'

def is_peak_hour(time, morning_peak=(8, 10), evening_peak=(17, 18)):
    """Check if the given time is within peak hours."""
    if pd.isnull(time):
        return False
    return (morning_peak[0] <= time.hour < morning_peak[1]) or (evening_peak[0] <= time.hour < evening_peak[1])

# Main Streamlit App
def main():
    st.title("CURT Fleet Management and Handover Analysis")
    
    st.sidebar.header("Upload Your Data")
    uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file:
        # Load data
        df = pd.read_csv(uploaded_file)
        st.write("Uploaded Data:")
        st.dataframe(df.head())

        # Define route categories
        in_city_routes = [
            '9', '09 S', '11S', '12', '12S', '13', '13S', '16', '16S',
            '19', '19S', '20', '20 S', '21', '21 S', '23', '23 S',
            '24', '24 S', '24E', '25', '25 S', '26', '26 S', '27',
            '27 S', '28', '28 S', '29', '29 S', '29E', '30', '30 S',
            '31', '31S', '32', '32 S', '33', '33 S', '34', '34 S',
            '35', '35 S', '36', '36 S', '39', '39S', '40', '40S',
            '42', '42S'
        ]
        out_city_routes = [
            '10', '10S', '17', '17S', '18', '18S', '22 A', '22 B',
            '22 S', '22B S', '37', '37 S', '38', '38S', '41', '41S',
            '43', '43S', '50', '50S', '51', '52', '52S', '53', '54',
            '54S', '70', '70S', '71', '71S', '80', '80 S', '81',
            '81 S', '81S', '82', '82 S', '83', '83 S'
        ]

        def mark_route_type(route):
            if route in in_city_routes:
                return "In-City"
            elif route in out_city_routes:
                return "Out-City"
            else:
                return "Unknown"

        # Fleet Management Analysis
        st.header("Fleet Management Analysis")
        df['City Route Type'] = df['Route No.'].astype(str).apply(mark_route_type)
        st.write("Fleet Management Data:")
        st.dataframe(df[['Route No.', 'City Route Type']])

        # Handover Analysis
        st.header("Handover Analysis")
        handover_points = {
            point.upper() for point in {
                'ACHARYA VIHAR', 'AIRPORT GATE', 'BARAMUNDA ISBT', 
                'BHUBANESWAR RAILWAY STATION', 'CUTTACK RAILWAY STATION', 
                'JAYADEV VIHAR', 'KHANDAGIRI SQUARE', 'SISHUPALGARH',
                'NUAGAON', 'LINGRAJ TEMPLE ROAD', 'GOURI NAGAR', 
                'STATE BANK SQUARE, CDA', 'RAJ KISHORE MARG',
                'KIIT SQUARE', 'NANDANKANAN ZOOLOGICAL PARK', 
                'PHULNAKHARA JUNCTION', 'RASULGARH SQUARE', 
                'VANI VIHAR'
            }
        }

        df['Stop Sequence'] = df.apply(parse_stops, axis=1)
        df['Number of Stops'] = df['Stop Sequence'].apply(len)

        threshold = df['Number of Stops'].quantile(0.65)
        df['Route Type'] = df['Number of Stops'].apply(
            lambda x: 'Long Route' if x > threshold else 'Short Route'
        )

        df['Handover Points'] = df.apply(
            lambda row: find_handover_points(row['Stop Sequence'], handover_points)
            if row['Route Type'] == 'Long Route' else None,
            axis=1
        )

        st.write(f"Threshold for Long Route: {threshold}")
        st.write("Handover Analysis Data:")
        st.dataframe(df[['Route No.', 'Number of Stops', 'Route Type', 'Handover Points']])
        
        # Occupancy Analysis
        st.header("Occupancy Analysis")
        df['Start Time'] = pd.to_datetime(df['Start Time'], errors='coerce')
        df['Peak Hour'] = df['Start Time'].apply(is_peak_hour)
        df['Peak Hour'] = df['Peak Hour'].replace({True: "Yes", False: "No"})  # Convert Boolean to string

        np.random.seed(42)
        df['Occupancy'] = np.random.randint(0, 100, size=len(df))
        df['Occupancy Status'] = df['Occupancy'].apply(classify_occupancy)

        st.write("Occupancy Analysis Data:")
        st.dataframe(df[['Route No.', 'Start Time', 'Peak Hour', 'Occupancy', 'Occupancy Status']])


        # Download Processed Data
        st.download_button(
            label="Download Processed Data",
            data=df.to_csv(index=False),
            file_name="processed_data.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
