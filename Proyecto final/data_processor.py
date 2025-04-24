import json
import pandas as pd
import os
import sys
from typing import Dict, List, Any, Tuple, Optional

from config import (
    INPUT_FILE, PLAYERS_OUTPUT, MATCHES_OUTPUT,
    UNWANTED_STATS, MATCHES_COLUMNS, PLAYERS_COLUMNS
)


class DataLoader:
    
    @staticmethod
    def load_match_data(file_path: str) -> List[Dict]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist")
        
        with open(file_path) as f:
            matches_data = json.load(f)
        
        if not isinstance(matches_data, list):
            raise ValueError(f"Expected matches_data to be a list, got {type(matches_data)}")
        
        if len(matches_data) == 0:
            print("Warning: No matches found in the data file")
            
        print(f"Successfully loaded {len(matches_data)} matches")
        return matches_data


class MatchProcessor:
    
    def __init__(self):
        self.processed_games = 0
        self.skipped_games = 0
    
    def extract_team_data(self, game_id: int, team: Dict, game_duration: int) -> Optional[List]:
        if 'teamId' not in team:
            print(f"Warning: Team in game {game_id} missing 'teamId' - skipping")
            return None
            
        team_id = team['teamId']
        
        if 'bans' not in team or not isinstance(team['bans'], list):
            print(f"Warning: Team {team_id} in game {game_id} has invalid 'bans' data")
            bans = [None] * 5
        else:
            bans = []
            for ban in team['bans']:
                if isinstance(ban, dict) and 'championId' in ban:
                    bans.append(ban['championId'])
                else:
                    bans.append(None)
            
            bans = (bans + [None] * 5)[:5]
        
        objectives = []
        if 'objectives' not in team or not isinstance(team['objectives'], dict):
            print(f"Warning: Team {team_id} in game {game_id} has invalid 'objectives' data")
            objectives = [False, 0] * 7
        else:
            try:
                for objective in team['objectives']:
                    obj_data = team['objectives'][objective]
                    first = obj_data.get('first', False)
                    kills = obj_data.get('kills', 0)
                    objectives.extend([first, kills])
            except Exception as e:
                print(f"Error processing objectives for team {team_id} in game {game_id}: {e}")
                objectives = [False, 0] * 7
        
        return [game_id, team_id, game_duration] + bans + objectives
    
    def extract_player_data(self, game_id: int, player: Dict) -> List:
        player_data = [game_id]
        
        for key, value in player.items():
            if key not in UNWANTED_STATS:
                player_data.append(value)
                
        return player_data
    
    def process_matches(self, matches_data: List[Dict]) -> Tuple[List[List], List[List]]:
        aggregated_matches_data = []
        aggregated_players_data = []
        
        self.processed_games = 0
        self.skipped_games = 0
        
        for game_index, game in enumerate(matches_data):
            try:
                if 'info' not in game:
                    print(f"Warning: Game at index {game_index} missing 'info' key - skipping")
                    self.skipped_games += 1
                    continue
                    
                game_info = game['info']
                
                if 'gameId' not in game_info:
                    print(f"Warning: Game at index {game_index} missing 'gameId' - skipping")
                    self.skipped_games += 1
                    continue
                    
                if 'gameDuration' not in game_info:
                    print(f"Warning: Game ID {game_info.get('gameId', 'unknown')} missing 'gameDuration' - skipping")
                    self.skipped_games += 1
                    continue
                
                game_id = game_info['gameId']
                game_duration = game_info['gameDuration']
                
                match_data = []
                if 'teams' in game_info and isinstance(game_info['teams'], list):
                    for team in game_info['teams']:
                        team_data = self.extract_team_data(game_id, team, game_duration)
                        if team_data:
                            match_data.append(team_data)
                else:
                    print(f"Warning: Game ID {game_id} has invalid 'teams' data - skipping teams processing")
                
                players_data = []
                if 'participants' in game_info and isinstance(game_info['participants'], list):
                    for player in game_info['participants']:
                        try:
                            player_data = self.extract_player_data(game_id, player)
                            players_data.append(player_data)
                        except Exception as e:
                            print(f"Error processing player in game {game_id}: {e}")
                else:
                    print(f"Warning: Game ID {game_id} has invalid 'participants' data - skipping players processing")
                
                aggregated_matches_data.extend(match_data)
                aggregated_players_data.extend(players_data)
                
                self.processed_games += 1
                
            except Exception as e:
                print(f"Error processing game at index {game_index}: {e}")
                self.skipped_games += 1
        
        print(f"Processed {self.processed_games} games successfully, skipped {self.skipped_games} games")
        return aggregated_matches_data, aggregated_players_data


class DataWriter:
    
    @staticmethod
    def save_dataframe(data: List[List], columns: List[str], output_file: str) -> None:
        try:
            if not data:
                print(f"Warning: No data to save to {output_file}")
                df = pd.DataFrame(columns=columns)
            else:
                df = pd.DataFrame(data, columns=columns)
            
            df.to_parquet(output_file)
            print(f"Successfully saved {len(df)} records to {output_file}")
        except Exception as e:
            print(f"Error saving data to {output_file}: {e}")


def main():
    try:
        loader = DataLoader()
        matches_data = loader.load_match_data(INPUT_FILE)
        
        processor = MatchProcessor()
        match_data, player_data = processor.process_matches(matches_data)
        
        writer = DataWriter()
        writer.save_dataframe(match_data, MATCHES_COLUMNS, MATCHES_OUTPUT)
        writer.save_dataframe(player_data, PLAYERS_COLUMNS, PLAYERS_OUTPUT)
        
        print("Processing completed successfully!")
        
    except Exception as e:
        print(f"Processing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()