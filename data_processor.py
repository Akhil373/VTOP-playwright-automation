import pandas as pd
from bs4 import BeautifulSoup
import os

def clean_file(input_file, output_file) -> None: 
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            stripped_line: str = line.strip()
            if stripped_line:
                outfile.write(stripped_line + '\n')

def html_to_csv(file_path, output_path) -> None: 
    html_string: str = ""
    with open(file_path) as f:
        html_string = f.read()

    soup = BeautifulSoup(html_string, 'html.parser') 
    data: list = []
    table_rows= soup.find_all('tr')

    for row in table_rows:
        all_cells = row.find_all(['th', 'td'])
        cols = [cell.get_text(strip=True) for cell in all_cells]
        data.append(cols)

    header = data[0]
    table_data = data[1:]
    df = pd.DataFrame(table_data, columns=header)
    
    print("---Academic Calendar---")
    print(df)
    df.to_csv(output_path, index=False) 
    
    print("\nData successfully saved to academic_calendar.csv") 