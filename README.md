# acton_ai
This repo contains tooling for data collection, management, and training of ML models
for robot action policies. It is currently only compatible with ElephantRobotics' 
MyArmM and MyArmC robotic arms.

_________________

[![PyPI version](https://badge.fury.io/py/acton_ai.svg)](http://badge.fury.io/py/acton_ai)
[![Test Status](https://github.com/apockill/acton_ai/workflows/Test/badge.svg?branch=main)](https://github.com/apockill/acton_ai/actions?query=workflow%3ATest)
[![Lint Status](https://github.com/apockill/acton_ai/workflows/Lint/badge.svg?branch=main)](https://github.com/apockill/acton_ai/actions?query=workflow%3ALint)
[![codecov](https://codecov.io/gh/apockill/acton_ai/branch/main/graph/badge.svg)](https://codecov.io/gh/apockill/acton_ai)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://timothycrosley.github.io/isort/)
_________________

[Read Latest Documentation](https://apockill.github.io/acton_ai/) - [Browse GitHub Code Repository](https://github.com/apockill/acton_ai/)
_________________

## Tools

After installing ([under Development](#Development)) the package, the following tools
will be in your path:

`acton_teleop`:
- Passes joint from MyArmC to MyArmM, allowing for teleoperation of the MyArmM

`acton_validate`: 
- Prints the firmware and hardware version of the MyArmM and MyArmC arms

`acton_calibrate`:
- Places the MyArmM into a zero'ed out position, and guides user through calibration of
  the MyArmC

## Development

### Installing python dependencies
```shell
poetry install
```

### Running Tests
```shell
pytest .
```

### Formatting Code
```shell
bash .github/format
```

### Linting
```shell
bash .github/check_lint
```