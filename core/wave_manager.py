from core.bringer import BringerOfDeathEnemy  # ✅ Importa o Bringer

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
                    spawn_x = self.screen_width - 150 - i * 100  # ✅ Mantém espaçamento

                    if issubclass(enemy_class, BringerOfDeathEnemy):
                        spawn_y = self.ground_level - 80  # ✅ Ajuste para o Bringer
                        enemy = enemy_class((spawn_x, spawn_y), scale=1.0)
                    else:
                        # ✅ Correção para NightBorneEnemy
                        if enemy_class.__name__ == "NightBorneEnemy":
                            spawn_y = 660  # ✅ Ajuste para alinhar o NightBorne
                            sprite_sheet_path = "assets/enemies/nightborne/NightBorne.png" 
                            enemy = enemy_class((spawn_x, spawn_y), sprite_sheet_path)
                        else:
                            spawn_y = 560  # ✅ Padrão pros esqueletos
                            enemy = enemy_class((spawn_x, spawn_y))

                    enemy.facing_right = False
                    enemy.recently_hit = False
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
