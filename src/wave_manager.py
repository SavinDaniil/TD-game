from src.enemy import Enemy


class WaveManager:
    def __init__(self, game_map):
        self.game_map = game_map
        self.max_wave = 5
        self.current_wave = 0
        self.enemies_to_spawn = 0
        self.spawn_timer = 0
        self.wave_active = False

    def start_wave(self):
        if self.wave_active or self.current_wave >= self.max_wave:
            return False
        self.current_wave += 1
        self.enemies_to_spawn = 6 + self.current_wave * 2
        self.spawn_timer = 0
        self.wave_active = True
        return True

    def update(self, dt, enemies):
        if not self.wave_active:
            return
        self.spawn_timer -= dt
        if self.enemies_to_spawn > 0 and self.spawn_timer <= 0:
            enemies.append(Enemy(self.game_map.path_points, self.current_wave))
            self.enemies_to_spawn -= 1
            self.spawn_timer = 0.7
        if self.enemies_to_spawn == 0 and not any(enemy.alive for enemy in enemies):
            self.wave_active = False

    def is_finished(self, enemies):
        return (
            self.current_wave >= self.max_wave
            and not self.wave_active
            and self.enemies_to_spawn == 0
            and not any(enemy.alive for enemy in enemies)
        )
