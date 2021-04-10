# Azul (work in progress)

When we bought it we were one player too many. Is it weird to volunteer for skipping the first games so you can program it instead?!

I did end up playing this game quite a bit and it's a fantastic game! The design of this game is just terrific. Also, the rules are not very complex, which makes it a fun programming project.

## To do list
Implement the following structure:
- Create class `Tile`
- Create class `PlayerBoard`
- Create class `Plate`
- Create class `InnerRoundTileArea`
- Create class `InnerRoundMinusPoints`

- Each `Player` has a `Playerboard`
- Each `PlayerBoard` has
    - `InnerRoundTileArea`
    - `InnerRoundMinusPoints`
    - `EndStateTileArea`
    - current points
- Each `SharedBoard` has
    - `Plate`s
- Each `Plate` has
    - `Tile`s

- Each `Player` can interact with `SharedBoard`
- Each `Player` can interact with their `PlayerBoard`
- Each `Player` manages the interactions between the attributes on their `PlayerBoard`

Add a visual explanation to documentation of
- `PlayerBoard`
- `Plate`
- `Tile`
- `InnerroundTileArea`
- `InnerRoundMinusPoints`
- `SharedBoard`
