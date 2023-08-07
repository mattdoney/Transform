from flask import Flask, request, send_file, render_template
import pandas as pd

def transform_data(df, uplift_values, co2_threshold):
    # Filter the dataframe
    df = df[(df['CO2_g_per_km'] < co2_threshold) & (df['Commercial'] == 'N')]

    # Extract intCapID
    df['intCapID'] = df['David_Henley_Code'].str.lstrip('0').str.split('/').str[0]

    # Set intScheme
    df['intScheme'] = 4

    # Copy intTerm
    df['intTerm'] = df['Term']

    # Copy intMileage
    df['intMileage'] = df['Mileage']

    # Calculate mnyFinanceRental
    df['mnyFinanceRental'] = df.apply(
        lambda row: (
            ((row['Lease_Rental'] * (row['Term'] - 1)) + (6 * row['Lease_Rental'])) / row['Term']
        ) + uplift_values.get(row['Term'], 0),
        axis=1)

    # Set mnyServiceRental
    df['mnyServiceRental'] = df['Service_Rental']

    # Set intLeadTimeWeeks
    df['intLeadTimeWeeks'] = -1

    # Calculate strUniqueID
    df['strUniqueID'] = df['intCapID'].astype(str) + df['intTerm'].astype(str) + df['intMileage'].astype(str)

    # Return the new dataframe
    return df[['intCapID', 'intScheme', 'intTerm', 'intMileage', 'mnyFinanceRental', 'mnyServiceRental', 'intLeadTimeWeeks', 'strUniqueID']]

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    df = pd.read_csv(file)
    uplift_values = {
        24: request.form.get('uplift24', type=float),
        36: request.form.get('uplift36', type=float),
        48: request.form.get('uplift48', type=float),
        60: request.form.get('uplift60', type=float),
    }
    co2_threshold = request.form.get('co2threshold', type=float)

    # Call your transformation function here
    df = transform_data(df, uplift_values, co2_threshold)

    # Save the transformed dataframe to a new CSV file
    output_filename = 'transformed_data.csv'
    df.to_csv(output_filename, index=False)

    return send_file(output_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
