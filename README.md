[![Build Status](https://travis-ci.org/wirelessr/HeartsEnv.svg?branch=master)](https://travis-ci.org/wirelessr/HeartsEnv)
[![codecov](https://codecov.io/gh/wirelessr/HeartsEnv/branch/master/graph/badge.svg)](https://codecov.io/gh/wirelessr/HeartsEnv)
  
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
