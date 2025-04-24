import logging
import json
import requests
import time
import os
import random
from requests import Session, HTTPError, ConnectionError, Timeout, TooManyRedirects
from urllib3.exceptions import ProtocolError, ReadTimeoutError
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("riot_api.log"),
        logging.StreamHandler()
    ]
)

queues     = ['RANKED_SOLO_5x5']
tiers      = ['MASTER', 'GRANDMASTER', 'CHALLENGER']
divisions  = ['I', 'II', 'III', 'IV']
API_KEY    = "RGAPI-XXXXX-XXXX-XXXX-XXXX-XXXXXXX"
THRESHOLD  = 1
PAUSE_BETW = 0.25
CHECKPOINT_FREQ = 25
MAX_RETRIES = 5
BASE_TIMEOUT = 10

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
players_file   = os.path.join(BASE_DIR, "players_puuids.json")
games_file     = os.path.join(BASE_DIR, "latest_games.json")
timeline_file  = os.path.join(BASE_DIR, "matches_timeline.json")
failed_matches_file = os.path.join(BASE_DIR, "failed_matches.json")

adapter = requests.adapters.HTTPAdapter(
    max_retries=0,
    pool_connections=10,
    pool_maxsize=20
)

session = Session()
session.mount('https://', adapter)
session.headers.update({
    "X-Riot-Token": API_KEY,
    "User-Agent": "MyLoLTool/1.0 (https://github.com/you/mytool; you@example.com)",
    "Accept-Encoding": "gzip",
})

def parse_header_pairs(header_val: str):
    pairs = []
    if not header_val:
        return pairs
    for chunk in header_val.split(","):
        limit, window = map(int, chunk.split(":"))
        pairs.append((limit, window))
    return pairs

def exponential_backoff(attempt, base=1, max_backoff=60):
    delay = min(max_backoff, base * (2 ** attempt))
    jitter = random.uniform(0, 0.1 * delay)
    return delay + jitter

def fetch_respecting_headers(url, params=None, max_retries=MAX_RETRIES):
    for attempt in range(max_retries):
        try:
            timeout = BASE_TIMEOUT * (1 + attempt * 0.5)
            
            resp = session.get(url, params=params, timeout=timeout)
            
            if resp.status_code == 429:
                app_limits = parse_header_pairs(resp.headers.get("X-App-Rate-Limit", ""))
                app_counts = parse_header_pairs(resp.headers.get("X-App-Rate-Limit-Count", ""))
                
                if "Retry-After" in resp.headers:
                    wait = int(resp.headers["Retry-After"])
                else:
                    violated = [w for (L, w), (c, _) in zip(app_limits, app_counts) if c >= L]
                    wait = max(violated) if violated else 1
                
                logging.warning(f"[429] Rate limited. Sleeping {wait}s (attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
                continue
                
            elif 500 <= resp.status_code < 600:
                wait = exponential_backoff(attempt)
                logging.warning(f"[{resp.status_code}] Server error for URL: {url}. Retrying in {wait:.2f}s (attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
                continue
            
            resp.raise_for_status()
            return resp
            
        except (ConnectionError, ProtocolError, ReadTimeoutError) as e:
            wait = exponential_backoff(attempt)
            logging.warning(f"Connection error ({type(e).__name__}) for URL: {url}. Retrying in {wait:.2f}s (attempt {attempt+1}/{max_retries})")
            time.sleep(wait)
            
        except Timeout as e:
            wait = exponential_backoff(attempt, base=2)
            logging.warning(f"Timeout ({type(e).__name__}) for URL: {url}. Retrying in {wait:.2f}s (attempt {attempt+1}/{max_retries})")
            time.sleep(wait)
            
        except HTTPError as e:
            logging.error(f"HTTP error {getattr(e.response, 'status_code', 'unknown')} for URL: {url}")
            return None
            
        except Exception as e:
            logging.error(f"Unexpected error ({type(e).__name__}: {str(e)}) for URL: {url}")
            if attempt == max_retries - 1:
                return None
            
            wait = exponential_backoff(attempt, base=3)
            time.sleep(wait)
    
    logging.error(f"Max retries exceeded for URL: {url}")
    return None

def load_or_create_file(file_path, default=None):
    if default is None:
        default = []
    
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump(default, f)
        return default
    
    try:
        with open(file_path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.warning(f"Couldn't parse JSON from {file_path}, creating new file")
        return default

def save_checkpoint(file_path, data):
    try:
        temp_path = file_path + ".tmp"
        with open(temp_path, "w") as f:
            json.dump(data, f)
        
        os.replace(temp_path, file_path)
        return True
    except Exception as e:
        logging.error(f"Failed to save checkpoint to {file_path}: {str(e)}")
        return False

players_puuids = load_or_create_file(players_file)
failed_matches = load_or_create_file(failed_matches_file)
combos = [(q, t, d) for q in queues for t in tiers for d in divisions]

try:
    with tqdm(combos, desc="Fetching league entries", unit="req", 
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
        for i, (queue, tier, division) in enumerate(pbar):
            pbar.set_description(f"Fetching {tier} {division}")
            url = f"https://kr.api.riotgames.com/lol/league-exp/v4/entries/{queue}/{tier}/{division}"
            resp = fetch_respecting_headers(url, params={"page": 1})
            if not resp:
                logging.warning(f"Failed to fetch {tier} {division}, continuing to next")
                continue
                
            try:
                entries = resp.json()
                for p in entries:
                    if "puuid" in p and p["puuid"] not in players_puuids:
                        players_puuids.append(p["puuid"])
            except (ValueError, KeyError) as e:
                logging.error(f"Error parsing response: {str(e)}")
                
            pbar.set_postfix(players=len(players_puuids))
            
            if (i + 1) % CHECKPOINT_FREQ == 0 or i == len(combos) - 1:
                save_checkpoint(players_file, players_puuids)
                    
            time.sleep(PAUSE_BETW)
except KeyboardInterrupt:
    logging.info("Process interrupted by user during player fetching")
    save_checkpoint(players_file, players_puuids)
    raise

latest_games = load_or_create_file(games_file)
stored_puuids = load_or_create_file(players_file)

try:
    with tqdm(stored_puuids, desc="Fetching match IDs", unit="player", 
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
        for i, puuid in enumerate(pbar):
            url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
            resp = fetch_respecting_headers(url, params={"queue": 420, "type": "ranked", "start": 0, "count": 20})
            if not resp:
                continue
                
            try:
                new_matches = [m for m in resp.json() if m not in latest_games]
                latest_games.extend(new_matches)
            except (ValueError, KeyError) as e:
                logging.error(f"Error parsing matches for puuid {puuid}: {str(e)}")
                continue
            
            pbar.set_postfix(total_matches=len(latest_games), new_matches=len(new_matches))
            
            if (i + 1) % CHECKPOINT_FREQ == 0 or i == len(stored_puuids) - 1:
                save_checkpoint(games_file, latest_games)
                    
            time.sleep(PAUSE_BETW)
except KeyboardInterrupt:
    logging.info("Process interrupted by user during match ID fetching")
    save_checkpoint(games_file, latest_games)
    raise

matches_info = load_or_create_file(timeline_file)
stored_games = load_or_create_file(games_file)

processed_matches = {m.get("metadata", {}).get("matchId") for m in matches_info if "metadata" in m}
unprocessed_games = [match_id for match_id in stored_games if match_id not in processed_matches and match_id not in failed_matches]

try:
    with tqdm(unprocessed_games, desc="Fetching match data", unit="match",
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
        for i, match_id in enumerate(pbar):
            pbar.set_description(f"Match {match_id}")
            url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}"
            resp = fetch_respecting_headers(url)
            
            if not resp:
                logging.warning(f"Failed to fetch match {match_id}, adding to failed matches list")
                failed_matches.append(match_id)
                save_checkpoint(failed_matches_file, failed_matches)
                continue
                
            try:
                match_data = resp.json()
                matches_info.append(match_data)
            except (ValueError, KeyError) as e:
                logging.error(f"Error parsing match data for {match_id}: {str(e)}")
                failed_matches.append(match_id)
                save_checkpoint(failed_matches_file, failed_matches)
                continue
            
            approx_size_mb = sum(len(json.dumps(m)) for m in matches_info) / (1024 * 1024)
            pbar.set_postfix(matches=len(matches_info), failed=len(failed_matches), size_mb=f"{approx_size_mb:.1f}MB")
            
            if (i + 1) % CHECKPOINT_FREQ == 0 or i == len(unprocessed_games) - 1:
                save_checkpoint(timeline_file, matches_info)
                    
            time.sleep(PAUSE_BETW)
except KeyboardInterrupt:
    logging.info("Process interrupted by user during match data fetching")
    save_checkpoint(timeline_file, matches_info)
    save_checkpoint(failed_matches_file, failed_matches)
    print("Process interrupted. Progress has been saved.")