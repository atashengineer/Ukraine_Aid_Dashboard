# Ukraine Aid Dashboard

## Overview
The Ukraine Aid Dashboard is a web-based visualization tool that provides insights into international aid sent to Ukraine. This project transforms raw data from the Kiel Institute for the World Economy using Python and Pandas, and then visualizes it on a dynamic web page.

## Features
- **Data Transformation:** The raw data is processed using Pandas and converted into JSON format.
- **Dynamic Charts:** The data is visualized using interactive charts on an HTML page.
- **Aid Breakdown:** The dashboard categorizes aid into military, financial, and humanitarian assistance.
- **Quarterly Trends:** Displays aid contributions over time.
- **Top Aid Packages:** Highlights major financial and military aid commitments.

## Data Source
The data used in this project is sourced from the **Kiel Institute for the World Economy**, which tracks international aid to Ukraine.

## Technologies Used
- **Python & Pandas**: Data extraction and transformation
- **JavaScript & Chart.js**: Visualization of aid data
- **HTML & CSS**: Front-end design and layout

## Installation & Usage
1. Clone this repository:
   ```bash
   git clone https://github.com/atashengineer/Ukraine_Aid_Dashboard.git
   ```
2. Navigate to the project directory:
   ```bash
   cd ukraine-aid-dashboard
   ```
3. Install dependencies (optional for additional data processing):
   ```bash
   pip install pandas
   ```
4. Run the data processing script to generate `data.json`:
   ```bash
   python sandbox.py
   ```
5. Open `index.html` in a web browser to view the dashboard.

## Project Structure
```
ukraine-aid-dashboard/
│── data.json          # Processed aid data in JSON format
│── index.html         # Main webpage displaying visualizations
│── sandbox.py         # Python script to process and transform data
│── README.md          # Project documentation
```

## Contribution
Contributions are welcome! If you have improvements or additional features, feel free to fork the repository and create a pull request.

## License
This project is open-source and available under the MIT License.

## Acknowledgment
Special thanks to the **Kiel Institute for the World Economy** for providing detailed data on Ukraine aid efforts.

