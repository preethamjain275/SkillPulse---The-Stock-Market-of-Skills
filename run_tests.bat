@echo off
title SkillPulse - Test Suite Runner
cd /d "%~dp0"

echo =================================================================
echo                 SKILLPULSE AUTOMATED TEST SUITE                  
echo =================================================================
echo.
echo Running backend and ML pipeline unit tests with pytest...
echo.

pytest backend/tests/test_api.py -v

echo.
echo =================================================================
echo Test run complete.
echo =================================================================
pause
