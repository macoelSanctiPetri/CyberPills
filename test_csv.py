import csv

def test_csv_parsing():
    input_file = 'contactos_profesores.csv'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        # It seems the file might not be standard CSV if it has ":::" or weird spacing, but let's try csv reader
        reader = csv.reader(f)
        header = next(reader)
        print(f"Header length: {len(header)}")
        print(f"Header: {header}")
        
        # We suspect email is around index 18 (19th column)
        # Header: ..., E-mail 1 - Label, E-mail 1 - Value, E-mail 2 - Label, E-mail 2 - Value
        try:
            email_idx = header.index('E-mail 1 - Value')
            print(f"Found 'E-mail 1 - Value' at index {email_idx}")
        except ValueError:
            print("Could not find 'E-mail 1 - Value' in header")
            return

        print("-" * 20)
        
        count = 0
        for row in reader:
            if len(row) <= email_idx:
                continue
                
            first_name = row[0]
            last_name = row[2]
            email = row[email_idx]
            
            # Print a few examples of likely teachers (non-students)
            # Students usually have class code in Phonetic First Name (index 3) or similar? 
            # In the file viewed: line 2 "Mario,,Prieto García,1bacha" -> Index 3 (Phonetic First Name) is '1bacha'.
            # Teachers found at the end had empty Index 3.
            
            phonetic_first = row[3]
            
            if not phonetic_first and email and '@' in email:
                 print(f"Teacher candidate: {first_name} {last_name} -> {email}")
                 count += 1
                 if count > 10:
                     break
                     
if __name__ == "__main__":
    test_csv_parsing()
