import re
from parsepbp_utils import parse_hitlocation, HITLOCATION_REGEX, debugprint, FIELD_BY_NUM
from utils import construct_player_dict

std_mod_strs = {
    "BF": ", bunt foul",
    "C": ", called strike",
    "FO": ", forceout",
    "DP": ", double play",
    "NDP": ", no double play",
    "TP": ", triple play",
    "OBS": ", obstruction on the play",
    "BINT": ", batter interference on the play",
    "RINT": ", runner interference on the play",
    "UINT": ", umpire interference on the play",
    "FINT": ", fan interference on the play",
    "INT": ", unspecified interference on the play",
    "PASS": ", runner called out for passing",
    "MREV": ", manager review",
    "UREV": ", umpire review",
    "AP": ", appeal play",
    "BOOT": ", batting out of turn",
    "COUR": ", courtesy runner", # TODO: this may not always be in the right place,
    "COUF": ", courtesy fielder takes the field during the plate appearance" # Rare
}

fielder_names = {
    "1": "pitcher",
    "2": "catcher",
    "3": "1B",
    "4": "2B",
    "5": "3B",
    "6": "shortstop",
    "7": "LF",
    "8": "CF",
    "9": "RF"
}

PLAYERS = construct_player_dict()
NARRATE = False

def describe_hitlocation(code):
    return f" on a {parse_hitlocation(code)}" if NARRATE else ""

def describe_fielders(nums):
    return ", ".join([fielder_names[chr] for chr in nums]) if NARRATE else ""

# In-park non-HR hit
def std_hit(id, row, modinfo, basicplay, unusualplayflag, outdatedrelayflag):
    printstr = f"hit by {PLAYERS[row[3]]}"
    locstr = ""
    if basicplay[0] == "S":
        printstr = f"{PLAYERS[row[3]]} singles"
    elif basicplay[0] == "D":
        printstr = f"{PLAYERS[row[3]]} doubles"
    elif basicplay[0] == "T":
        printstr = f"{PLAYERS[row[3]]} triples"
    if len(basicplay) > 1:
        printstr += f", fielded by {describe_fielders(basicplay[1:])}"
    for k in range(1, len(modinfo)):
        if modinfo[k].endswith("#"):
            modinfo[k] = modinfo[k][:-1]
        if modinfo[k] in std_mod_strs:
            printstr += std_mod_strs[modinfo[k]]
        elif re.fullmatch(HITLOCATION_REGEX, modinfo[k]) and not modinfo[k] == "":
            printstr += describe_hitlocation(modinfo[k])
            locstr = modinfo[k]
        elif re.fullmatch(r"TH[1-3H]?", modinfo[k]):
            if modinfo[k] == "TH":
                printstr += f", throw to unspecified base"
            else:
                printstr += f", throw to {modinfo[k][2]}"
        elif re.fullmatch(r"R[1-9]+", modinfo[k]):
            printstr += f", subsequent relay to fielder(s) {modinfo[k][1:]} fails to secure any outs"
        elif re.fullmatch(r"((R|U)[1-9]+)+", modinfo[k]):
            if outdatedrelayflag:
                debugprint("Outdated relay format", id, row)
        elif modinfo[k] == "BR":
            printstr += f", runner hit by batted ball"
        elif modinfo[k] == "R":
            if outdatedrelayflag:
                debugprint("Raw relay with no fielders", id, row)
        elif unusualplayflag:
            debugprint("Unexpected hit modifier", id, row)
    return printstr, locstr

# Ground rule double
def grd(id, row, modinfo, basicplay, unusualplayflag):
    printstr = f"ground-rule double batted by {PLAYERS[row[3]]}"
    locstr = ""
    if len(basicplay) > 3:
        if basicplay[3:] == "7":
            printstr += f" to left field"
        elif basicplay[3:] == "8":
            printstr += f" to center field"
        elif basicplay[3:] == "9":
            printstr += f" to right field"
        elif basicplay[3:] == "5":
            # As of the end of the 2025 season, this has happened four times.
            # Once in a 2018 Rays game from getting stuck in padding, once in a 2017 Astros game from fan interference,
            # once in a 2010 Athletics game probably also from getting stuck although I could find no record, and once
            # in a 1912 Washington Senators game because Ray Morgan smashed a ball so hard off of Charlie Deal's shin
            # that it then flew into the stands. Ouch!
            printstr += f" to 3B"
        elif basicplay[3:] == "89":
            # As of the end of the 2025 season, this has happened twice, once in a 2015 Tigers game and once in a 2016 Padres game.
            printstr += f" to right center field"
        elif unusualplayflag:
            print(f"Odd ground-rule double location: {basicplay} for game {id} play {str(row)}")
            printstr += f" to {basicplay[3:]}"
    for k in range(1, len(modinfo)):
        if modinfo[k].endswith("#"):
            modinfo[k] = modinfo[k][:-1]
        if modinfo[k] in std_mod_strs:
            printstr += std_mod_strs[modinfo[k]]
        elif re.fullmatch(HITLOCATION_REGEX, modinfo[k]) and not modinfo[k] == "":
            printstr += describe_hitlocation(modinfo[k])
            locstr = modinfo[k]
        elif unusualplayflag:
            debugprint("Unexpected ground rule double modifier", id, row)
    return printstr, locstr

# Home run (numbers indicate fielders for inside-the-parkers)
def hr(id, row, modinfo, basicplay, unusualplayflag):
    printstr = f"{PLAYERS[row[3]]} homers"
    tpe = ""
    location = ""
    if len(basicplay) > 2:
        printstr = f"inside-the-park home run batted by {PLAYERS[row[3]]} fielded by {describe_fielders(basicplay[2:])}"
        tpe = "I"
        for k in range(1, len(modinfo)):
            if modinfo[k].endswith("#"):
                modinfo[k] = modinfo[k][:-1]
            if modinfo[k] == "IPHR":
                continue
            elif re.fullmatch(HITLOCATION_REGEX, modinfo[k]) and not modinfo[k] == "":
                printstr += describe_hitlocation(modinfo[k])
                location = modinfo[k]
            elif re.fullmatch(r"R[1-9]+", modinfo[k]):
                printstr += f", subsequent relay to fielder(s) {modinfo[k][1:]} fails to secure any outs"
            elif unusualplayflag:
                debugprint("Unexpected inside-the-park HR modifier", id, row)
    else:
        printstr = f"home run batted by {PLAYERS[row[3]]}"
        tpe = "H"
        for k in range(1, len(modinfo)):
            if modinfo[k].endswith("#"):
                modinfo[k] = modinfo[k][:-1]
            if modinfo[k] in std_mod_strs:
                printstr += std_mod_strs[modinfo[k]]
            elif modinfo[k] == "IPHR":
                printstr += f", inside the park"
                tpe = "I"
            elif modinfo[k] == "7":
                printstr += f" to left field"
            elif modinfo[k] == "78":
                printstr += f" to left center field"
            elif modinfo[k] == "8":
                printstr += f" to center field"
            elif modinfo[k] == "89":
                printstr += f" to right center field"
            elif modinfo[k] == "9":
                printstr += f" to right field"
            elif re.fullmatch(HITLOCATION_REGEX, modinfo[k]) and not modinfo[k] == "":
                printstr += describe_hitlocation(modinfo[k])
                location = modinfo[k]
            elif unusualplayflag:
                debugprint("Unexpected home run modifier", id, row)
    return printstr, tpe, location

# Strikeout
def so(id, row, modinfo, basicplay, unusualplayflag):
    printstr = f"{PLAYERS[row[3]]} strikes out"
    k_type = "K"
    if len(basicplay) > 1:
        printstr = f"{PLAYERS[row[3]]} strikes out on a dropped third strike, fielded by {describe_fielders(basicplay[1:])}"
        if basicplay == "K23":
            printstr = f"{PLAYERS[row[3]]} strikes out on a dropped third strike, catcher throws down to 1B ({basicplay})"
        elif basicplay in ["K13", "K213"]:
            printstr = f"{PLAYERS[row[3]]} strikes out on a dropped third strike that caroms away from the catcher, pitcher gets to it and throws to 1B ({basicplay})"
        else:
            printstr = f"{PLAYERS[row[3]]} strikes out on an unusual dropped third strike ({basicplay})"
    
    for k in range(1, len(modinfo)):
        if modinfo[k].endswith("#"):
            modinfo[k] = modinfo[k][:-1]
        if modinfo[k] in std_mod_strs:
            printstr += std_mod_strs[modinfo[k]]
        elif modinfo[k] == "C":
            printstr += f" on called strike"
            k_type = "C"
        elif modinfo[k] == "S":
            printstr += f" on swinging strike"
            k_type = "S"
        elif re.fullmatch(r"R[1-9]+", modinfo[k]):
            printstr += f", subsequent relay to fielder(s) {modinfo[k][1:]} fails to secure any outs"
        elif unusualplayflag:
            debugprint("Unexpected strikeout modifier", id, row)
    return printstr, k_type

# Walk
def walk(id, row, modinfo, unusualplayflag, outdatedrelayflag):
    printstr = f"{PLAYERS[row[3]]} walks"
    for k in range(1, len(modinfo)):
        if modinfo[k] in std_mod_strs:
            printstr += std_mod_strs[modinfo[k]]
        elif re.fullmatch(r"R[4-6]", modinfo[k]):
            # This may be completely wrong, since all but one W/R[num]s are to fielders when runners are already being forced.
            # The one instance where this isn't the case, in TEX199709200, is a 3X3 which contradicts R's nominal role as being
            # a relay that does not secure any outs.
            printstr += f", subsequent relay to fielder(s) {modinfo[k][1:]}"
        elif re.fullmatch(r"((R|U)[1-9]+)+", modinfo[k]):
            if outdatedrelayflag:
                debugprint("Outdated relay format", id, row)
        elif unusualplayflag:
            debugprint("Unexpected walk modifier", id, row)
    return printstr

# Hit by pitch
def hbp(id, row, modinfo, unusualplayflag):
    printstr = f"{PLAYERS[row[3]]} hit by pitch"
    for k in range(1,len(modinfo)):
        if modinfo[k] in std_mod_strs:
            printstr += std_mod_strs[modinfo[k]]
        elif unusualplayflag:
            debugprint("Unexpected hit by pitch modifier", id, row)
    return printstr

# Wild pitch
def wp(id, row, modinfo, unusualplayflag):
    printstr = f"wild pitch during {PLAYERS[row[3]]} at-bat"
    for k in range(1,len(modinfo)):
        if modinfo[k] in std_mod_strs:
            printstr += std_mod_strs[modinfo[k]]
        elif re.fullmatch(r"R[1-6U]+", modinfo[k]):
            printstr += f", subsequent relay to fielder(s) {modinfo[k][1:]} fails to secure any outs"
        elif unusualplayflag:
            debugprint("Unexpected wild pitch modifier", id, row)
    return printstr

# Passed ball
def pb(id, row, modinfo, unusualplayflag):
    printstr = f"passed ball during {PLAYERS[row[3]]} at-bat"
    for k in range(1,len(modinfo)):
        if modinfo[k] in std_mod_strs:
            printstr += std_mod_strs[modinfo[k]]
        elif re.fullmatch(r"R[1-6U]+", modinfo[k]):
            printstr += f", subsequent relay to fielder(s) {modinfo[k][1:]} fails to secure any outs"
        elif unusualplayflag:
            debugprint("Unexpected passed ball modifier", id, row)
    return printstr

# Balk
def bk(id, row, modinfo, unusualplayflag):
    printstr = f"balk during {PLAYERS[row[3]]} at-bat"
    for k in range(1,len(modinfo)):
        if modinfo[k] in std_mod_strs:
            printstr += std_mod_strs[modinfo[k]]
        elif unusualplayflag:
            debugprint("Unexpected balk modifier", id, row)
    return printstr

# Field play
def field(id, row, modinfo, runnerinfo, unusualplayflag, outdatedrelayflag):
    printstr = f"field play, "

    # Combined play involving a field play occurs when there is an error on the strikeout/walk.
    if "+" in row[6].split(".")[0].split("/")[0]:
        row[6] = row[6][row[6].index("+")+1:]

    advinfo = [-2, -2, -2, -2]
    play_sections = [x.split("(") for x in row[6].split(".")[0].split("/")[0].split(")") if x != ""]
    autoadv = False
    error_flag = False
    strsecs = []
    for play_sec in play_sections:
        if "E" in play_sec[0]:
            fielders = play_sec[0].split("E")
            if len(fielders[0]) > 0:
                strsecs.append(f"fielded by {describe_fielders(fielders[0])} before error by {fielder_names[fielders[1]]}")
            else:
                strsecs.append(f"error by {fielder_names[fielders[1]]}")
            advinfo[0] = 1
            error_flag = True
            continue
        out = 0
        if len(play_sec) > 1:
            strsecs.append(f"fielded by {describe_fielders(play_sec[0])} to get runner on {play_sec[1]} out")
            autoadv = True
            if play_sec[1] == "B":
                out = 0
            else:
                out = int(play_sec[1])
        else:
            strsecs.append(f"fielded by {describe_fielders(play_sec[0])} to get batter out")
        advinfo[out] = -1
    fo_flag = False
    for mod in modinfo:
        if "FO" in mod:
            fo_flag = True
    if fo_flag and not error_flag:
        loopflag = False
        for i in range(len(advinfo)):
            if advinfo[i] == -1 or loopflag:
                loopflag = True
                continue
            else:
                advinfo[i] = i + 1
    if fo_flag or "(B)" in row[6]:
        autoadv = False
    # Only forced runners (every base behind them occupied) auto-advance, and never onto a base the runner ahead keeps.
    # Runners that hold are often not annotated, e.g. 64(1)3/GDP.3-3 with the bases loaded ends the inning with the
    # runner on 3rd staying put, so the runner on 2nd must stay put too. Go lead runner first so holds cascade backward.
    # Explicit advance info (e.g. 3-3) isn't merged in until after this function, so check for runners who explicitly hold
    holds = set()
    if "." in row[6]:
        for adv in row[6].split(".")[1].split(";"):
            if len(adv) >= 3 and adv[1] == "-" and adv[0] == adv[2]:
                holds.add(int(adv[0]))
    for i in range(len(advinfo)-1, -1, -1):
        forced = all(runnerinfo[j] != "" for j in range(i))
        blocked = i + 1 < 4 and runnerinfo[i+1] != "" and (i + 1 in holds or advinfo[i+1] in (-2, i + 1))
        if autoadv and forced and not blocked and runnerinfo[i] != "" and advinfo[i] == -2:
            advinfo[i] = i + 1
    
    printstr += "; next ".join(strsecs)
    location = ""
    sac = False

    for k in range(1, len(modinfo)):
        if modinfo[k].endswith("#"):
            modinfo[k] = modinfo[k][:-1]
        if "!" in modinfo[k]:
            modinfo[k] = modinfo[k].replace("!", "")
        
        if modinfo[k] in std_mod_strs:
            printstr += std_mod_strs[modinfo[k]]
        elif re.fullmatch(HITLOCATION_REGEX, modinfo[k]) and not modinfo[k] == "":
            printstr += describe_hitlocation(modinfo[k])
            location = modinfo[k]
        elif re.fullmatch(r"R[1-9]+", modinfo[k]):
            printstr += f", subsequent relay to fielder(s) {modinfo[k][1:]} fails to secure any outs"
        elif re.fullmatch(r"((R|U)[1-9]+)+", modinfo[k]):
            if outdatedrelayflag:
                debugprint("Outdated relay format", id, row)
        elif modinfo[k] == "R":
            if outdatedrelayflag:
                debugprint("Raw relay with no fielders", id, row)
        elif modinfo[k] == "FL":
            printstr += f" on foul ball"
        elif modinfo[k] == "SF":
            printstr += f", sac fly"
            sac = True
        elif modinfo[k] == "SH":
            printstr += f", sac hit"
            sac = True
        elif modinfo[k] == "IF":
            printstr += f", infield fly called on play"
        elif modinfo[k] == "GDP":
            printstr += f", ground into double play"
        elif modinfo[k] == "LDP":
            printstr += f", line into double play"
        elif modinfo[k] == "FDP":
            printstr += f", fly into double play"
        elif modinfo[k] == "BGDP":
            printstr += f", bunt ground into double play"
        elif modinfo[k] == "BPDP":
            printstr += f", bunt pop up into double play"
        elif modinfo[k] == "GTP":
            printstr += f", ground into triple play"
        elif modinfo[k] == "LTP":
            printstr += f", line into triple play"
        elif re.fullmatch(r"TH[1-3H]?", modinfo[k]):
            if modinfo[k] == "TH":
                printstr += f", throw to unspecified base"
            else:
                printstr += f", throw to {modinfo[k][2]}"
        elif modinfo[k] == "COUB":
            # As of the end of the 2025 season, this has happened only once, not only for field plays but in all MLB outcomes ever.
            # July 12, 1915, Washington Nationals @ Chicago White Sox. Top of the 3rd, Chick Gandil at the plate. On a swing and miss,
            # Gandil injures his knee and is unable to continue. With the White Sox's permission, Rip Williams is allowed to take his
            # place just for the at-bat. Williams grounds out, and after the end of the inning, Gandil returns to play 1B.
            printstr += f", courtesy batter"
        else:
            if unusualplayflag:
                debugprint("Unexpected field play modifier", id, row)

    return (printstr, advinfo, location, sac)

# Dropped foul fly ball error
def fle(id, row, modinfo, basicplay, unusualplayflag):
    printstr = f"dropped foul fly ball error during {PLAYERS[row[3]]} at-bat by {FIELD_BY_NUM[int(basicplay[3])-1]}"
    location = ""
    for k in range(1, len(modinfo)):
        if re.fullmatch(HITLOCATION_REGEX, modinfo[k]) and not modinfo[k] == "":
            printstr += describe_hitlocation(modinfo[k])
            location = modinfo[k]
        elif modinfo[k] == "FL":
            if unusualplayflag:
                debugprint("Redundant foul marker on FLE", id, row)
        elif unusualplayflag:
            debugprint("Unexpected FLE modifier", id, row)
    return printstr, location

# Fielder's choice
def fc(id, row, modinfo, basicplay, unusualplayflag, outdatedrelayflag):
    printstr = f"{PLAYERS[row[3]]} reaches on fielder's choice"
    fielder = 0
    location = ""
    sac = False
    if len(basicplay) > 2:
        printstr += f" by {FIELD_BY_NUM[int(basicplay[2])-1]}"
        fielder = int(basicplay[2])
    for k in range(1, len(modinfo)):
        if modinfo[k] in std_mod_strs:
            printstr += std_mod_strs[modinfo[k]]
        elif re.fullmatch(HITLOCATION_REGEX, modinfo[k]) and not modinfo[k] == "":
            location = modinfo[k]
            printstr += describe_hitlocation(modinfo[k])
        elif re.fullmatch(r"TH[1-3H]?", modinfo[k]):
            if modinfo[k] == "TH":
                printstr += f", throw to unspecified base"
            else:
                printstr += f", throw to {modinfo[k][2]}"
        elif re.fullmatch(r"R[1-9]+", modinfo[k]):
            printstr += f", subsequent relay to fielder(s) {modinfo[k][1:]} fails to secure any outs"
        elif re.fullmatch(r"((R|U)[1-9]+)+", modinfo[k]):
            if outdatedrelayflag:
                debugprint("Outdated relay format", id, row)
        elif modinfo[k] == "SH":
            printstr += f", sac hit"
            sac = True
        elif modinfo[k] == "SF":
            printstr += f", sac fly"
            sac = True
        elif modinfo[k] == "GDP":
            printstr += f", ground ball double play"
        elif modinfo[k] == "FDP":
            # As of the end of the 2025 season, this has happened once.
            # May 8, 2013, Minnesota Twins @ Boston Red Sox. Top of the 7th, Ryan Doumit at the plate, Trevor Plouffe on 1st, and
            # Josh Willingham on 2nd. Doumit hits a fly ball to center field for what is initially ruled a single, but later turned
            # to a fielder's choice. Somehow, the fielding credit apparently goes CF-SS-2B-1B with Doumit out on the way to 2nd, and
            # then Plouffe out on the way to 3rd with credit to the 2B.
            printstr += f", fly ball double play"
        elif unusualplayflag:
            debugprint("Unexpected fielder's choice modifier", id, row)
    return printstr, fielder, location, sac

# Stolen base
def sb(id, row, modinfo, basicplay, unusualplayflag, outdatedrelayflag, hitlocationflag):
    sections = basicplay.split(";")
    secstrs = []
    for section in sections:
        if section == "":
            continue
            
        secstr = f"base {section[2]} stolen"
        loc = -1
        if section[2] == "H":
            loc = 3
        else:
            loc = int(section[2]) - 1
        if section[-3:] == "TUR":
            secstr = f"{secstr}, team unearned run"
        elif section[-2:] == "UR":
            secstr = f"{secstr}, unearned run"
        secstrs += [secstr]
    printstr = f"during {PLAYERS[row[3]]} at-bat, " + "; ".join(secstrs)

    for k in range(1, len(modinfo)):
        if modinfo[k] in std_mod_strs:
            printstr += std_mod_strs[modinfo[k]]
        elif re.fullmatch(HITLOCATION_REGEX, modinfo[k]) and not modinfo[k] == "":
            if hitlocationflag:
                debugprint("Hit location on stolen base", id, row)
        elif re.fullmatch(r"R[1-9]+", modinfo[k]):
            printstr += f", subsequent relay to fielder(s) {modinfo[k][1:]} fails to secure any outs"
        elif re.fullmatch(r"((R|U)[1-9]+)+", modinfo[k]):
            if outdatedrelayflag:
                debugprint("Outdated relay format", id, row)
        elif re.fullmatch(r"TH[1-3H]", modinfo[k]):
            printstr += f", throw to {modinfo[k][2]}"
        elif unusualplayflag:
            debugprint("Unexpected stolen base modifier", id, row)
    return printstr

# Pickoff / caught stealing / both
def pocs(id, row, modinfo, basicplay, unusualplayflag, outdatedrelayflag, hitlocationflag):
    printstr = f"PO/CS/POCS during {PLAYERS[row[3]]} at-bat"
    advinfo = [-2, -2, -2, -2]
    pos = [False, False, False]
    css = [False, False, False]

    sections = basicplay.split(";")
    secstrs = []
    for section in sections:
        if section == "":
            continue

        loc = -1

        secstr = ""
        if section.startswith("POCS"):
            secstr = f"runner picked off while attempting to steal {section[4]}"
            if section[4] == "H":
                loc = 3
            else:
                loc = int(section[4]) - 1
            pos[loc-1] = True
            css[loc-1] = True
            if not "E" in section:
                advinfo[loc] = -1
            else:
                advinfo[loc] = loc + 1
            section = section[5:]
        elif section.startswith("PO"):
            secstr = f"runner picked off {section[2]}"
            pos[int(section[2])-1] = True
            if not "E" in section:
                advinfo[int(section[2])] = -1
            section = section[3:]
        elif section.startswith("CS"):
            secstr = f"runner caught stealing {section[2]}"
            if section[2] == "H":
                loc = 3
            else:
                loc = int(section[2]) - 1
            css[loc-1] = True
            if not "E" in section:
                advinfo[loc] = -1
            else:
                advinfo[loc] = loc + 1
            section = section[3:]
        subsections = section.replace(")","").split("(")
        for subsec in subsections:
            if subsec == "":
                continue
                
            if re.fullmatch(r"[1-9]+", subsec):
                secstr = f"{secstr}, fielded by {describe_fielders(subsec)}"
            elif re.fullmatch(r"E[1-9](\/TH)?", subsec):
                if subsec.endswith("/TH"):
                    secstr = f"{secstr}, throwing error by {subsec[1]} prevents out"
                else:
                    secstr = f"{secstr}, error by {subsec[1]} prevents out"
            elif re.fullmatch(r"[1-9]+(E[1-9](\/TH)?)", subsec):
                if subsec.endswith("/TH"):
                    secstr = f"{secstr}, fielded by {describe_fielders(subsec[:-5])} until throwing error by {fielder_names[subsec[-4]]} prevents out"
                else:
                    secstr = f"{secstr}, fielded by {describe_fielders(subsec[:-2])} until final error by {fielder_names[subsec[-1]]}"
            elif subsec == "UR":
                secstr = f"{secstr}, unearned run"
            elif unusualplayflag:
                debugprint("Unexpected PO/CS/POCS type", id, row)
        secstrs += [secstr]
    printstr = f"during {PLAYERS[row[3]]} at-bat, " + "; ".join(secstrs)

    for k in range(1, len(modinfo)):
        if modinfo[k].endswith("#"):
            modinfo[k] = modinfo[k][:-1]

        if modinfo[k] in std_mod_strs:
            printstr += std_mod_strs[modinfo[k]]
        elif re.fullmatch(r"TH[1-3H]?", modinfo[k]):
            if modinfo[k] == "TH":
                printstr += f", throw to unspecified base"
            else:
                printstr += f", throw to {modinfo[k][2]}"
        elif re.fullmatch(r"R[1-9]+", modinfo[k]):
            printstr += f", subsequent relay to fielder(s) {modinfo[k][1:]} fails to secure any outs"
        elif re.fullmatch(r"((R|U)[1-9]+)+", modinfo[k]):
            if outdatedrelayflag:
                debugprint("Outdated relay format", id, row)
        elif re.fullmatch(HITLOCATION_REGEX, modinfo[k]) and not modinfo[k] == "":
            if hitlocationflag:
                debugprint("Hit location on PO/CS/POCS", id, row)
        elif unusualplayflag:
            debugprint("Unexpected PO/CS/POCS modifier", id, row)
    return (printstr, advinfo, pos, css)

# Out advancing
def oa(id, row, modinfo, unusualplayflag, outdatedrelayflag):
    printstr = f"during {PLAYERS[row[3]]} at-bat, runner out advancing"
    for k in range(1, len(modinfo)):
        if modinfo[k] in std_mod_strs:
            printstr += std_mod_strs[modinfo[k]]
        elif re.fullmatch(r"R[1-9]+", modinfo[k]):
            printstr += f", subsequent relay to fielder(s) {modinfo[k][1:]} fails to secure any outs"
        elif re.fullmatch(r"((R|U)[1-9]+)+", modinfo[k]):
            if outdatedrelayflag:
                debugprint("Outdated relay format", id, row)
        elif unusualplayflag:
            debugprint("Unexpected out advancing modifier", id, row)
    return printstr

# Interference, should always come with modifier(s)
def inf(id, row, modinfo, unusualplayflag):
    if len(modinfo) == 1:
        if unusualplayflag:
            debugprint("Interference without fielder information", id, row)
        return "Unspecified interference"
    
    printstr = f"during {PLAYERS[row[3]]} at-bat, interference/obstruction"
    
    hitlocation_index = -1
    hitlocation_string = ""
    
    fielder = 0
    if modinfo[1] == "E2" or modinfo[1] == "E2#":
        if len(modinfo) == 2:
            # Technically this could be obstruction, but there is no further available info in the play
            printstr = f"during {PLAYERS[row[3]]} at-bat, (presumed) catcher's interference"
        else:
            basestr = f"during {PLAYERS[row[3]]} at-bat, catcher's interference"
            appendstr = ""
            obstruction_flag = False
            for k in range(2, len(modinfo)):
                if re.fullmatch(HITLOCATION_REGEX, modinfo[k]) and not modinfo[k] == "":
                    basestr = f"during {PLAYERS[row[3]]} at-bat, catcher obstruction"
                    appendstr += describe_hitlocation(modinfo[k])
                elif modinfo[k] == "OBS":
                    basestr = f"during {PLAYERS[row[3]]} at-bat, catcher obstruction"
                elif modinfo[k] == "INT":
                    continue
                elif unusualplayflag:
                    debugprint("Unexpected interference modifier", id, row)
            printstr = basestr + appendstr
        fielder = 2
    elif modinfo[1] in ["E1", "E3"]:
        # Fielder obstruction
        printstr = f"during {PLAYERS[row[3]]} at-bat, obstruction (generally of batter running to first) by {FIELD_BY_NUM[int(modinfo[1][1])-1]}"
        for k in range(2, len(modinfo)):
            if re.fullmatch(HITLOCATION_REGEX, modinfo[k]) and not modinfo[k] == "":
                printstr += describe_hitlocation(modinfo[k])
            elif (modinfo[k] == "OBS"):
                # Since all such fielder 'interferences' are actually obstructions, technically
                # all such plays should have this flag
                continue
            elif re.fullmatch(r"R[1-6U]+", modinfo[k]):
                printstr += f", subsequent relay to fielder(s) {modinfo[k][1:]} fails to secure any outs"
            elif unusualplayflag:
                debugprint("Unexpected interference modifier", id, row)
        fielder = int(modinfo[1][1])
    elif modinfo[1] == "E4":
        printstr = f"during {PLAYERS[row[3]]} at-bat, defensive shift violation by {FIELD_BY_NUM[int(modinfo[1][1])-1]}"
        for k in range(2, len(modinfo)):
            if re.fullmatch(HITLOCATION_REGEX, modinfo[k]):
                printstr += describe_hitlocation(modinfo[k])
            elif unusualplayflag:
                debugprint("Unexpected interference modifier", id, row)
        fielder = 4
    elif unusualplayflag:
        debugprint("Interference not of expected format C/E[1-4](#)", id, row)
    return printstr, fielder