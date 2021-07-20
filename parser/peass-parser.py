#!/usr/bin/env python3

import sys
import re
import json

# Pattern to identify main section titles
TITLE1_PATTERN = r"════════════════════════════════════╣"
TITLE2_PATTERN = r"╔══════════╣"
TITLE3_PATTERN = r"══╣"
INFO_PATTERN = r"╚ "
TITLE_CHARS = ['═', '╔', '╣', '╚']

# Patterns for colors
## The order is important, the first string colored with a color will be the one selected (the same string cannot be colored with different colors)
COLORS = {
    "REDYELLOW": [r"\x1b\[1;31;103m"],
    "RED": [r"\x1b\[1;31m"],
    "GREEN": [r"\x1b\[1;32m"],
    "YELLOW": [r"\x1b\[1;33m"],
    "BLUE": [r"\x1b\[1;34m"],
    "LIGHT_MAGENTA": [r"\x1b\[1;95m"],
    "MAGENTA": [r"\x1b\[1;35m"],
    "CYAN": [r"\x1b\[1;36m"],
    "LIGHT_CYAN": [r"\x1b\[1;96m"],
    "LIGHT_GREY": [r"\x1b\[1;37m"],
    "DARKGREY": [r"\x1b\[1;90m"],
}


# Final JSON structure
FINAL_JSON = {}

#Constructing the structure
C_SECTION = FINAL_JSON
C_MAIN_SECTION = FINAL_JSON
C_2_SECTION = FINAL_JSON
C_3_SECTION = FINAL_JSON


 
    
def is_section(line: str, pattern: str) -> bool:
    """Returns a boolean

    Checks if line matches the pattern and returns True or False
    """
    return line.find(pattern) > -1 

def get_colors(line: str) -> dict:
    """Given a line return the colored strings"""

    colors = {}
    for c,regexs in COLORS.items():
        colors[c] = []
        for reg in regexs:
            for re_found in re.findall(reg+"(.+?)\x1b|$", line):
                re_found = clean_colors(re_found.strip())
                #Avoid having the same color for the same string
                if re_found and not any(re_found in values for values in colors.values()):
                    colors[c].append(re_found)
        
        if not colors[c]:
            del colors[c]
    
    return colors

def clean_title(line: str) -> str:
    """Given a title clean it"""
    for c in TITLE_CHARS:
        line = line.replace(c,"")
    
    line = line.encode("ascii", "ignore").decode() #Remove non ascii chars
    line = line.strip()
    return line

def clean_colors(line: str) -> str:
    """Given a line clean the colors inside of it"""

    for reg in re.findall(r'\x1b[^ ]+\dm', line):
        line = line.replace(reg,"")
    
    line = line.replace('\x1b',"") #Sometimes that byte stays
    line = line.strip()
    return line


def parse_title(line: str) -> str:
    """ Given a title, clean it"""

    return clean_colors(clean_title(line))


def parse_line(line: str):
    """Parse the given line adding it to the FINAL_JSON structure"""

    global FINAL_JSON, C_SECTION, C_MAIN_SECTION, C_2_SECTION, C_3_SECTION

    if is_section(line, TITLE1_PATTERN):
        title = parse_title(line)
        FINAL_JSON[title] = { "sections": {}, "lines": [], "infos": [] }
        C_MAIN_SECTION = FINAL_JSON[title]
        C_SECTION = C_MAIN_SECTION
    
    elif is_section(line, TITLE2_PATTERN):
        title = parse_title(line)
        C_MAIN_SECTION["sections"][title] = { "sections": {}, "lines": [], "infos": [] }
        C_2_SECTION = C_MAIN_SECTION["sections"][title]
        C_SECTION = C_2_SECTION

    elif is_section(line, TITLE3_PATTERN):
        title = parse_title(line)
        C_2_SECTION["sections"][title] = { "sections": {}, "lines": [], "infos": [] }
        C_3_SECTION = C_2_SECTION["sections"][title]
        C_SECTION = C_3_SECTION

    elif is_section(line, INFO_PATTERN):
        title = parse_title(line)
        C_SECTION["infos"].append(title)
    
    #If here, then it's text
    else:
        #If no main section parsed yet, pass
        if C_SECTION == {}:
            return

        C_SECTION["lines"].append({
            "raw_text": line,
            "clean_text": clean_colors(line),
            "colors": get_colors(line)
        })


def main():
    for line in open(OUTPUT_PATH, 'r').readlines():
        line = line.strip()
        if not line or not clean_colors(line): #Remove empty lines or lines just with colors hex
            continue

        parse_line(line)

    with open(JSON_PATH, "w") as f:
        json.dump(FINAL_JSON, f)


# Start execution
if __name__ == "__main__":
    try:
        OUTPUT_PATH = sys.argv[1]
        JSON_PATH = sys.argv[2]
    except IndexError as err:
        print("Error: Please pass the peas.out file and the path to save the json\n./peas-parser.py <output_file> <json_file.json>")
        sys.exit(1)
    
    main()
