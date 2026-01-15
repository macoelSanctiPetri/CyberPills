import os

def fix_typos():
    input_file = 'index.html'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define replacements
    replacements = [
        ("&#191;Qui&#233;n est&#225; dentro de tu cuenta_", "&#191;Qui&#233;n est&#225; dentro de tu cuenta?"),
        ("&#191;Sabes qui&#233;n te est&#225; mirando_", "&#191;Sabes qui&#233;n te est&#225; mirando?"),
        ("Me han robado la cuenta_ 5 pasos", "Me han robado la cuenta: 5 pasos"),
        ("El acosador no manda solo_ el grupo", "El acosador no manda solo, el grupo"),
        ("No es broma_ es ciberacoso", "No es broma, es ciberacoso"),
        ("No es ligar_ es grooming", "No es ligar, es grooming"),
        ("PAU_ el mensaje", "PAU: el mensaje"),
        ("No te hackean_ te infectan", "No te hackean, te infectan"),
        ("Ransomware_ el d&#237;a", "Ransomware: el d&#237;a"),
        ("Wi-Fi p&#250;blico_ c&#243;modo", "Wi-Fi p&#250;blico: c&#243;modo"),
        ("No era mi amigo_ era", "No era mi amigo, era"),
        ("No te calles_", "No te calles!"),
        # Add plain text versions just in case unescaped versions exist
        ("¿Quién está dentro de tu cuenta_", "¿Quién está dentro de tu cuenta?"),
        ("¿Sabes quién te está mirando_", "¿Sabes quién te está mirando?"),
        # Variations found in viewing
        ("No pagues. No negocies. No te calles_", "No pagues. No negocies. No te calles!"),
    ]
    
    new_content = content
    count_replacements = 0
    
    for old, new in replacements:
        if old in new_content:
            occurrences = new_content.count(old)
            new_content = new_content.replace(old, new)
            print(f"Replaced {occurrences} occurrences of '{old}' with '{new}'")
            count_replacements += occurrences
            
    if count_replacements > 0:
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"\nFixed {count_replacements} typos in {input_file}.")
    else:
        print("No typos found to fix.")

if __name__ == "__main__":
    fix_typos()
