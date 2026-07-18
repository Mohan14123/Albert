# 14. Development Guide

Guidelines for integrating and testing the Alfred AI module.

## Local Test Rig

1. Inject mock adapters implementing interfaces in `contracts.py`.
2. Construct a test harness invoking `AIOrchestrator.respond(...)`.
3. Assert step completion traces match execution expectations.
