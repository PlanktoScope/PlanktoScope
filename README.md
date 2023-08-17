# device-backend

All backend software underneath the PlanktoScope device's standard API.

Note: this is a work-in-progress refactor and is not yet ready for general use.

## Introduction

This repository contains the PlanktoScope's backend software services implementing the PlanktoScope's hardware support, application logic, and public API. The current backend functionality can be divided into two categories:

- Device control: controls the PlanktoScope's sensors and actuators, producing raw data. Currently, device control consists of:
  - Hardware abstraction layers: implements a simple, mostly-uniform internal API on different underlying hardware devices, for the application-level hardware controller to be used with different hardware implementations of PlanktoScope designs.
  - Application-level controller: provides device behaviors (such as stop-flow imaging) generalizable across different generations of PlanktoScopes. In software engineering jargon, this is the "business logic" of the PlanktoScope hardware-control software.
  - API adapter: exposes the application-level controller with a standard public API for other software clients to use.
- Data processing: transforms raw data into processed data for downstream analysis and quantification. Currently, data processing functionality consists of:
  - Object isolation: detects objects from camera frames and creates an image for each isolated object, with the background removed.

However, the organization of the source code does not yet reflect the organization of software functionalities.

## Usage

TBD

## Licensing

Except where otherwise indicated, source code provided here is covered by the following information:

Copyright Romain Bazile, Ethan Li, and PlanktoScope project contributors

SPDX-License-Identifier: GPL-3.0-only

You can use the source code provided here under the [GPL 3.0 License](https://www.gnu.org/licenses/gpl-3.0.en.html).
