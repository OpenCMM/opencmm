# opencmm
![Test](https://github.com/OpenCMM/opencmm/actions/workflows/ci.yml/badge.svg)
![UI](https://github.com/OpenCMM/opencmm/actions/workflows/ui.yml/badge.svg)

An opensource on-machine CMM (Coordinate Measuring Machine) system

## Introduction
This project is an opensource on-machine CMM (Coordinate Measuring Machine) system. It can be used to measure the workpiece on the CNC machine without removing the workpiece from the machine.

![a laser triagulation sensor](https://opencmm.xyz/assets/images/sensor-55b7cf98350f293eba2c2b9d593bdd4f.png)

## How it works:

1. exports a stl file from a cad/cam software
2. upload the stl file
3. send gcode to the cnc machine
4. start the cnc machine with the gcode
5. see the result with the desktop app

## Prerequisites

- CNC machine that supports [MTConnect](https://www.mtconnect.org/)
- [C++ Agent](https://github.com/mtconnect/cppagent)
- A computer with 4GB RAM and 10GB free disk space
- Docker >= 24.0.7
- Docker-compose >= 1.29.2
- OpenCMM device (We plan to release the device)

## Installation
Clone the repository
```bash
git clone https://github.com/OpenCMM/opencmm.git
cd opencmm
```

## Quick Start
```bash
docker-compose up -d
```

## Goal
10 micron precision
