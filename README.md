# opencmm
![Test](https://github.com/OpenCMM/opencmm/actions/workflows/ci.yml/badge.svg)
![UI](https://github.com/OpenCMM/opencmm/actions/workflows/ui.yml/badge.svg)

An image-based CMM (Coordinate Measuring Machine) system for CNC machine tools

## Introduction
This project is an image-based CMM (Coordinate Measuring Machine) system for CNC machine tools. It can be used to measure the workpiece on the CNC machine tool without removing the workpiece from the machine tool.

## How it works:

1. exports a stl file from a cad/cam software
2. access to an desktop app and upload the stl file
3. download gcode
4. start the cnc machine with the gcode and camera with the desktop app
5. see the result with the desktop app

## Goal
- 1 micron precision
- save centering and measuring time 
