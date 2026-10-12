import argparse
import logging
from pathlib import Path
from parse_sql.parsepbp import db_by_year

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Convert Retrosheet-style data downloads into SQL tables.")
    parser.add_argument("--folder", default="alldata", help="Folder where the data download is located. The default name used by Retrosheet is 'alldata'.")
    parser.add_argument("--gametype", help="Specific game type to parse, as a subfolder of alldata")
    parser.add_argument("--year", type=int, help="Specific year to parse. Supersedes start and end range specifications.")
    parser.add_argument("--start", type=int, help="Start of a specific inclusive range of years to parse.")
    parser.add_argument("--end", type=int, help="End of a specific inclusive range of years to parse.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    ROOT = Path(__file__).resolve().parent
    DATAPATH = ROOT / args.folder

    if not (DATAPATH.exists() and DATAPATH.is_dir()):
        parser.error(f"Was not able to locate a root data folder at {DATAPATH}")

    search_folders = []
    if args.gametype:
        GAMETYPE_PATH = DATAPATH / args.gametype
        if not (GAMETYPE_PATH.exists() and GAMETYPE_PATH.is_dir()):
            parser.error(f"Was not able to locate a game type folder at {GAMETYPE_PATH}")
        search_folders.append(args.gametype)
    else:
        for default_folder in ["events", "ngl_e", "postseason", "allstar"]:
            DEFAULT_PATH = DATAPATH / default_folder
            if DEFAULT_PATH.exists() and DEFAULT_PATH.is_dir():
                search_folders.append(default_folder)
            else:
                logger.info("Default folder %s not found", default_folder)

    start_year = 1900
    end_year = 2025
    if args.start:
        start_year = args.start
    if args.end:
        end_year = args.end
    if args.year:
        start_year = args.year
        end_year = args.year
    for search_folder in search_folders:
        for year in range(start_year, end_year+1):
            db_by_year(ROOT, args.folder, search_folder, year)

if __name__ == "__main__":
    main()