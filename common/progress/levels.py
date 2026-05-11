"""Clase que gestiona la lógica para subir de nivel los personajes"""

XP_REWARDS = {
    1: 50,   # Fácil
    2: 100,  # Intermedio
    3: 200,  # Avanzado
    4: 400,  # Épico
}

def get_xp_reward(difficulty: int) -> int:
    return XP_REWARDS.get(difficulty, 0)

def xp_required_for_level(level: int) -> int:
    return 100 + ((level - 1) * 50)

def did_level_up(old_xp: int, new_xp: int) -> bool:
    return calculate_level(new_xp) > calculate_level(old_xp)

def calculate_level(total_xp: int) -> int:
    level = 1
    remaining_xp = total_xp

    while remaining_xp >= xp_required_for_level(level):
        remaining_xp -= xp_required_for_level(level)
        level += 1

    return level

def xp_progress(total_xp: int) -> tuple[int, int, int]:
    level = 1
    remaining_xp = total_xp

    while remaining_xp >= xp_required_for_level(level):
        remaining_xp -= xp_required_for_level(level)
        level += 1

    required = xp_required_for_level(level)
    return level, remaining_xp, required