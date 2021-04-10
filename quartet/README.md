# Quartets

Even though playing this game is no fun at all, programming it has been a lot of fun. It's a great way to practice your programming and also serves as a great programming challenge for job interviews!

This implementation of quartets is for the 4-player quartet with 5 quartets. Running a simulation will generate a log file, which contains logs of each move, the subsequent state of the game and, of course, the winner of the game. 

## Player policies

While programming this game, I got carried away a little bit and decided to implement different playing policies that a player can choose from:
- *naive game* - `quartet_minimal.py`: I consider this the minimum solution, because it shows a solution in the Python sense, without "cluttering" the code  with game decision tactics and memory representations.
- *perfect memory game* - `quartet_clever.py`: Adds decision policies to the `Player` instances. Some of these decision policies apply simple rules that rely on knowledge gained during a game (who owns which cards, etc.). I like this implementation, because it allows me to apply a clever policy to my avater, whilst leaving my opponents with the 'naive' strategy! The implemented policies are: `random`, `semi-random` and `pretty-smart`.

## How to run

```bash
$ python3 quartet_minimal.py
```
This will create a log file `quartet_minimal.log`.

```bash
$ python3 quartet_clever.py
```

If you run the clever decision implementation like this, the policies (`random`, `semi-random` and `pretty-smart`) are assigned randomly to the players. You will find each player's decision policy at the top of `quartet_clever.log`
