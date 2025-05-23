import pygame

class WaveManager:
    def __init__(self, wave_definitions, all_enemies, screen_width, ground_level, room_manager):
        self.wave_definitions = wave_definitions
        self.all_enemies = all_enemies
        self.current_wave = 1
        self.wave_in_progress = False
        self.screen_width = screen_width
        self.ground_level = ground_level
        self.room_manager = room_manager

    def start_next_wave(self):
        if self.current_wave <= len(self.wave_definitions):
            print(f"Iniciando Wave {self.current_wave}")
            wave = self.wave_definitions[self.current_wave - 1]
            for enemy_class, count in wave:
                for i in range(count):
                    # ✅ Spawn no canto direito alinhado ao chão
                    dummy = enemy_class((0, 0))  # para saber altura
                    spawn_x = self.screen_width - 100 - i * 60  # espaçamento
                    spawn_y = self.ground_level - dummy.rect.height
                    enemy = enemy_class((spawn_x, spawn_y))
                    enemy.facing_right = False  # todos virados pro player
                    self.all_enemies.add(enemy)
            self.wave_in_progress = True
        else:
            print("✅ Todas as waves concluídas!")
            self.room_manager.complete_waves()

    def update(self):
        if self.wave_in_progress and len(self.all_enemies) == 0:
            print(f"✅ Wave {self.current_wave} concluída!")
            self.current_wave += 1
            self.wave_in_progress = False
            if self.current_wave > len(self.wave_definitions):
                self.room_manager.complete_waves()
