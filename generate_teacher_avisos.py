import re
import html
import os
import csv
import unicodedata

def normalize_text(text):
    """
    Normalize text by removing accents, converting to lowercase, 
    and splitting into words.
    """
    if not text:
        return []
    # Normalize unicode characters (remove accents)
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    text = text.lower()
    # Remove non-alphanumeric characters (keep spaces)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    # Split into set of words
    return set(text.split())

def load_teacher_emails(csv_file):
    """
    Load teacher emails from CSV. 
    Returns a list of dicts: {'words': set(normalized_words), 'email': email, 'full_name': raw_name}
    """
    teachers_db = []
    
    if not os.path.exists(csv_file):
        print(f"Warning: {csv_file} not found. Emails will be skipped.")
        return teachers_db

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
            email_idx = header.index('E-mail 1 - Value')
            first_name_idx = 0
            last_name_idx = 2
            phonetic_idx = 3 # Used to filter students
        except ValueError:
            print("Error: Required columns not found in CSV.")
            return teachers_db
            
        for row in reader:
            if len(row) <= email_idx:
                continue
            
            first_name = row[first_name_idx].strip()
            last_name = row[last_name_idx].strip()
            phonetic_name = row[phonetic_idx].strip()
            email = row[email_idx].strip()
            
            if not first_name or not last_name or not email:
                continue
                
            if phonetic_name:
                continue
                
            full_name_raw = f"{first_name} {last_name}"
            words = normalize_text(full_name_raw)
            
            teachers_db.append({
                'words': words,
                'email': email,
                'full_name': full_name_raw
            })
            
    return teachers_db

def find_email(teacher_name_html, teachers_db):
    html_words = normalize_text(teacher_name_html)
    if not html_words:
        return ""
    
    candidates = []
    for entry in teachers_db:
        if html_words.issubset(entry['words']):
            candidates.append(entry)
    
    if len(candidates) == 1:
        return candidates[0]['email']
    elif len(candidates) > 1:
        return candidates[0]['email']
        
    return ""

def parse_and_generate():
    input_file = 'index.html'
    output_file = 'index_avisos.html'
    csv_file = 'contactos_profesores.csv'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    teachers_db = load_teacher_emails(csv_file)
    print(f"Loaded {len(teachers_db)} teacher contacts.")

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace('</div< /td>', '</div></td>')

    teacher_schedule = {} 

    rows = re.findall(r'<tr>(.*?)</tr>', content, re.DOTALL)
    
    for row in rows:
        cells = re.findall(r'<td.*?>(.*?)</td>', row, re.DOTALL)
        
        if len(cells) < 4:
            continue
            
        date = html.unescape(cells[0]).strip()
        day = html.unescape(cells[1]).strip()
        time = html.unescape(cells[2]).strip()
        
        # Simplified time info
        header_info = f"{date} ({day}) {time}"
        
        for col_html in cells[3:]:
            visit_chunks = col_html.split('class="visit"')
            valid_visits = visit_chunks[1:]
            
            for index, visit_html in enumerate(valid_visits):
                group_match = re.search(r'<div class="group">(.*?)</div>', visit_html)
                group = html.unescape(group_match.group(1)).strip() if group_match else "Desconocido"
                
                # Extract Pill Title
                pill_title_match = re.search(r'<strong>CyberPill:</strong>(.*?)(<ul|</div>)', visit_html, re.DOTALL)
                pill_title = html.unescape(pill_title_match.group(1)).strip() if pill_title_match else ""
                
                # Extract Pill List Items
                pill_items = re.findall(r'<li>(.*?)</li>', visit_html, re.DOTALL)
                pill_text = ". ".join([html.unescape(item).strip() for item in pill_items])
                
                full_comment = f"{pill_title}: {pill_text}" if pill_title and pill_text else (pill_title or pill_text)

                teacher_matches = re.findall(r'\(\s*<strong>(.*?)</strong>\s*\)', visit_html)
                
                timing = ""
                if index == 0:
                    timing = "Principios clase"
                elif index == 1:
                    timing = "Mitad clase"
                elif index == 2:
                    timing = "Final clase"
                else:
                    timing = "Durante clase"
                
                # Entry with Comment included
                entry = f"{header_info} | <strong>Grupo:</strong> {group} | <span class='timing'>{timing}</span> | <span class='comment'>{full_comment}</span>"
                
                for teacher_raw in teacher_matches:
                    teacher_name = html.unescape(teacher_raw).strip()
                    teacher_name_clean = " ".join(teacher_name.split())
                    
                    if teacher_name_clean not in teacher_schedule:
                        teacher_schedule[teacher_name_clean] = []
                    
                    if entry not in teacher_schedule[teacher_name_clean]:
                        teacher_schedule[teacher_name_clean].append(entry)

    sorted_teachers = sorted(teacher_schedule.keys())
    
    html_out = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Avisos Profesorado - CyberPills</title>
<style>
:root {
  --bg: #f6f7fb;
  --text: #111;
  --accent: #0b5f60;
  --border: #cfd6e4;
  --card: #fff;
  --timing: #e67e22;
}
body { font-family: Arial, sans-serif; margin: 24px; background: var(--bg); color: var(--text); }
h1 { color: var(--accent); margin-bottom: 24px; }
table { border-collapse: collapse; width: 100%; background: var(--card); box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }
th, td { border: 1px solid var(--border); padding: 12px; text-align: left; vertical-align: middle; }
th { background: #eef2f8; color: var(--accent); font-weight: bold; }
tr:nth-child(even) { background: #fcfcfd; }
.name { font-weight: bold; color: var(--accent); white-space: nowrap; }
.email { font-weight: normal; font-size: 0.85em; color: #555; display: block; margin-top: 2px;}
th:first-child, td:first-child { width: auto; min-width: 200px; }
.slots { line-height: 1.6; }
.timing { font-weight: bold; color: var(--timing); font-size: 0.95em; text-transform: uppercase; }
.comment { color: #555; font-style: italic; }
strong { color: #333; }
.slot-row { border-bottom: 1px solid #eee; padding: 4px 0; }
.slot-row:last-child { border-bottom: none; }
</style>
</head>
<body>
<h1>Avisos de visitas - Profesorado afectado</h1>
<table>
<thead>
<tr>
<th>Profesor/a</th>
<th>Detalle de Visitas</th>
</tr>
</thead>
<tbody>
"""

    for teacher in sorted_teachers:
        email = find_email(teacher, teachers_db)
        email_html = f"<span class='email'>{email}</span>" if email else ""
        
        slots_list = teacher_schedule[teacher]
        # Wrap each slot in a div class='slot-row' for better CSS control if needed, but keeping it simple with breaks
        # Actually user asked for everything in same line. 
        # But if a teacher has multiple visits, we still need lines separate? Yes, probably. 
        # The user said "intenta poner la fecha la hora el grupo la clase y el comentario en la misma linea".
        # This implies per visit.
        
        slots_html = ""
        for slot in slots_list:
             slots_html += f"<div class='slot-row'>{slot}</div>"
        
        html_out += f"<tr><td class='name'>{teacher}{email_html}</td><td class='slots'>{slots_html}</td></tr>\n"

    html_out += """</tbody>
</table>
</body>
</html>"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_out)
    
    print(f"Successfully created {output_file} with single-line entry format.")

if __name__ == "__main__":
    parse_and_generate()
