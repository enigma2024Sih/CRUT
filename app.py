import streamlit as st
import pandas as pd

# Function to parse stops for handover points
def parse_stops(row):
    stops = [row['Starting Point']] + row['Intermediate Stoppages'].split(' - ') + [row['Final Stoppage']]
    return stops

# Function to find handover points
def find_handover_points(row, handover_points):
    stop_sequence = row['Stop Sequence']
    total_stops = len(stop_sequence)

    midpoint_index_start = int(total_stops * 0.4)  # 40%
    midpoint_index_end = int(total_stops * 0.6)  # 60%

    handovers = [
        stop for stop in stop_sequence[midpoint_index_start:midpoint_index_end]
        if stop.upper() in handover_points
    ]

    return handovers[-1] if handovers else None

# Main Streamlit app
def main():
    st.title("CURT")
    st.title("Fleet Management and Handover Analysis")
    
    st.sidebar.header("Upload Your Data")
    uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])
    
    if uploaded_file:
        # Load data
        df = pd.read_csv(uploaded_file)
        st.write("Uploaded Data:")
        st.dataframe(df.head())

        # Fleet Management Analysis
        st.header("Fleet Management Analysis")
        
        # Define in-city and out-city routes
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

        # Parse stop sequence
        df['Stop Sequence'] = df.apply(parse_stops, axis=1)

        # Calculate number of stops
        df['Number of Stops'] = df['Stop Sequence'].apply(len)

        # Define threshold for long/short route
        threshold = df['Number of Stops'].quantile(0.65)
        df['Route Type'] = df['Number of Stops'].apply(
            lambda x: 'Long Route' if x > threshold else 'Short Route'
        )

        df['Handover Points'] = df.apply(
            lambda row: find_handover_points(row, handover_points) 
            if row['Route Type'] == 'Long Route' else None,
            axis=1
        )
        
        st.write(f"Threshold for Long Route: {threshold}")
        st.write("Handover Analysis Data:")
        st.dataframe(df[['Route No.', 'Number of Stops', 'Route Type', 'Handover Points']])

        # Option to download processed data
        st.download_button(
            label="Download Processed Data",
            data=df.to_csv(index=False),
            file_name="processed_data.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
