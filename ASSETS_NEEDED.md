# Asset Manifest for Lavacakes: Pizza Fury

This document outlines all the visual and audio assets needed to complete the game. The art style should be inspired by "Rick and Morty" - cartoony, a bit grotesque, and full of personality.

## Characters

### Player: The Pizza Man

The hero of our story. He should be overweight, wearing a slightly-too-small pizza shop uniform, and led around by his enormous, sentient belly.

-   **Player Sprite Sheet (`assets/images/player_spritesheet.png`)**
    -   **Dimensions:** Each frame should be approximately 66 pixels wide by 90 pixels tall.
    -   **Animations:**
        -   **Idle:** A 2-4 frame animation of the pizza man standing, with his belly jiggling.
        -   **Walk/Run:** A 4-8 frame animation of him being pulled forward by his belly.
        -   **Jump:** A 1-2 frame animation of him in the air.
        -   **Stomp:** A 1-frame image of him feet-first, ready to crush a hungry customer.

### Enemy: The Hungry Customer

A generic, zombified-looking customer, obsessed with getting pizza.

-   **Enemy Sprite Sheet (`assets/images/enemy_spritesheet.png`)**
    -   **Dimensions:** Each frame should be approximately 30 pixels wide by 50 pixels tall.
    -   **Animations:**
        -   **Walk:** A 2-4 frame animation of the customer shambling back and forth.

## Environment

### Platforms

The surfaces the player will run and jump on. These should look like parts of a Staten Island street scene.

-   **Platform Textures (`assets/images/platforms/`)**
    -   `street.png`: A tileable image of asphalt.
    -   `rooftop.png`: A tileable image of a flat, gravelly rooftop.
    -   `awning.png`: A tileable image of a storefront awning.

### Backgrounds

These will be multi-layered to create a parallax scrolling effect, adding depth to the world.

-   **Background Layers (`assets/images/backgrounds/`)**
    -   `sky.png`: A distant sky layer.
    -   `buildings.png`: A layer of distant buildings.
    -   `foreground.png`: A layer of closer details, like streetlights and fire hydrants.

## Audio

### Sound Effects (`assets/sounds/`)

-   `jump.wav`: A comical "boing" or "sproing" sound.
-   `stomp.wav`: A satisfying, squishy "splat" sound.
-   `death.wav`: A classic, video-gamey "lose a life" sound.

### Music (`assets/music/`)

-   `background.ogg`: An upbeat, slightly zany chiptune track that can be looped seamlessly.