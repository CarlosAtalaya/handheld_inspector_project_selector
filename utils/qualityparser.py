'''
    qualityparser.py

    Extract costumer quality criteria info from pdf's tables and save in csv.
    ~Adhoc module.

    Expected PDF layout:

    ┌─────────────────────────────────────────────┐
    │                 │Table 1│                   │
    │                                             │
    │              4.x DEFECT NAME                │
    ├─────────────────────────────────────────────┤
    │  Surface   │  Evaluation A  │  Evaluation B │
    ├────────────┼────────────────┼───────────────┤
    │     A      │     Value A1   │    Value B1   │
    │     B      │     Value A2   │    Value B2   │
    │     C      │     Value A3   │    Value B3   │
    └────────────┴────────────────┴───────────────┘
    Notes:
    - The defect sections starts with a header like '4.X DEFECT NAME'.
    - There are 2 tables per page, we want to parse the 2nd.
    - Each table may have 2 or 3 columns (Evaluation A and B may share criteria
        and thus be merged in 1 column).
    - Surface category column can be either {A, B, C} or 'all'.

    Csv Ouput Layout:
    Defect  |  Surface Quality  |  Finish  |  Criteria
    --------------------------------------------------
    Chip    |  A                |  Painted |  Not acceptable

'''
import fitz  # requires pymupdf installation
import re
import csv


file_path = 'standards.pdf'
skip_pages = 1
csv_name = 'costumer_quality_criteria.csv'
csv_columns = ['Defect', 'Surface Quality', 'Finish', 'Criteria']

rows = []
with fitz.open(file_path) as doc:
    for i, page in enumerate(doc[skip_pages:], start=skip_pages):

        # Get all text from page
        page_text = page.get_text()

        # Find defect name on page
        # Pattern:
        # '4\.\d+' →  4. follow by one or more digits.
        # '\s+' →  One or more blank spaces.
        # '[A-Z]' →  Any letter from A to Z.
        # '[^\n]' →  Zero or more characters that are not new line.
        title_matches = re.finditer(r'(4\.\d+\s+[A-Z][^\n]*)', page_text)

        for idx, match in enumerate(title_matches):
            title = match.group(0)
            # Remove characters from defect name
            # Pattern:
            # '^\d+\.\d+' →  From start of the line, digit(s) + . + digit(s)
            # '\s*' →  Zero or more blank spaces.
            # strip() →  Remove blank spaces at the beginning and end.
            title = re.sub(r'^\d+\.\d+\s*', '', title).strip()

            # TABLES
            page_tables = page.find_tables()  # Find all tables on page
            table = page_tables.tables[1].extract()  # Get second table
            # Remove rows that have empty or 'None' cells
            table = [
                row
                for row in table
                if all(cell not in ('', None) for cell in row)
            ]
            # Replace '\n' for ' ' in cells
            table = [
                [
                    cell.replace('\n', ' ').strip('"') if isinstance(cell, str)
                    else cell
                    for cell in row
                ]
                for row in table
            ]

            # Get info from table
            headers = table[0]
            num_columns = len(headers)

            for row in table[1:]:

                surface_quality = row[0]
                if surface_quality == 'All':
                    surface_quality_list = ['A', 'B', 'C']
                else:
                    surface_quality_list = [surface_quality]

                if num_columns == 2:
                    painted_criteria = visual_criteria = row[1]

                if num_columns == 3:
                    painted_criteria = row[1]
                    visual_criteria = row[2]

                for surface_quality in surface_quality_list:
                    rows.append(
                        [title, surface_quality, 'Painted', painted_criteria]
                    )
                    rows.append(
                        [title, surface_quality, 'Visual', visual_criteria]
                    )

# Write table info to csv
with open(csv_name, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(csv_columns)
    writer.writerows(rows)
