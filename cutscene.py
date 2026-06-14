import pygame
import os
import sys

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets", "images")
FONT_DIR  = os.path.join(os.path.dirname(__file__), "assets", "fonts")

BLACK  = (  0,   0,   0)
WHITE  = (255, 255, 255)
YELLOW = (255, 216,   0)
RED    = (220,  50,  50)

PANELS = [
    ("cut_p1.png", "Isang araw sa Senado ng Pilipinas..."),
    ("cut_p2.png", "Nag-aaway na naman ang mga senador..."),
    ("cut_p3.png", "Si Bato ay tumayo para magsalita..."),
    ("cut_p4.png", "Habang siya ay nag sasalita..."),
    ("cut_p5.png", "Bigla siyang NAHULOG...!"),
    ("cut_p6.png", "Sa isang PORTAL...!"),
    ("cut_p7.png", "Napunta siya sa lugar na hindi niya alam..."),
    ("cut_p8.png", "Kaya ngayon... kailangan niyang tumakbo."),
]


class CutsceneScreen:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock  = clock
        self.SW, self.SH = screen.get_size()

        fs = self.SH / 1080
        font_path     = os.path.join(FONT_DIR, "PressStart2P.ttf")
        self.f_text   = pygame.font.Font(font_path, int(16 * fs))
        self.f_hint   = pygame.font.Font(font_path, int( 9 * fs))
        self.f_title  = pygame.font.Font(font_path, int(48 * fs))

        self.scanlines = self._make_scanlines()

        # Load and scale all panel images
        panel_w = int(self.SW * 0.72)
        panel_h = int(self.SH * 0.62)
        self.panels = []
        for img_name, text in PANELS:
            path = os.path.join(ASSET_DIR, img_name)
            img  = pygame.image.load(path).convert()
            img  = pygame.transform.scale(img, (panel_w, panel_h))
            self.panels.append((img, text))

        self.panel_w = panel_w
        self.panel_h = panel_h
        self.panel_x = (self.SW - panel_w) // 2
        self.panel_y = int(self.SH * 0.06)

        # text box
        self.box_h   = int(self.SH * 0.18)
        self.box_y   = self.panel_y + panel_h + int(self.SH * 0.02)
        self.skip_requested = False

    # ── helpers ───────────────────────────────────────────────────────────
    def _make_scanlines(self):
        surf = pygame.Surface((self.SW, self.SH), pygame.SRCALPHA)
        for y in range(0, self.SH, 2):
            pygame.draw.line(surf, (0, 0, 0, 50), (0, y), (self.SW, y))
        return surf

    def _outline(self, font, text, color, cx, cy, d=2):
        for ox in range(-d, d+1):
            for oy in range(-d, d+1):
                if ox == 0 and oy == 0:
                    continue
                s = font.render(text, False, BLACK)
                self.screen.blit(s, s.get_rect(center=(cx+ox, cy+oy)))
        s = font.render(text, False, color)
        self.screen.blit(s, s.get_rect(center=(cx, cy)))

    def _handle_cutscene_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.skip_requested = True
            return True
        return False

    def _fade(self, direction, duration=400):
        """direction: 'in' = black→scene, 'out' = scene→black"""
        overlay = pygame.Surface((self.SW, self.SH))
        overlay.fill(BLACK)
        steps  = 30
        delay  = duration // steps
        for i in range(steps + 1):
            for event in pygame.event.get():
                if self._handle_cutscene_event(event):
                    return False
            alpha = int(255 * (1 - i/steps)) if direction == 'in' else int(255 * i/steps)
            overlay.set_alpha(alpha)
            self.screen.blit(overlay, (0, 0))
            pygame.display.flip()
            pygame.time.delay(delay)
        return True

    # ── word by word text reveal ──────────────────────────────────────────
    def _reveal_text(self, text, panel_idx):
        """Reveal text word by word with flash, return False if player skipped."""
        words      = text.split()
        revealed   = []
        flash_word = None
        flash_timer= 0
        word_delay = 120   # ms between words
        last_word_time = pygame.time.get_ticks()

        word_idx = 0

        while True:
            now = pygame.time.get_ticks()

            # advance word
            if word_idx < len(words) and now - last_word_time >= word_delay:
                flash_word  = words[word_idx]
                flash_timer = 10
                revealed.append(words[word_idx])
                word_idx       += 1
                last_word_time  = now

            for event in pygame.event.get():
                if self._handle_cutscene_event(event):
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if word_idx < len(words):
                            # skip to end of text
                            revealed = words[:]
                            word_idx = len(words)
                            flash_word = None
                        else:
                            return True   # advance panel

            # Draw
            self._draw_base(panel_idx, revealed, flash_word, flash_timer)
            if flash_timer > 0:
                flash_timer -= 1
                if flash_timer == 0:
                    flash_word = None

            # show "SPACE" hint only when all words revealed
            if word_idx >= len(words):
                hint = self.f_hint.render(
                    "[ SPACE ] next    [ ENTER ] skip", False, (80, 80, 80)
                )
                self.screen.blit(hint, hint.get_rect(
                    bottomright=(self.panel_x + self.panel_w - 10,
                                 self.box_y + self.box_h - 8)
                ))

            self.screen.blit(self.scanlines, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)

    def _draw_base(self, panel_idx, revealed_words, flash_word, flash_timer):
        self.screen.fill((10, 8, 18))

        # panel image
        img, _ = self.panels[panel_idx]
        # border glow
        border_color = RED if panel_idx == 3 else YELLOW
        pygame.draw.rect(self.screen, border_color,
                         (self.panel_x - 3, self.panel_y - 3,
                          self.panel_w + 6, self.panel_h + 6), 3)
        self.screen.blit(img, (self.panel_x, self.panel_y))

        # panel counter dots
        dot_y = self.panel_y + self.panel_h + 8
        total = len(self.panels)
        dot_spacing = 18
        start_x = self.SW // 2 - (total * dot_spacing) // 2
        for i in range(total):
            col = YELLOW if i == panel_idx else (50, 50, 60)
            pygame.draw.circle(self.screen, col,
                               (start_x + i * dot_spacing, dot_y), 5)

        # text box
        box_surf = pygame.Surface((self.panel_w, self.box_h), pygame.SRCALPHA)
        box_surf.fill((0, 0, 0, 200))
        self.screen.blit(box_surf, (self.panel_x, self.box_y))
        pygame.draw.rect(self.screen, border_color,
                         (self.panel_x, self.box_y,
                          self.panel_w, self.box_h), 2)

        # revealed text word by word, wrap if needed
        if revealed_words:
            line      = ""
            lines     = []
            max_w     = self.panel_w - 40
            for word in revealed_words:
                test = (line + " " + word).strip()
                if self.f_text.size(test)[0] <= max_w:
                    line = test
                else:
                    if line:
                        lines.append(line)
                    line = word
            if line:
                lines.append(line)

            total_h  = len(lines) * int(self.SH * 0.035)
            start_ty = self.box_y + (self.box_h - total_h) // 2

            for li, ln in enumerate(lines):
                ty = start_ty + li * int(self.SH * 0.035)
                words_in_line = ln.split()
            
            if flash_word and flash_timer > 0 and words_in_line and words_in_line[-1] == flash_word:
                # measure full line width so we can center it
                full_line_surf = self.f_text.render(ln, False, WHITE)
                full_w         = full_line_surf.get_width()
                x              = self.SW // 2 - full_w // 2

                # draw all words except last in white
                base = " ".join(words_in_line[:-1])
                if base:
                    base_surf = self.f_text.render(base + " ", False, WHITE)
                    # outline
                    for ox in [-1, 0, 1]:
                        for oy in [-1, 0, 1]:
                            if ox == 0 and oy == 0:
                                continue
                            s = self.f_text.render(base + " ", False, BLACK)
                            self.screen.blit(s, (x + ox, ty - base_surf.get_height()//2 + oy))
                    self.screen.blit(base_surf, (x, ty - base_surf.get_height()//2))
                    x += base_surf.get_width()
                
                # flash word
                flash_col  = WHITE if flash_timer > 5 else YELLOW
                flash_surf = self.f_text.render(flash_word, False, flash_col)
                for ox in [-2, -1, 0, 1, 2]:
                    for oy in [-2, -1, 0, 1, 2]:
                        if ox == 0 and oy == 0:
                            continue
                        s = self.f_text.render(flash_word, False, BLACK)
                        self.screen.blit(s, (x + ox, ty - flash_surf.get_height()//2 + oy))
                self.screen.blit(flash_surf, (x, ty - flash_surf.get_height()//2))
            else:
                self._outline(self.f_text, ln, WHITE, self.SW // 2, ty, d=1)

    # ── title reveal ──────────────────────────────────────────────────────
    def _title_reveal(self):
        """Word by word title: RUN, BATO! RUN! then flash and hold."""
        words      = ["RUN,", "BATO!", "RUN!"]
        colors     = [WHITE, YELLOW, RED]
        revealed   = 0
        flash_on   = False
        flash_count= 0
        word_times = [0, 800, 1600]   # ms after start each word appears
        start      = pygame.time.get_ticks()
        hold_start = None
        holding    = False

        while True:
            now = pygame.time.get_ticks()
            elapsed = now - start

            # reveal words on schedule
            new_rev = sum(1 for t in word_times if elapsed >= t)
            if new_rev > revealed:
                revealed   = new_rev
                flash_on   = True
                flash_count= 12

            # once all revealed, hold for 2s then return
            if revealed == len(words):
                if hold_start is None:
                    hold_start = now
                if now - hold_start > 2000:
                    return True

            for event in pygame.event.get():
                if self._handle_cutscene_event(event):
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return True

            # Draw
            self.screen.fill(BLACK)

            # flash overlay
            if flash_on and flash_count > 0:
                alpha = int(200 * flash_count / 12)
                fl = pygame.Surface((self.SW, self.SH))
                fl.fill(WHITE)
                fl.set_alpha(alpha)
                self.screen.blit(fl, (0, 0))
                flash_count -= 1
                if flash_count == 0:
                    flash_on = False

            # draw words
            fs     = self.SH / 1080
            total_w = sum(self.f_title.size(w)[0] for w in words[:revealed])
            total_w += int(20 * fs) * max(0, revealed - 1)
            x       = self.SW // 2 - total_w // 2
            cy      = self.SH // 2

            for i in range(revealed):
                w   = words[i]
                col = colors[i]
                surf = self.f_title.render(w, False, col)
                # outline
                for ox, oy in [(-3,0),(3,0),(0,-3),(0,3)]:
                    s2 = self.f_title.render(w, False, BLACK)
                    self.screen.blit(s2, (x + ox, cy - surf.get_height()//2 + oy))
                self.screen.blit(surf, (x, cy - surf.get_height()//2))
                x += surf.get_width() + int(20 * fs)

            self.screen.blit(self.scanlines, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)

    # ── main run ──────────────────────────────────────────────────────────
    def run(self):
        # fade in from black
        self.screen.fill(BLACK)
        pygame.display.flip()
        pygame.time.delay(300)

        for i, (img, text) in enumerate(self.panels):
            if not self._fade('in', 350):
                return
            if not self._reveal_text(text, i):
                return
            if not self._fade('out', 350):
                return

        # title reveal
        pygame.time.delay(200)
        if self.skip_requested:
            return
        if not self._title_reveal():
            return
        self._fade('out', 600)
