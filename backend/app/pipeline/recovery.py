# minimal recovery utilities (placeholder for restart logic)
# For now a simple function to read state and determine resume point

from pipeline.state_manager import StateManager

def get_last_successful_stage(state_path: str):
    sm = StateManager(state_path)
    s = sm.read_state()
    return s.get("current_stage"), s.get("artifacts", {})
