@echo off
REM script to shortcut tox environment activation
REM if called without arguments, list available tox environments

if "%1" == "" goto list_env

echo Activating tox environment %1
call .tox\%1\Scripts\activate
exit /b

:list_env
echo No arguments given. list available tox environments
call tox -l
exit /b