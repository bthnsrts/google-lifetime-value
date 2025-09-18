import yaml
from pathlib import Path

def get_config():    
    repo_root = Path(__file__).resolve().parents[3]
    
    # Load the config file
    config_path = repo_root / 'config.yml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_active_companies():    
    config = get_config()
    return config['companies']['active']
    