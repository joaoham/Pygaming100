"""
Gerenciador de salas (**RoomManager**) do Hollow Mooni.

Responsabilidades principais
----------------------------
1. Carregar e escalar os fundos/foregrounds de cada sala.
2. Informar nível do chão, se o player pode se mover e se está colidindo
   com a “porta” de transição.
3. Avançar para a próxima sala quando requisitado.

Fluxo típico de uso (no main):
    room_manager = RoomManager(SCREEN_WIDTH, SCREEN_HEIGHT)
    ground_y = room_manager.get_ground_level()
    room_manager.draw_room(screen)
    room_manager.draw_foreground(screen)
"""

import pygame


class RoomManager:
    """
    Classe que define as salas (fases) do jogo.

    Parâmetros
    ----------
    screen_width : int
        Largura da janela do jogo (px).
    screen_height : int
        Altura da janela do jogo (px).
    """

    def __init__(self, screen_width, screen_height):
        # Cada dicionário é uma sala com suas propriedades
        self.rooms = [
            {
                "background": "assets/background/tela1true.png",
                "movement": True,
                "ground_level": 800,
            },
            {
                "background": "assets/background/background_passarela.png",
                "foreground": "assets/background/frente_passarela.png",
                "movement": False,  # travado até waves concluírem
                "waves_completed": False,
                "ground_level": 750,
            },
            {
                "background": "assets/background/boss_arena.png",
                "movement": True,
                "ground_level": 650,
            },
        ]

        self.current_room = 0
        self.screen_width = screen_width
        self.screen_height = screen_height

        # pré-carrega e escala todas as superfícies (bg/fg)
        for room in self.rooms:
            if "background" in room:
                img = pygame.image.load(room["background"]).convert()
                room["bg_surface"] = pygame.transform.scale(
                    img, (screen_width, screen_height)
                )
            if "foreground" in room:
                img = pygame.image.load(room["foreground"]).convert_alpha()
                room["fg_surface"] = pygame.transform.scale(
                    img, (screen_width, screen_height)
                )

        # “porta” imaginária no centro da tela (usada p/ colidir com o player)
        self.door_rect = pygame.Rect(
            screen_width // 2 - 50, screen_height // 2 + 50, 100, 200
        )

    # ------------------------------------------------------------------
    # trocas de sala e desenhar cenários
    # ------------------------------------------------------------------
    def next_room(self):
        """Avança para a próxima sala, se existir."""
        if self.current_room < len(self.rooms) - 1:
            self.current_room += 1

    def draw_room(self, surface):
        """Desenha o fundo da sala atual."""
        room = self.rooms[self.current_room]
        if "bg_surface" in room:
            surface.blit(room["bg_surface"], (0, 0))
        else:
            surface.fill(room.get("color", (0, 0, 0)))

    def draw_foreground(self, surface):
        """Desenha (se houver) o foreground da sala atual."""
        room = self.rooms[self.current_room]
        if "fg_surface" in room:
            surface.blit(room["fg_surface"], (0, 0))

    # ------------------------------------------------------------------
    # utilidades
    # ------------------------------------------------------------------
    def can_move(self):
        """
        Retorna `True` se o player pode se mover nesta sala
        (p.e., sala da passarela bloqueia antes das waves).
        """
        if self.current_room == 1 and not self.rooms[1]["waves_completed"]:
            return False
        return self.rooms[self.current_room]["movement"]

    def player_at_door(self, player):
        """Verifica se o player encostou na “porta” da sala."""
        return self.door_rect.colliderect(player.rect)

    def get_ground_level(self):
        """Y (px) onde o player deve parar de cair nesta sala."""
        return self.rooms[self.current_room].get("ground_level", 690)

    def complete_waves(self):
        """Marca waves como concluídas e libera movimento na sala 1."""
        if self.current_room == 1:
            self.rooms[1]["waves_completed"] = True
            self.rooms[1]["movement"] = True
