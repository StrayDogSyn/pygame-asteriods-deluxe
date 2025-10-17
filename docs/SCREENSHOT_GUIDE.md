# 📸 Screenshot Guide for Portfolio

## Perfect Preview Image Tips

### Timing for Best Screenshot

**Ideal Gameplay Moment:**
- Mid-game with 5-8 asteroids visible
- Ship firing (bullet trail visible)
- Shield active (energy glow visible)
- 1-2 particles/explosions in frame
- Score around 5,000-15,000 (shows progression)
- Multiple stars visible in background
- Nebula clouds visible for atmosphere

**What to Avoid:**
- Empty screen (boring)
- Too cluttered (confusing)
- Game Over screen (negative)
- Menu screen only (not enough action)

### Recommended Settings

```python
# Before capturing, set:
- Color Scheme: Matrix (Green) or Amber Terminal (classic look)
- CRT Effects: ON (V key) for authentic retro aesthetic
- Resolution: 1200x900 (scales well for web)
```

### How to Capture

**Windows:**
1. Start game: `python asteroids_deluxe.py`
2. Play until ideal moment
3. Press `Windows + Shift + S` for Snipping Tool
4. Select game window
5. Save as `preview.png`

**Cross-Platform (Pygame):**
```python
# Add to game loop temporarily:
if keys[pygame.K_F12]:
    pygame.image.save(screen, "preview.png")
    print("Screenshot saved!")
```

### Editing Tips (Optional)

1. **Crop**: Ensure game window is centered
2. **Resolution**: 1920x1080 or 1200x900 ideal
3. **Compression**: Use PNG for quality, optimize for web
4. **Border**: Add subtle shadow/border for GitHub display

### GitHub Display Optimization

```markdown
# In README.md:
![Asteroids Deluxe Gameplay](preview.png)

# Or with alignment:
<div align="center">
  <img src="preview.png" alt="Asteroids Deluxe Gameplay" width="800">
</div>
```

### Portfolio Presentation

**Multiple Screenshots Strategy:**
1. `preview.png` - Main hero image (action shot)
2. `screenshot-menu.png` - Color schemes showcase
3. `screenshot-effects.png` - Particle effects demo
4. `screenshot-gameplay.gif` - 5-second gameplay loop (optional)

**GIF Creation** (Advanced):
```bash
# Using FFmpeg
ffmpeg -i gameplay.mp4 -vf "fps=15,scale=800:-1:flags=lanczos" -loop 0 preview.gif
```

---

## Current Preview Image

The existing `preview.png` should showcase:
✅ Active gameplay
✅ Visual effects (glow, particles)
✅ HUD elements (score, lives)
✅ Asteroids and ship visible
✅ 16-bit aesthetic clear

If you need a new screenshot, follow the guide above!
