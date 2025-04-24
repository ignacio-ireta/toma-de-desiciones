INPUT_FILE = "matches_data.json"
PLAYERS_OUTPUT = "players_data.parquet"
MATCHES_OUTPUT = "matches_data.parquet"

# Collector configuration
API_KEY = "RGAPI-XXXXX-XXXX-XXXX-XXXX-XXXXXXX"  # Replace with your actual API key
THRESHOLD = 1
PAUSE_BETW = 0.25
CHECKPOINT_FREQ = 25
MAX_RETRIES = 5
BASE_TIMEOUT = 10

# File paths for collector
PLAYERS_FILE = "players_puuids.json"
GAMES_FILE = "latest_games.json"
TIMELINE_FILE = "matches_timeline.json"
FAILED_MATCHES_FILE = "failed_matches.json"

# API configuration
QUEUES = ['RANKED_SOLO_5x5']
TIERS = ['MASTER', 'GRANDMASTER', 'CHALLENGER']
DIVISIONS = ['I', 'II', 'III', 'IV']

UNWANTED_STATS = [
    'PlayerScore0', 'PlayerScore1', 'PlayerScore10', 'PlayerScore11', 'PlayerScore2', 
    'PlayerScore3', 'PlayerScore4', 'PlayerScore5', 'PlayerScore6', 'PlayerScore7', 
    'PlayerScore8', 'PlayerScore9', 'challenges', 'missions', 'playerAugment1', 
    'playerAugment2', 'playerAugment3', 'playerAugment4', 'playerAugment5', 
    'playerAugment6', 'perks'
]

MATCHES_COLUMNS = [
    'gameId', 'teamId', 'win', 'gameDuration', 'ban1', 'ban2', 'ban3', 'ban4', 'ban5', 
    'atakhanFirst', 'atakhanKills', 'baronFirst', 'baronKills', 'championFirst', 
    'championKills', 'dragonFirst', 'dragonKills', 'hordeFirst', 'hordeKills', 
    'inhibitorFirst', 'inhibitorKills', 'riftHeraldFirst', 'riftHeraldKills', 
    'towerFirst', 'towerKills'
]

PLAYERS_COLUMNS = [
    'gameId', 'allInPings', 'assistMePings', 'assists', 'baronKills', 'basicPings',
    'bountyLevel', 'champExperience', 'champLevel', 'championId', 'championName',
    'championTransform', 'commandPings', 'consumablesPurchased', 
    'damageDealtToBuildings', 'damageDealtToObjectives', 'damageDealtToTurrets',
    'damageSelfMitigated', 'dangerPings', 'deaths', 'detectorWardsPlaced', 
    'doubleKills', 'dragonKills', 'eligibleForProgression', 'enemyMissingPings',
    'enemyVisionPings', 'firstBloodAssist', 'firstBloodKill', 'firstTowerAssist',
    'firstTowerKill', 'gameEndedInEarlySurrender', 'gameEndedInSurrender',
    'getBackPings', 'goldEarned', 'goldSpent', 'holdPings', 'individualPosition',
    'inhibitorKills', 'inhibitorTakedowns', 'inhibitorsLost', 'item0', 'item1', 
    'item2', 'item3', 'item4', 'item5', 'item6', 'itemsPurchased', 'killingSprees',
    'kills', 'lane', 'largestCriticalStrike', 'largestKillingSpree',
    'largestMultiKill', 'longestTimeSpentLiving', 'magicDamageDealt',
    'magicDamageDealtToChampions', 'magicDamageTaken', 'needVisionPings',
    'neutralMinionsKilled', 'nexusKills', 'nexusLost', 'nexusTakedowns',
    'objectivesStolen', 'objectivesStolenAssists', 'onMyWayPings', 'participantId',
    'pentaKills', 'physicalDamageDealt', 'physicalDamageDealtToChampions', 
    'physicalDamageTaken', 'placement', 'playerSubteamId', 'profileIcon',
    'pushPings', 'puuid', 'quadraKills', 'retreatPings', 'riotIdGameName',
    'riotIdTagline', 'role', 'sightWardsBoughtInGame', 'spell1Casts', 'spell2Casts',
    'spell3Casts', 'spell4Casts', 'subteamPlacement', 'summoner1Casts',
    'summoner1Id', 'summoner2Casts', 'summoner2Id', 'summonerId', 'summonerLevel',
    'summonerName', 'teamEarlySurrendered', 'teamId', 'teamPosition',
    'timeCCingOthers', 'timePlayed', 'totalAllyJungleMinionsKilled',
    'totalDamageDealt', 'totalDamageDealtToChampions',
    'totalDamageShieldedOnTeammates', 'totalDamageTaken',
    'totalEnemyJungleMinionsKilled', 'totalHeal', 'totalHealsOnTeammates',
    'totalMinionsKilled', 'totalTimeCCDealt', 'totalTimeSpentDead',
    'totalUnitsHealed', 'tripleKills', 'trueDamageDealt',
    'trueDamageDealtToChampions', 'trueDamageTaken', 'turretKills', 'turretTakedowns', 
    'turretsLost', 'unrealKills', 'visionClearedPings', 'visionScore', 
    'visionWardsBoughtInGame', 'wardsKilled', 'wardsPlaced', 'win'
]

BATCH_SIZE = 100
LARGE_FILE_THRESHOLD = 100 * 1024 * 1024
CHUNK_SIZE = 10000

