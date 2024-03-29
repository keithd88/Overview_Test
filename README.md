# Test Automation Engineer

This test aims to demonstrate your abilities to write and execute a simple testing framework under the GitHub CI/CD runners. The included repository has a single Python file with several functions inside that require basic tests. You can use any framework you are familiar with to write tests for these functions.

- Write tests for each function inside the Python file.
- Push the code and your tests to a GitHub repository, and write a GitHub workflow that should:
  - Execute tests against that image.
  - Bonus points for building a containerized docker image and executing the tests against that image.


# Hardware Test Automation

This test aims to demonstrate your abilities to evaluate a hardware interface and how to interface with an automated testing suite.

Take a look at the documentation for this hardware interfacing device (LabJack T4) https://labjack.com/pages/support?doc=%2Fdatasheets%2Ft-series-datasheet%2F40-hardware-overview-t-series-datasheet.

- Imagine an electronic hardware system with one input and one output. When the input state changes, the output pin toggles on for one second.
- Write a Python test fixture that interfaces with this hardware system. It should toggle a digital output pin and then read that another input pin has changed its state in response to the digital output pin's state change.
- Propose how you would run this fixture in an automated fashion in a CI/CD pipeline. The goal is to execute these tests with hardware-in-the-loop.
- As there is no physical hardware to try with, we understand if the code might not work.
