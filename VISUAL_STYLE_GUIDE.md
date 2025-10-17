# Visual Style Guide - 16-Bit 3D Enhancements

## 🎨 Color & Lighting Philosophy

### Light Source
Primary light source: **Top-Left** (-0.5, -0.7)
- Creates consistent shadows across all objects
- Edges facing light = bright
- Edges away from light = dark

### Material Types

#### 1. Metallic (Ship, UFO)
```
Brightness Zones:
- Shadow:  20-30% base color
- Dark:    40-50% base color
- Mid:     70% base color
- Base:    100% base color
- Light:   120-130% base color (clamped to 255)
- Bright:  160-170% base color
- Specular: 200%+ (white hot spots)
```

#### 2. Rocky (Asteroids)
```
Brightness Zones:
- Shadow:  20-40% base color
- Mid:     70% base color
- Base:    100% base color
- Light:   120% base color
- Bright:  150% base color
+ Glow on bright edges
```

#### 3. Energy (Bullets, Shields, Flames)
```
Structure:
- Outer Glow: 5+ layers, fading alpha
- Main Body: Full color
- Core:      Brighter (150%)
- Hot Spot:  White or 200% brightness
```

#### 4. Glass/Panel (UI)
```
Top Zone:    Bright (120%), high alpha
Middle Zone: Solid fill
Bottom Zone: Dark (60-90%), gradient
+ Beveled edges
+ Corner glow accents
```

## 🌈 Glow Effect Specifications

### Standard Glow (bullets, small effects)
- **Layers**: 5
- **Radius Growth**: +2 pixels per layer
- **Alpha Decay**: 80 * (layer / 5)
- **Intensity Multiplier**: 0.5 - 2.0

### Large Glow (ship, UFO, stars)
- **Layers**: 4-6
- **Radius Growth**: +4 pixels per layer
- **Alpha Decay**: 50 * (layer / total)
- **Blend Mode**: SRCALPHA additive

### Energy Glow (flames, explosions)
- **Layers**: 5+
- **Radius Growth**: +3 pixels per layer
- **Alpha Decay**: 70 * (layer / 5)
- **Color Shift**: Outer = accent → Inner = white

## 📐 Depth Layer Distances

### Background Layers (Z-order):
```
Z=0:  Background fill (solid color)
Z=1:  Nebulae (alpha 5-15)
Z=2:  Far stars (layer 1) - tiny, dim
Z=3:  Grid effects
Z=4:  Mid stars (layer 2) - medium
Z=5:  Near stars (layer 3) - large, bright
```

### Game Object Layers:
```
Z=6:  Particles (background trails)
Z=7:  Asteroids
Z=8:  UFO
Z=9:  Enemy bullets
Z=10: Ship
Z=11: Player bullets
Z=12: Explosions (bright particles)
```

### UI Layers:
```
Z=13: UI panels (translucent)
Z=14: Text with shadows
Z=15: Flashing effects
```

## 💎 Material Rendering Techniques

### Metallic Surfaces (Ship, UFO)

**Technique**: Multi-zone gradient + specular highlights

1. **Base Fill**: Start with darkest color (20-40%)
2. **Gradient Zones**: Apply lighting-based gradients
3. **Edge Lighting**: Calculate normals, apply brightness
4. **Specular Highlight**: Add bright spots near light source
5. **Outline**: Contrasting edge line
6. **Glow**: Subtle ambient glow

**Code Pattern**:
```python
dark = (c * 0.2)
shadow = (c * 0.4)
mid = (c * 0.7)
base = (c * 1.0)
light = (min(255, c * 1.2))
bright = (min(255, c * 1.6))
specular = (255, 255, 255) or (c * 2.0)
```

### Rocky Surfaces (Asteroids)

**Technique**: Edge-based directional lighting + craters

1. **Ambient Glow**: Faint outer halo
2. **Dark Fill**: Base with shadow color
3. **Edge Analysis**: For each edge:
   - Calculate normal vector
   - Dot product with light direction
   - Apply graduated brightness
4. **Crater Details**: Dark circles with bright rim arcs
5. **Surface Cracks**: Fine dark lines
6. **Outline**: Medium-bright edge

**Edge Lighting Thresholds**:
```
light_amount > 0.6:  Bright + glow (4px line)
light_amount > 0.3:  Light (3px line)
light_amount > 0.0:  Mid (2px line)
light_amount > -0.3: Base (2px line)
light_amount < -0.3: Dark/shadow (2px line)
```

### Energy Effects (Bullets, Flames, Shields)

**Technique**: Multi-layer additive glow + hot core

1. **Outer Glow Rings**: 5+ expanding circles
   - Largest radius, lowest alpha
   - Progressively smaller and brighter
2. **Main Body**: Full-opacity shape
3. **Gradient Core**: Brighter inner region
4. **Hot Spot**: Intense white or bright center
5. **Motion Trail**: Repeated shapes along velocity vector

**Flame-Specific**:
```
Outer:  Accent color (full)
Middle: Yellow/orange (75%)
Core:   White hot (50%)
Glow:   Expanding rings (alpha 70)
```

### Glass Panels (UI)

**Technique**: Three-zone gradient + beveled edges

1. **Top Shine** (⅓ height):
   - Gradient from 120% bright → 100%
   - Alpha: fill_alpha + 35 → fill_alpha
2. **Middle Fill** (⅓ height):
   - Solid color at fill_alpha + 10
3. **Bottom Shadow** (⅓ height):
   - Gradient from 90% → 60% brightness
   - Alpha: fill_alpha → fill_alpha - 20
4. **Inner Shadows**: 4 layers, top and left edges
5. **Highlights**: 3 layers, bottom and right edges
6. **Border Glow**: 4 expanding layers outside border
7. **Corner Accents**: Radial glow + bright lines

## ⚡ Animation Techniques

### Pulsing Glow
```python
pulse = (sin(time * speed + offset) + 1) / 2  # 0 to 1
current_alpha = base_alpha * (0.7 + pulse * 0.3)
```

### Twinkling Stars
```python
twinkle = (sin(time * speed + offset) + 1) / 2
brightness = base * (0.4 + twinkle * 0.6)
```

### Rotating Energy
```python
rotation = (time * speed) % (2 * pi)
for band in range(num_bands):
    angle = rotation + (band * 2*pi / num_bands)
```

### Flickering Flame
```python
length = base_length * random.uniform(0.6, 1.0)
# Random variation each frame
```

### Rotating Beam
```python
angle = time * rotation_speed
end_x = start_x + cos(angle) * length
end_y = start_y + sin(angle) * length
```

## 🎯 Visual Hierarchy

### Size & Brightness = Importance
1. **Player Ship**: Medium size, bright colors, strong glow
2. **UFO**: Large, very bright, distinctive metallic shine
3. **Asteroids**: Varied sizes, medium brightness, rocky texture
4. **Bullets**: Small, very bright with strong trails
5. **Particles**: Tiny, fading brightness and alpha
6. **Stars**: Tiny to small, dim to medium, twinkling

### Glow Intensity = Energy Level
- **High Energy**: Bullets (1.5), Flames (1.5), UFO lights (1.0)
- **Medium Energy**: Ship glow (0.8), Star layer 3 (0.8)
- **Low Energy**: Asteroids (ambient), Star layer 2 (0.4)
- **Minimal**: Star layer 1 (no glow), Particles (fading)

## 🔍 Detail Levels by Object Size

### Large Objects (UFO, Large Asteroids)
- Multiple gradient zones (6-8 layers)
- Surface details (lights, craters, cracks)
- Complex shading (edge + zone based)
- Strong ambient glow
- Specular highlights

### Medium Objects (Ship, Medium Asteroids)
- Moderate gradients (4-5 layers)
- Some surface detail (2-3 craters, panel lines)
- Edge-based shading
- Moderate glow
- Simple highlights

### Small Objects (Bullets, Small Asteroids, Stars)
- Simple gradients (2-3 layers)
- Minimal detail
- Glow-based rendering
- Core + halo structure

### Particles
- Single pixel or small circle
- Glow for larger particles
- Alpha-based fading
- No surface detail

## 🎨 Color Temperature Guide

### Warm (Yellow-Orange-Red)
- Flames: Accent → Yellow → White
- Explosions: Accent color
- Alert states: Use in Red Alert scheme

### Cool (Blue-Cyan)
- Shields: Bright scheme color
- UFO lights: Alternating accent/primary
- Ice/crystal effects: Blue-tinted

### Neutral (White-Gray)
- Stars: White with slight tints
- Specular highlights: Pure white
- Laser cores: White hot

### Scheme-Adaptive
All effects use `current_scheme` colors:
- Maintains visual consistency
- Automatic recoloring on scheme change
- Ensures good contrast

## 💡 Pro Tips

### Performance
- Use SRCALPHA surfaces for alpha blending
- Pre-calculate color variations
- Batch similar transparency operations
- Limit glow layers to 3-6
- Cache static gradients when possible

### Visual Polish
- Always offset shadows (1-2 pixels down-right)
- Use odd numbers for layer counts (3, 5, 7)
- Bright highlights should be 1.5-2x base color
- Dark shadows should be 0.2-0.5x base color
- Glow radius = object radius + (layers * 2-4)

### Consistency
- Keep light direction consistent (-0.5, -0.7)
- Use same gradient ratios across similar objects
- Match glow intensity to energy level
- Maintain visual hierarchy through size/brightness

### 16-Bit Feel
- Bold color transitions (not too smooth)
- High contrast highlights
- Clear edge definition
- Visible glow halos
- Distinct material types

## 📊 Quick Reference Values

```
ALPHA RANGES:
- Solid: 255
- UI Panels: 40-100
- Glows: 20-150
- Particles: 255 → 0 (fade)
- Nebulae: 5-15
- Shadows: 60-100

BRIGHTNESS MULTIPLIERS:
- Shadow: 0.2-0.3
- Dark: 0.4-0.5
- Mid: 0.7
- Base: 1.0
- Light: 1.2-1.3
- Bright: 1.5-1.7
- Specular: 2.0+ or white

GLOW SIZES:
- Small (bullets): +2px per layer, 5 layers
- Medium (ship): +3px per layer, 4 layers
- Large (UFO): +4-6px per layer, 6 layers

LINE WIDTHS:
- Fine detail: 1px
- Regular edges: 2px
- Highlighted edges: 3-4px
- Borders: 2-4px
```

This creates a cohesive, polished 16-bit 3D aesthetic!
