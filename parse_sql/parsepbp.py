from __future__ import annotations

import csv, re, sqlite3
from collections import defaultdict
from pathlib import Path

from parse_sql.play_objects.balk import Balk
from parse_sql.play_objects.defensiveindifference import DefensiveIndifference
from parse_sql.play_objects.droppedfoulerror import DroppedFoulError
from parse_sql.play_objects.fielderschoice import FieldersChoice
from parse_sql.play_objects.fieldplay import FieldPlay
from parse_sql.play_objects.hit import Hit
from parse_sql.play_objects.hitbypitch import HitByPitch
from parse_sql.play_objects.interference import Interference
from parse_sql.play_objects.outadvancing import OutAdvancing
from parse_sql.play_objects.passedball import PassedBall
from parse_sql.play_objects.pickoffcaughtsteal import PickOffCaughtStealing
from parse_sql.play_objects.play import Play
from parse_sql.play_objects.sacs import Sacs
from parse_sql.play_objects.stolenbase import StolenBase
from parse_sql.play_objects.strikeout import Strikeout
from parse_sql.play_objects.walk import Walk
from parse_sql.play_objects.wildpitch import WildPitch
from parse_sql.parsepbp_utils import parse_advinfo, debugprint
from parse_sql.parsepbp_scenarios import *
import parse_sql.parsepbp_scenarios as parsepbp_scenarios
from parse_sql.utils import get_filenames

def push_up(runner_info: list[int]) -> list[int]:
    a = [0, 1, 2, 3]
    i = 0
    while i < len(runner_info) and not runner_info[i] == "":
        i = i + 1
    last_assign = i
    for j in range(0, last_assign):
        a[j] = a[j] + 1
    return a

def auto_advance(runner_info: list[int], bases: int, batter_pos: int = None) -> list[int]:
    a = [-2, -2, -2, -2]
    for i in range(len(runner_info)):
        if not runner_info[i] == "":
            a[i] = min(i + bases, 4)
    if not batter_pos == None:
        a[0] = batter_pos
    return a

# Rows are queued per insert statement and written with executemany once per file, which is much faster than one execute per row
def add_to_sql(sql_obj, narrateflag: bool, pending: defaultdict[str, list[tuple]]) -> None:
    values = sql_obj()
    if narrateflag:
        print(sql_obj.TABLE_INSERT, values)
    pending[sql_obj.TABLE_INSERT].append(values)

# printstr is the natural language parsing of the play for display
# expected_advinfo is the default expected advance information based on the play; actual advance info supersedes where available

# Main
def db_by_year(root: Path, dataroot: str, gametype: str, year: int) -> None:
    eventfiles = get_filenames(root / dataroot / gametype)

    narrateflag = False
    extranarrateflag = False
    unusualplayflag = True
    outdatedrelayflag = False
    hitlocationflag = False
    parsepbp_scenarios.NARRATE = narrateflag or extranarrateflag

    id=''
    inn = -1
    half = -1
    outs = 0
    fielders = [[""] * 9, [""] * 9]

    search_files = [file for file in eventfiles if str(year) in file.name]
    
    (root / "dbs" / f"dbs_{gametype}").mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(root / "dbs" / f"dbs_{gametype}" / f"{year}.db")
    cur = con.cursor()
    cur.execute(Play.TABLE_DELETE)
    cur.execute(Play.TABLE_CREATE)
    cur.execute(Balk.TABLE_DELETE)
    cur.execute(Balk.TABLE_CREATE)
    cur.execute(DefensiveIndifference.TABLE_DELETE)
    cur.execute(DefensiveIndifference.TABLE_CREATE)
    cur.execute(DroppedFoulError.TABLE_DELETE)
    cur.execute(DroppedFoulError.TABLE_CREATE)
    cur.execute(FieldersChoice.TABLE_DELETE)
    cur.execute(FieldersChoice.TABLE_CREATE)
    cur.execute(FieldPlay.TABLE_DELETE)
    cur.execute(FieldPlay.TABLE_CREATE)
    cur.execute(Hit.TABLE_DELETE)
    cur.execute(Hit.TABLE_CREATE)
    cur.execute(HitByPitch.TABLE_DELETE)
    cur.execute(HitByPitch.TABLE_CREATE)
    cur.execute(Interference.TABLE_DELETE)
    cur.execute(Interference.TABLE_CREATE)
    cur.execute(OutAdvancing.TABLE_DELETE)
    cur.execute(OutAdvancing.TABLE_CREATE)
    cur.execute(PassedBall.TABLE_DELETE)
    cur.execute(PassedBall.TABLE_CREATE)
    cur.execute(PickOffCaughtStealing.TABLE_DELETE)
    cur.execute(PickOffCaughtStealing.TABLE_CREATE)
    cur.execute(Sacs.TABLE_DELETE)
    cur.execute(Sacs.TABLE_CREATE)
    cur.execute(StolenBase.TABLE_DELETE)
    cur.execute(StolenBase.TABLE_CREATE)
    cur.execute(Strikeout.TABLE_DELETE)
    cur.execute(Strikeout.TABLE_CREATE)
    cur.execute(Walk.TABLE_DELETE)
    cur.execute(Walk.TABLE_CREATE)
    cur.execute(WildPitch.TABLE_DELETE)
    cur.execute(WildPitch.TABLE_CREATE)

    runner_info = ["", "", "", ""]
    runs = [0, 0]
    radj_runner = ("", -1)
    playNum = -1
    for filename in search_files:
        pending = defaultdict(list)
        with open(filename, newline='', encoding="utf8") as csvfile:
            print(f"Processing {filename}")
            logreader = csv.reader(csvfile)

            for row in logreader:
                if row[0] == 'id':
                    id = row[1]
                    if narrateflag or extranarrateflag:
                        print(f"\n{id}")
                    fielders = [[""] * 9, [""] * 9]
                    runs = [0, 0]
                    playNum = 0
                if row[0] == 'start':
                    if int(row[5]) <= 9:
                        fielders[int(row[3])][int(row[5])-1] = row[1]
                if row[0] == 'play':
                    if row[6] != "NP":
                        playNum += 1
                    if not inn == int(row[1]) or not half == int(row[2]):
                        inn = int(row[1])
                        half = int(row[2])
                        outs = 0

                        runner_info = ["", "", "", ""]

                        if narrateflag or extranarrateflag:
                            print()
                    if radj_runner[0]:
                        runner_info[radj_runner[1]] = radj_runner[0]
                        radj_runner = ("", -1)

                    for chr in ["#", "?", "!"]:
                        row[6] = row[6].replace(chr, "")

                    parts = row[6].split(".")
                    play = parts[0]
                    modinfo = play.split('/')
                    basicplay = modinfo[0]

                    runner_info[0] = row[3]

                    # Basic preprocessing to remove extraneous characters and to fix up
                    if(basicplay.endswith('#') or basicplay.endswith('?')):
                        # Uncertain play
                        basicplay = basicplay[:-1]
                    elif(basicplay.endswith('+') or basicplay.endswith('-')):
                        # + indicates hard-hit, - indicates soft-hit
                        basicplay = basicplay[:-1]
                    if('!' in basicplay):
                        # Excellent play, may occur for more than one fielder hence the full replaces
                        basicplay = basicplay.replace('!','')

                    # Throwing errors are annotated E[fielder]/TH, and the / causes regex errors
                    if(re.fullmatch(r"((K|W)\+)*(PO|CS|POCS)[1-3]\([1-9]*E[1-6]", basicplay)):
                        # There has never been a PO/CS/POCS with a throwing error charged to an outfielder, so we use [1-6] for now.
                        # Also there has never been a CS/POCS of home with a throwing error, so we use [1-3] for now.
                        if(modinfo[1] == "TH)"):
                            basicplay=basicplay+"/TH)"
                            modinfo[0:2] = ['/'.join(modinfo[0:2])]
                        else:
                            print(f"Unexpected ending in play format: {play} for game {id} play {row}")
                            raise
                    
                    printstr, expected_advinfo = "", [-2, -2, -2, -2]
                    basictype = ""

                    ## Batter-oriented events
                    if re.fullmatch(r"(S|D|T)[1-9]*", basicplay):
                        # In-park non-HR hit
                        printstr, location = std_hit(id, row, modinfo, basicplay, unusualplayflag, outdatedrelayflag)
                        if basicplay[0] == "S":
                            # Despite what one might expect, simply advancing runners up one doesn't work for one specific reason
                            # Sometimes, a batter singles but runners don't move. When there are multiple runners that don't move,
                            # runners after the lead runner may not have that advance info specifically listed
                            # For example, with runners on 2nd and 3rd, a single may be annotated S.3-3 instead of S.3-3;2-2
                            expected_advinfo = auto_advance(runner_info, 0, batter_pos=1)
                            basictype = "S"
                            single_sql = Hit(id, playNum, "S", location)
                            add_to_sql(single_sql, extranarrateflag, pending)
                        elif basicplay[0] == "D":
                            expected_advinfo = auto_advance(runner_info, 0, batter_pos=2)
                            basictype = "D"
                            double_sql = Hit(id, playNum, "D", location)
                            add_to_sql(double_sql, extranarrateflag, pending)
                        elif basicplay[0] == "T":
                            expected_advinfo = auto_advance(runner_info, 0, batter_pos=3)
                            basictype = "T"
                            triple_sql = Hit(id, playNum, "T", location)
                            add_to_sql(triple_sql, extranarrateflag, pending)
                    elif re.fullmatch(r"DGR[1-9]*",basicplay):
                        # Ground-rule double
                        printstr, location = grd(id, row, modinfo, basicplay, unusualplayflag)
                        expected_advinfo = auto_advance(runner_info, 2)
                        basictype = "DG"
                        grd_sql = Hit(id, playNum, "G", location)
                        add_to_sql(grd_sql, extranarrateflag, pending)
                    elif re.fullmatch(r"HR[3-9]*",basicplay):
                        # Home run (numbers indicate fielders for inside-the-parkers)
                        printstr, tpe, location = hr(id, row, modinfo, basicplay, unusualplayflag)
                        expected_advinfo = auto_advance(runner_info, 4)
                        basictype = "HR"
                        hr_sql = Hit(id, playNum, tpe, location)
                        add_to_sql(hr_sql, extranarrateflag, pending)
                    
                    ## Pitcher-oriented events
                    elif re.fullmatch(r"K\d*",basicplay):
                        # Strikeout
                        printstr, k_type = so(id, row, modinfo, basicplay, unusualplayflag)
                        expected_advinfo = auto_advance(runner_info, 0, batter_pos=-1)
                        basictype = "K"
                        k_sql = Strikeout(id, playNum, k_type)
                        add_to_sql(k_sql, extranarrateflag, pending)
                    elif(basicplay == 'W'):
                        # Walk
                        printstr = walk(id, row, modinfo, unusualplayflag, outdatedrelayflag)
                        expected_advinfo = push_up(runner_info)
                        basictype = "W"
                        walk_sql = Walk(id, playNum, False)
                        add_to_sql(walk_sql, extranarrateflag, pending)
                    elif(basicplay == 'I' or basicplay == 'IW'):
                        # Intentional walk
                        printstr = f"{row[3]} intentionally walked"
                        expected_advinfo = push_up(runner_info)
                        for k in range(1, len(modinfo)):
                            if modinfo[k] == "MREV":
                                printstr += ", manager review for pickoff"
                            elif unusualplayflag:
                                debugprint("Unexpected modifier on intentional walk", id, row)
                        basictype = "IW"
                        iwalk_sql = Walk(id, playNum, True)
                        add_to_sql(iwalk_sql, extranarrateflag, pending)
                    elif("+" in basicplay):
                        # Combined play, mostly strikeout + some other event or (intentional) walk{ + }some other event
                        secs = basicplay.split("+")
                        firstplay = secs[0]
                        firststr = ""
                        firstadv = [0, 1, 2, 3]
                        if re.fullmatch(r"K\d*",firstplay):
                            firststr, k_type = so(id, row, [], firstplay, unusualplayflag)
                            firstadv = auto_advance(runner_info, 0, batter_pos=-1)
                            k_sql = Strikeout(id, playNum, k_type)
                            add_to_sql(k_sql, extranarrateflag, pending)
                        elif firstplay == "W":
                            firststr = walk(id, row, [], firstplay, unusualplayflag)
                            firstadv = push_up(runner_info)
                            walk_sql = Walk(id, playNum, False)
                            add_to_sql(walk_sql, extranarrateflag, pending)
                        elif firstplay == "I" or firstplay == "IW":
                            firststr = f"{row[3]} intentionally walked"
                            firstadv = push_up(runner_info)
                            iwalk_sql = Walk(id, playNum, True)
                            add_to_sql(iwalk_sql, extranarrateflag, pending)
                        basictype = "CM"
                            
                        addplay = secs[1]
                        secondstr = ""
                        secondadv = [0, 1, 2, 3]
                        if re.fullmatch(r"((CS|POCS)[1-3H]\([1-9]+\);)*((PO|CS|POCS)[1-3H]\([1-9]*(E[1-9](\/TH)?)?\)(\(T?UR\))?)", addplay):
                            secondstr, secondadv, pos, css = pocs(id, row, modinfo, addplay, unusualplayflag, outdatedrelayflag, hitlocationflag)
                            pocs_sql = PickOffCaughtStealing(id, playNum, pos, css)
                            add_to_sql(pocs_sql, extranarrateflag, pending)
                        elif re.fullmatch(r"(SB([2-3H](\(T?UR\))?);)*SB([2-3H](\(T?UR\))?)", addplay):
                            secondstr = sb(id, row, modinfo, addplay, unusualplayflag, outdatedrelayflag, hitlocationflag)
                            sbs = [False, False, False]
                            for stolen_base in addplay.split(";"):
                                if stolen_base[2] == "H":
                                    secondadv[3] = 4
                                    sbs[2] = True
                                else:
                                    secondadv[int(stolen_base[2])-1] = int(stolen_base[2])
                                    sbs[int(stolen_base[2])-2] = True
                            sb_sql = StolenBase(id, playNum, sbs)
                            add_to_sql(sb_sql, extranarrateflag, pending)
                        elif addplay == "WP":
                            secondstr = wp(id, row, modinfo, unusualplayflag)
                            secondadv = auto_advance(runner_info, 0)
                            wp_sql = WildPitch(id, playNum)
                            add_to_sql(wp_sql, extranarrateflag, pending)
                        elif addplay == "PB":
                            secondstr = pb(id, row, modinfo, unusualplayflag)
                            secondadv = auto_advance(runner_info, 0)
                            pb_sql = PassedBall(id, playNum)
                            add_to_sql(pb_sql, extranarrateflag, pending)
                        elif addplay == "OA":
                            secondstr = oa(id, row, modinfo, unusualplayflag, outdatedrelayflag)
                            secondadv = auto_advance(runner_info, 0)
                            oa_sql = OutAdvancing(id, playNum)
                            add_to_sql(oa_sql, extranarrateflag, pending)
                        elif addplay == "DI":
                            secondstr = f"Runner advances on defensive indifference"
                            secondadv = auto_advance(runner_info, 0)
                            di_sql = DefensiveIndifference(id, playNum)
                            add_to_sql(di_sql, extranarrateflag, pending)
                        elif addplay in ["E2", "E1", "E3"]:
                            secondstr = field(id, row, modinfo, runner_info, unusualplayflag, outdatedrelayflag)
                            secondadv = auto_advance(runner_info, 0)
                            field_sql = FieldPlay(id, playNum, None)
                            add_to_sql(field_sql, extranarrateflag, pending)
                            
                        printstr = f"{firststr}. {secondstr}"
                        for i in range(len(expected_advinfo)):
                            if firstadv[i] == -1 or secondadv[i] == -1:
                                expected_advinfo[i] = -1
                            else:
                                expected_advinfo[i] = max(firstadv[i], secondadv[i])
                    elif(basicplay == 'HP'):
                        # Hit by pitch
                        printstr = hbp(id, row, modinfo, unusualplayflag)
                        expected_advinfo = push_up(runner_info)
                        basictype = "HP"
                        hbp_sql = HitByPitch(id, playNum)
                        add_to_sql(hbp_sql, extranarrateflag, pending)
                    elif basicplay == 'WP':
                        # Wild pitch
                        printstr = wp(id, row, modinfo, unusualplayflag)
                        expected_advinfo = auto_advance(runner_info, 0)
                        basictype = "WP"
                        wp_sql = WildPitch(id, playNum)
                        add_to_sql(wp_sql, extranarrateflag, pending)
                    elif(basicplay == 'PB'):
                        # Passed ball
                        printstr = pb(id, row, modinfo, unusualplayflag)
                        expected_advinfo = auto_advance(runner_info, 0)
                        basictype = "PB"
                        pb_sql = PassedBall(id, playNum)
                        add_to_sql(pb_sql, extranarrateflag, pending)
                    elif(basicplay == "BK"):
                        # Balk
                        printstr = bk(id, row, modinfo, unusualplayflag)
                        expected_advinfo = auto_advance(runner_info, 1, batter_pos=0)
                        basictype = "BK"
                        bk_sql = Balk(id, playNum)
                        add_to_sql(bk_sql, extranarrateflag, pending)
                    
                    ## Fielder-oriented events
                    elif re.fullmatch(r"([1-9]+\([B1-3]\))*[1-9E]*", basicplay):
                        # Field play
                        printstr, expected_advinfo, location, sac = field(id, row, modinfo, runner_info, unusualplayflag, outdatedrelayflag)
                        basictype = "FD"
                        fd_sql = FieldPlay(id, playNum, location)
                        add_to_sql(fd_sql, extranarrateflag, pending)
                        if sac:
                            sac_sql = Sacs(id, playNum)
                            add_to_sql(sac_sql, extranarrateflag, pending)
                    elif re.fullmatch(r"FLE[1-9]", basicplay):
                        # Dropped foul fly ball error
                        printstr, location = fle(id, row, modinfo, basicplay, unusualplayflag)
                        expected_advinfo = auto_advance(runner_info, 0)
                        basictype = "FE"
                        fle_sql = DroppedFoulError(id, playNum, basicplay[3], location)
                        add_to_sql(fle_sql, extranarrateflag, pending)
                    elif re.fullmatch(r"FC([1-9])?", basicplay):
                        # Fielder's choice
                        printstr, fielder, location, sac = fc(id, row, modinfo, basicplay, unusualplayflag, outdatedrelayflag)
                        expected_advinfo = auto_advance(runner_info, 0, batter_pos=1)
                        basictype = "FC"
                        fc_sql = FieldersChoice(id, playNum, fielder, location)
                        add_to_sql(fc_sql, extranarrateflag, pending)
                        if sac:
                            sac_sql = Sacs(id, playNum)
                            add_to_sql(sac_sql, extranarrateflag, pending)
                    
                    ## Baserunner-oriented events
                    elif(re.fullmatch(r"(SB([2-3H](\(T?UR\))?);)*SB([2-3H](\(T?UR\))?)", basicplay)):
                        # Stolen base
                        sbs = [False, False, False]
                        for stolen_base in basicplay.split(";"):
                            if stolen_base[2] == "H":
                                expected_advinfo[3] = 4
                                sbs[2] = True
                            else:
                                expected_advinfo[int(stolen_base[2])-1] = int(stolen_base[2])
                                sbs[int(stolen_base[2])-2] = True
                        printstr = sb(id, row, modinfo, basicplay, unusualplayflag, outdatedrelayflag, hitlocationflag)
                        basictype = "SB"
                        sb_sql = StolenBase(id, playNum, sbs)
                        add_to_sql(sb_sql, extranarrateflag, pending)
                    elif(re.fullmatch(r"((CS|POCS)[1-3H]\([1-9]+\);)*((PO|CS|POCS)[1-3H]\([1-9]*(E[1-9](\/TH)?)?\)(\(T?UR\))?)", basicplay)):
                        # PO/CS/POCS
                        printstr, expected_advinfo, pos, css = pocs(id, row, modinfo, basicplay, unusualplayflag, outdatedrelayflag, hitlocationflag)
                        basictype = "PC"
                        pocs_sql = PickOffCaughtStealing(id, playNum, pos, css)
                        add_to_sql(pocs_sql, extranarrateflag, pending)
                    elif basicplay == 'OA':
                        # Out advancing, runner advance should be explicitly given
                        printstr = oa(id, row, modinfo, unusualplayflag, outdatedrelayflag)
                        expected_advinfo = auto_advance(runner_info, 0)
                        basictype = "OA"
                        oa_sql = OutAdvancing(id, playNum)
                        add_to_sql(oa_sql, extranarrateflag, pending)
                    elif(basicplay == "DI"):
                        # Defensive indifference, generally only ever the one event followed by advance info
                        printstr = f'during {row[3]} at-bat, advance on defensive indifference'
                        if len(modinfo) > 1 and unusualplayflag:
                            debugprint("Unexpected defensive indifference modifier", id, row)
                        expected_advinfo = auto_advance(runner_info, 0)
                        basictype = "DI"
                        di_sql = DefensiveIndifference(id, playNum)
                        add_to_sql(di_sql, extranarrateflag, pending)
                    
                    ## Other
                    elif(basicplay == "C"):
                        # Interference, should always come with modifier(s)
                        printstr, fielder = inf(id, row, modinfo, unusualplayflag)
                        expected_advinfo = push_up(runner_info)
                        basictype = "CI"
                        int_sql = Interference(id, playNum, fielder)
                        add_to_sql(int_sql, extranarrateflag, pending)
                    elif(basicplay == 'NP'):
                        # No pitch
                        if not row[6] == 'NP' and unusualplayflag:
                            # A no-pitch should not be annotated
                            debugprint("No-pitch should not be annotated", id, row)
                    elif unusualplayflag:
                        # Catch-all
                        print(f"Unexpected play format: {basicplay} for game {id} play {row}")
                        continue

                    advstr = ""
                    # Adv info is as follows:
                    # -2 means runner info not given (for explicit advance info)
                    # -1 means batter/runner is out
                    # 0-3 means batter/runner is at home or on base 1-3
                    # 4 means batter/runner has scored
                    explicit_advinfo = [-2, -2, -2, -2]
                    if len(parts) > 1:
                        advstr, explicit_advinfo = parse_advinfo(id, row, parts[1].split(';'), unusualplayflag)
                        advstr = f": {advstr}"
                    
                    if (narrateflag or extranarrateflag) and not printstr == "":
                        print(f"{"B" if int(row[2]) > 0 else "T"}{row[1]}: {printstr}{advstr}")

                    deduced_advinfo = [0, 1, 2, 3]
                    for i in range(4):
                        deduced_advinfo[i] = int(expected_advinfo[i])
                        if not int(explicit_advinfo[i]) == -2:
                            deduced_advinfo[i] = int(explicit_advinfo[i])
                    
                    cleaned_advinfo = []
                    for i in range(len(deduced_advinfo)):
                        if deduced_advinfo[i] == -2:
                            cleaned_advinfo.append(i)
                        else:
                            cleaned_advinfo.append(deduced_advinfo[i])

                    if row[6] != "NP":
                        play_sql = Play(id, playNum, inn, half, outs, row[3], fielders[1-half][0], basictype, runner_info, cleaned_advinfo, runs)
                        add_to_sql(play_sql, extranarrateflag, pending)

                    for i in range(len(deduced_advinfo)):
                        if deduced_advinfo[i] == -1:
                            if extranarrateflag:
                                print(f"{i} is out.")
                            runner_info[i] = ""
                            outs += 1
                    for i in range(len(deduced_advinfo)-1,-1,-1):
                        if not deduced_advinfo[i] == i and deduced_advinfo[i] > -1:
                            if extranarrateflag:
                                print(f"{i} --> {deduced_advinfo[i]}")
                            if runner_info[i] == "":
                                print(f"{id}: {row}, {runner_info}, {deduced_advinfo}")
                                raise
                            elif deduced_advinfo[i] < 4 and runner_info[deduced_advinfo[i]] != "":
                                print(f"{id}: {row}, {runner_info}, {deduced_advinfo}")
                                raise
                            if deduced_advinfo[i] == -1:
                                runner_info[i] = ""
                            if deduced_advinfo[i] == 4:
                                runner_info[i] = ""
                                if outs < 3 or explicit_advinfo[i] == 4:
                                    runs[half] += 1
                            else:
                                runner_info[deduced_advinfo[i]] = runner_info[i]
                                runner_info[i] = ""
                    if extranarrateflag:
                        print(f"Runners on base: {runner_info[1:]}")
                if row[0] == "sub":
                    if int(row[5]) <= 9:
                        fielders[int(row[3])][int(row[5])-1] = row[1]
                if row[0] == "radj":
                    # Runner adjustment, generally used for ghost runners
                    radj_runner = (row[1], int(row[2]))
                    if narrateflag:
                        print(f"{row[1]} starts at base {row[2]}")
        for insert, rows in pending.items():
            cur.executemany(insert, rows)
        con.commit()
    con.close()