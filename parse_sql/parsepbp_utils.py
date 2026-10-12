import re

hittype = {
    "G": "ground ball",
    "L": "line drive",
    "P": "pop fly",
    "F": "fly ball"
}

zones = {
    "1": "the pitcher's mound",
    "15": "the area left of the pitcher's mound",
    "13": "the area right of the pitcher's mound",
    "2": "home plate",
    "25": "the left infield line",
    "23": "the right infield line",
    "2L": "left of home plate",
    "2R": "right of home plate",
    "5L": "third base line",
    "5": "third base",
    "56": "3B-shortstop hole",
    "6": "shortstop",
    "6M": "left of second base",
    "46": "second base",
    "4M": "right of second base",
    "4": "2B",
    "34": "1B-2B hole",
    "3": "first base",
    "3L": "first base line",
    "7L": "left outfield line",
    "7": "left field",
    "78": "left center field",
    "8L": "slight left center field",
    "8": "center field",
    "8R": "slight right center field",
    "89": "right center field",
    "9": "right field",
    "9L": "right outfield line",
}

def parse_hitlocation(code):
    if code == "":
        raise
    hitcode = code
    translated=""
    if hitcode.endswith("+"):
        translated="hard-hit "
        hitcode = hitcode[:-1]
    elif hitcode.endswith("-"):
        translated="soft-hit "
        hitcode = hitcode[:-1]
    if hitcode.startswith("B"):
        translated = translated + "bunt "
        hitcode = hitcode[1:]
    if len(hitcode) > 0 and hitcode[0] in hittype:
        translated = translated + hittype[hitcode[0]]
        hitcode = hitcode[1:]
    else:
        translated += "batted ball"

    wall = False
    if hitcode.endswith("W"):
        wall = True
        hitcode = hitcode[:-1]
    
    foul = False
    if hitcode.endswith("F"):
        foul = True
        hitcode = hitcode[:-1]
    
    length = False
    if hitcode.endswith("XD"):
        length = True
        translated += " to extra-deep "
        hitcode = hitcode[:-2]
    if hitcode.endswith("S"):
        length = True
        translated += " to short "
        hitcode = hitcode[:-1]
    if hitcode.endswith("D"):
        length = True
        translated += " to deep "
        hitcode = hitcode[:-1]

    if len(hitcode) > 0:
        if not length:
            translated += " to "
        if hitcode.endswith("M") and hitcode[:-1] in ["7", "78", "8L", "8", "8R", "89", "9", "5", "3", "7L", "9L"]:
            translated += "medium-deep "
            hitcode = hitcode[:-1]
        translated += zones[hitcode]

    if foul:
        translated += " in foul territory"
    if wall:
        translated += " off the wall"
    
    return translated

HITLOCATION_REGEX = r"B?[GLPF]?(7|78|8L|8|8R|89|9|56|6|6M|46|4M|4|34|5|3|7L|9L|1|15|13|2|25|23|2L|2R|5L|3L)?(S|M|D|XD)?F?W?(\+|-)?"

def parse_advinfo(id, row, advinfo, unusualplayflag):
    printstrs = []
    explicit_advinfo = [-2, -2, -2, -2]
    for adv in advinfo:
        printstr = ""
        basicplay = adv[:3]
        mods = adv[3:].replace("#", "").replace("!","").replace(")","").split("(")
        if basicplay[1] == "-":
            printstr = "runner on " + basicplay[0] + " goes to " + basicplay[2]

            fr = -1
            if basicplay[0] == "B":
                fr = 0
            else:
                fr = int(basicplay[0])

            to = -1
            if basicplay[2] == "H":
                to = 4
            else:
                to = int(basicplay[2])
            
            explicit_advinfo[fr] = to

            for mod in mods:
                modstr = ""
                mods2 = mod.split("/")
                for mod2 in mods2:
                    if mod2 == "":
                        continue
                    elif re.fullmatch(r"E[1-9]", mod2):
                        modstr = ", error by " + mod2[-1]
                    elif re.fullmatch(r"TH[1-3H]", mod2):
                        modstr = modstr + " on throw to " + mod2[-1]
                    elif mod2 == "TH":
                        modstr = modstr + " on throw"
                    elif mod2 == "PB":
                        modstr = modstr + ", on passed ball"
                    elif mod2 == "WP":
                        modstr = modstr + ", on wild pitch"
                    elif mod2 == "RBI":
                        modstr = modstr + ", RBI"
                    elif mod2 == "NR":
                        modstr = modstr + ", no RBI"
                    elif mod2 == "UR":
                        modstr = modstr + ", unearned run"
                    elif mod2 == "TUR":
                        modstr = modstr + ", team unearned run"
                    elif unusualplayflag:
                        debugprint(f"Unexpected advance information modifier", id, row)
                printstr = printstr + modstr
        elif basicplay[1] == "X":
            printstr = basicplay[0] + " is/should be out on the way to " + basicplay[2]

            fr = -1
            if basicplay[0] == "B":
                fr = 0
            else:
                fr = int(basicplay[0])

            to = -1
            if basicplay[2] == "H":
                to = 4
            else:
                to = int(basicplay[2])
            
            explicit_advinfo[fr] = -1

            still_first = True
            for mod in mods:
                if mod == "":
                    continue
                modstr = ""
                mods2 = mod.split("/")
                for mod2 in mods2:
                    if mod2 == "":
                        continue
                    elif re.fullmatch(r"[1-9]+", mod2):
                        modstr = ", fielded " + mod2
                        explicit_advinfo[fr] = -1
                    elif re.fullmatch(r"E[1-9]", mod2):
                        modstr = ", error by " + mod2[-1]
                        if still_first:
                            explicit_advinfo[fr] = to
                    elif re.fullmatch(r"[1-9]+E[1-9]", mod2):
                        modstr = ", fielded " + mod2[:-2] + " with final error by " + mod2[-1]
                        if still_first:
                            explicit_advinfo[fr] = to
                    elif re.fullmatch(r"TH[1-3H]", mod2):
                        modstr = modstr + " on throw to " + mod2[-1]
                    elif mod2 == "TH":
                        modstr = modstr + " on throw"
                    elif mod2 == "WP":
                        modstr = modstr + ", on passed ball"
                    elif mod2 == "NR":
                        modstr = modstr + ", no RBI"
                    elif mod2 == "UR":
                        modstr = modstr + ", unearned run"
                    elif unusualplayflag:
                        debugprint(f"Unexpected advance information modifier", id, row)
                printstr = printstr + modstr
                still_first = False
        printstrs = printstrs + [printstr]
    retstr = "; ".join(printstrs)
    return (retstr, explicit_advinfo)

def debugprint(debug_type, id, row):
    print(f"{debug_type} in {id}: [{', '.join(row)}]")

FIELD_BY_NUM = ['pitcher','catcher','1B','2B','3B','shortstop','LF','CF','RF']