[![Build Status](https://travis-ci.org/wirelessr/HeartsEnv.svg?branch=master)](https://travis-ci.org/wirelessr/HeartsEnv)
[![codecov](https://codecov.io/gh/wirelessr/HeartsEnv/branch/master/graph/badge.svg)](https://codecov.io/gh/wirelessr/HeartsEnv)
  
### Description
- 1.0.0 Full rules of Hearts has been supported

#### Single Player Enviroment
The environment is based on standard gym, so you can use `reset`, `step`, `render`, etc. to control the game.  
Moreover, the action space supports `sample` and `contains`. When you cannot consider what action you should take,
you can use `sample` to generate a regular action.  
  
The `render` supports two modes, *human* and *ansi*; the human mode can display colored cards, and the ansi mode 
display only the text.  
Every action you feed into `step` **MUST** pass the validation, or the environment throws the exception instead.  
You can check the type of exception to clarify what rule you violated.

```python
from hearts.single import SingleEnv
done = False
env = SingleEnv()

env.reset()
while not done:
    env.render()
    # You can simply use sample() to finish the whole game
    action = env.action_space.sample()

    obs, reward, done, _ = self.env.step(action)
    # Do whatever learning algorithm
```


### Reference
  
[gym.env](https://github.com/openai/gym/blob/master/gym/core.py)  
[Slides](https://docs.google.com/presentation/d/1MdtczHpVs6iht5Z_NQh_97ZHCyOkWD1f01pTfKBuW9s/edit?usp=sharing)

## How to use
1. Install docker and docker-compose
    1. [install docker](https://docs.docker.com/install/)
    1. [install docker compose](https://docs.docker.com/compose/install/#install-compose)
1. Goto docker-compose working directory
    ```
    cd HeartsEnv
1. Build docker image
    ```
    make
1. Start docker containers
    ```
    docker-compose up -d
1. Run poker bot
    ```
    docker-compose exec hearts python /hearts/demo/demo_hearts.py

## Jupyter (iPython)
1. Open browser
    ```
    http://localhost:8888/

## View OpenGL output
1. Open browser
    ```
    http://localhost:6080/

## Other commands
1. In docker-compose working directory
    1. Remove all docker containers
        ```
        docker-compose down
    1. Get shell of docker containers
        ```
        docker-compose exec hearts bash
