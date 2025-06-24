"""3. Extracting Table Data from a Wikipedia Page -- Lakshmi
Objective: Scrape tabular data, such as historical population data from a Wikipedia page.
Data Types: Structured tables (HTML tables).
Approach:
Use BeautifulSoup to parse the HTML, locating tables by class or ID.
Convert the table data to Pandas DataFrames for easier manipulation and storage.
Save the data as a CSV for further analysis.
Example Site: Any Wikipedia page with a table, like a country’s demographics or sports statistics."""
import requests
import pandas as pd
from bs4 import BeautifulSoup
# Step 1: Specify the URL of the Wikipedia page
url = "https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population"
# Step 2: Send a request to the URL
response = requests.get(url)
# Step 3: Parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')
# Step 4: Locate the table (get the first matching table)
table = soup.find('table',
                  class_='wikitable')
# Check if the table was found
if table is None:
    print("Table not found!")
else:
    # Step 5: Extract headers
    headers = []
    for th in table.find_all('th'):
        headers.append(th.get_text(strip=True))
    print("Headers:", headers)
    # Step 6: Extract rows
    data = []
    # Step 6: Extract rows with improved handling
    for tr in table.find_all('tr')[1:]:  # Skip the header row
        # Extract all cells, including potential nested tables
        cells = tr.find_all('td')
        # If no cells found, continue to the next row
        if not cells:
            continue
        # Extract text from each cell
        row = [td.get_text(strip=True) for td in cells]

        # Check if row length matches expected number of columns
        if len(row) == len(headers):  # Ensure it matches the headers
            data.append(row)
        else:
            print(f"Row with mismatched length: {row}")
print(f"Number of data rows: {len(data)}")
print("Extracted data:", data)
    # Step 7: Create a Pandas DataFrame
df = pd.DataFrame(data, columns=headers)
print(f"Number of headers: {len(headers)}")
print("dataframe cotent: ",df)
    # Step 8: Save the DataFrame as a CSV file
csv_file_path = 'C:\\Users\\sange\\Desktop\\web scraping_csv\\demographics_of_india.csv'
df.to_csv(csv_file_path, index=False)
print("Data has been scraped and saved to 'demographics_of_india.csv'.")
