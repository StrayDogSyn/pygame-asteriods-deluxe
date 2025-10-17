# 🎵 Pygame Sound Effects - Quick Reference Code

## Basic Sound Loading

```python
import pygame
pygame.init()
pygame.mixer.init()

# Load a single sound
shoot_sound = pygame.mixer.Sound('sounds/laser.wav')

# Load multiple sounds into a list
laser_sounds = [
    pygame.mixer.Sound('sounds/Retro_Laser_Shot_04.wav'),
    pygame.mixer.Sound('sounds/Retro_Laser_Shot_05.wav'),
    pygame.mixer.Sound('sounds/Retro_Laser_Shot_06.wav'),
]

# Set volume (0.0 = silent, 1.0 = max)
shoot_sound.set_volume(0.5)
```

---

## Playing Sounds

```python
# Play once
shoot_sound.play()

# Play and loop 3 times
shoot_sound.play(loops=2)  # Plays 3 times total (original + 2 loops)

# Loop forever (for music/ambience)
shoot_sound.play(loops=-1)

# Stop a sound
shoot_sound.stop()
```

---

## Cycling Through Multiple Sounds (Used for Lasers)

```python
# Setup
laser_sounds = [
    pygame.mixer.Sound('sounds/laser1.wav'),
    pygame.mixer.Sound('sounds/laser2.wav'),
    pygame.mixer.Sound('sounds/laser3.wav'),
]
current_laser = 0

# Play function
def play_laser():
    global current_laser
    laser_sounds[current_laser].play()
    current_laser = (current_laser + 1) % len(laser_sounds)

# Usage in game loop
if keys[pygame.K_SPACE]:
    play_laser()  # Cycles through laser1 → laser2 → laser3 → laser1...
```

**Why?** Each shot sounds different without randomness that could repeat.

---

## Random Sound Selection (Used for Explosions)

```python
import random

# Setup
explosion_sounds = [
    pygame.mixer.Sound('sounds/explosion1.wav'),
    pygame.mixer.Sound('sounds/explosion2.wav'),
    pygame.mixer.Sound('sounds/explosion3.wav'),
]

# Play function
def play_explosion():
    random.choice(explosion_sounds).play()

# Usage
if asteroid_destroyed:
    play_explosion()  # Picks random explosion each time
```

**Why?** Chaos! No two explosions sound identical.

---

## Error Handling (Game Runs Without Sounds)

```python
try:
    shoot_sound = pygame.mixer.Sound('sounds/laser.wav')
    sounds_loaded = True
except:
    # Create dummy that does nothing
    class DummySound:
        def play(self): pass
        def set_volume(self, vol): pass
    
    shoot_sound = DummySound()
    sounds_loaded = False
    print("Warning: Could not load sounds")

# Later in code:
shoot_sound.play()  # Safe - works even if sound failed to load
```

**Why?** Game never crashes if sounds are missing.

---

## Complete Implementation Template

```python
import pygame
import random

pygame.init()
pygame.mixer.init()

# ==========================================
# SOUND LOADING WITH ERROR HANDLING
# ==========================================

try:
    # PLAYER SHOOTING (cycling for variety)
    laser_sounds = [
        pygame.mixer.Sound('sounds/Retro_Laser_Shot_04.wav'),
        pygame.mixer.Sound('sounds/Retro_Laser_Shot_05.wav'),
        pygame.mixer.Sound('sounds/Retro_Laser_Shot_06.wav'),
        pygame.mixer.Sound('sounds/puny_laser.wav'),
    ]
    current_laser_index = 0
    
    # ENEMY SHOOTING (distinctive sound)
    ufo_laser = pygame.mixer.Sound('sounds/Big_Laser_Beam.wav')
    
    # EXPLOSIONS (random for chaos)
    explosion_sounds = [
        pygame.mixer.Sound('sounds/explosion_asteroid.wav'),
        pygame.mixer.Sound('sounds/explosion_asteroid2.wav'),
        pygame.mixer.Sound('sounds/Space_Explosion.wav'),
        pygame.mixer.Sound('sounds/Asteroide_Pelicula_SFX.wav'),
    ]
    
    # ACHIEVEMENTS (high value events)
    achievement_sounds = [
        pygame.mixer.Sound('sounds/Achievement.wav'),
        pygame.mixer.Sound('sounds/Jingle_Achievement_00.wav'),
        pygame.mixer.Sound('sounds/Jingle_Achievement_01.wav'),
    ]
    
    # LEVEL UP (wave completion)
    level_up_sounds = [
        pygame.mixer.Sound('sounds/Level_Up_01.wav'),
        pygame.mixer.Sound('sounds/Level_Up_02.wav'),
        pygame.mixer.Sound('sounds/Level_Up_03.wav'),
    ]
    
    # POWER-UPS (collect items)
    powerup_sound = pygame.mixer.Sound('sounds/Magic_Reveal.wav')
    
    # VOLUME CONTROL (balance loudness)
    for sound in laser_sounds:
        sound.set_volume(0.3)  # Quiet (frequent)
    ufo_laser.set_volume(0.4)
    for sound in explosion_sounds:
        sound.set_volume(0.5)
    for sound in achievement_sounds:
        sound.set_volume(0.6)  # Loud (rare)
    for sound in level_up_sounds:
        sound.set_volume(0.6)
    powerup_sound.set_volume(0.5)
    
    print("✓ All sounds loaded!")
    
except Exception as e:
    print(f"⚠ Sound loading failed: {e}")
    
    # Dummy sound that does nothing
    class DummySound:
        def play(self): pass
        def set_volume(self, vol): pass
    
    laser_sounds = [DummySound()] * 4
    current_laser_index = 0
    ufo_laser = DummySound()
    explosion_sounds = [DummySound()] * 4
    achievement_sounds = [DummySound()] * 3
    level_up_sounds = [DummySound()] * 3
    powerup_sound = DummySound()


# ==========================================
# SOUND PLAYBACK FUNCTIONS
# ==========================================

def play_laser():
    """Cycle through laser sounds"""
    global current_laser_index
    laser_sounds[current_laser_index].play()
    current_laser_index = (current_laser_index + 1) % len(laser_sounds)

def play_ufo_laser():
    """UFO fires"""
    ufo_laser.play()

def play_explosion():
    """Random explosion"""
    random.choice(explosion_sounds).play()

def play_achievement():
    """High value target destroyed"""
    random.choice(achievement_sounds).play()

def play_level_up():
    """Wave completed"""
    random.choice(level_up_sounds).play()

def play_powerup():
    """Item collected"""
    powerup_sound.play()


# ==========================================
# USAGE IN GAME LOOP
# ==========================================

# When player shoots
if keys[pygame.K_SPACE]:
    play_laser()

# When UFO shoots
if ufo_ready_to_shoot:
    play_ufo_laser()

# When asteroid destroyed
if bullet_hit_asteroid:
    play_explosion()
    asteroid.destroy()

# When UFO destroyed (special: explosion + achievement!)
if bullet_hit_ufo:
    play_explosion()
    play_achievement()  # Double sound for big event!
    score += 500

# When ship destroyed
if ship_hit_asteroid:
    play_explosion()
    lives -= 1

# When power-up collected
if ship_touches_powerup:
    play_powerup()
    apply_powerup_effect()

# When wave completed
if all_asteroids_destroyed:
    wave += 1
    play_level_up()
    spawn_new_wave()
```

---

## Advanced: Layering Sounds for Impact

```python
# Play multiple sounds simultaneously for major events
def destroy_ufo():
    play_explosion()      # Main explosion
    play_achievement()    # Victory fanfare
    # Both play at once = maximum impact!
```

---

## Advanced: Spatial Audio (Make Sounds Directional)

```python
import math

def play_explosion_at(x, y):
    """Play explosion with volume based on distance from center"""
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
    max_distance = math.sqrt(center_x**2 + center_y**2)
    
    # Volume decreases with distance
    volume = 1.0 - (distance / max_distance)
    volume = max(0.1, min(1.0, volume))  # Clamp between 0.1 and 1.0
    
    sound = random.choice(explosion_sounds)
    sound.set_volume(volume * 0.5)  # 0.5 = master volume
    sound.play()
```

---

## Advanced: Background Music

```python
# Music uses different API than sound effects
pygame.mixer.music.load('sounds/background_music.mp3')
pygame.mixer.music.set_volume(0.3)  # Quieter than SFX
pygame.mixer.music.play(-1)  # -1 = loop forever

# Control music
pygame.mixer.music.pause()
pygame.mixer.music.unpause()
pygame.mixer.music.stop()
```

---

## File Format Requirements

✅ **Recommended:** WAV files
- Format: PCM 16-bit
- Sample Rate: 44100 Hz (CD quality)
- Channels: Mono or Stereo

❌ **Avoid:** MP3 for sound effects (use for music only)
- Has slight delay on play()
- Not suitable for instant feedback

**Convert with Audacity:**
1. File → Open → your_sound.mp3
2. File → Export → Export as WAV
3. Set: Sample Rate 44100, Format PCM 16-bit
4. Save

---

## Debugging Checklist

**No sound at all?**
```python
# Add this at start of program
print(pygame.mixer.get_init())  # Should show: (44100, -16, 2)
```

**Check if sound loaded:**
```python
try:
    sound = pygame.mixer.Sound('test.wav')
    print(f"✓ Loaded: {sound.get_length()} seconds")
except:
    print("✗ Failed to load")
```

**Test sound immediately:**
```python
sound = pygame.mixer.Sound('sounds/test.wav')
sound.play()
pygame.time.wait(2000)  # Wait 2 seconds to hear it
```

---

## Common Mistakes

❌ **Wrong:** Loading in game loop
```python
while running:
    sound = pygame.mixer.Sound('laser.wav')  # SLOW!
    sound.play()
```

✅ **Right:** Load once at start
```python
sound = pygame.mixer.Sound('laser.wav')  # Load once
while running:
    sound.play()  # Play many times
```

---

❌ **Wrong:** Forgetting to init mixer
```python
pygame.init()
sound = pygame.mixer.Sound('laser.wav')  # Might fail!
```

✅ **Right:** Initialize mixer explicitly
```python
pygame.init()
pygame.mixer.init()  # Required!
sound = pygame.mixer.Sound('laser.wav')
```

---

❌ **Wrong:** Hardcoding volume everywhere
```python
explosion_sounds[0].set_volume(0.5)
explosion_sounds[1].set_volume(0.5)
explosion_sounds[2].set_volume(0.5)
```

✅ **Right:** Use loops
```python
for sound in explosion_sounds:
    sound.set_volume(0.5)
```

---

## Quick Copy-Paste Examples

### Just Shoot Sound
```python
import pygame
pygame.init()
pygame.mixer.init()

try:
    shoot = pygame.mixer.Sound('sounds/laser.wav')
    shoot.set_volume(0.3)
except:
    class DummySound:
        def play(self): pass
    shoot = DummySound()

# In game loop:
if shoot_button_pressed:
    shoot.play()
```

### Just Explosion Sound
```python
import pygame, random
pygame.init()
pygame.mixer.init()

try:
    explosions = [
        pygame.mixer.Sound('sounds/exp1.wav'),
        pygame.mixer.Sound('sounds/exp2.wav'),
    ]
    for exp in explosions:
        exp.set_volume(0.5)
except:
    class DummySound:
        def play(self): pass
    explosions = [DummySound(), DummySound()]

# In game loop:
if something_exploded:
    random.choice(explosions).play()
```

---

## Performance Notes

- ✅ Loading sounds: Do once at startup
- ✅ Playing sounds: As many times as needed
- ✅ Typical max: ~8 sounds playing simultaneously
- ❌ Loading in game loop: Will cause lag

**Memory usage:** Each sound loads into RAM. A typical 1-second .wav at 44100 Hz = ~172 KB.

---

**You're now ready to make any pygame project sound professional! 🎮🔊**
