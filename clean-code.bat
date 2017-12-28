@echo off
REM script to clean and futurize library
REM isort: ordering imports
REM futurize: make it python 3 compatible
REM yapf: nicely format

echo Activating tox environment 
call .tox\check\Scripts\activate

echo FUTURIZE: python 2/3 compatibility
echo ==================================
call futurize -0 -u src tests setup.py
echo ====================
set /p do_futurize=apply modifications [y]/n? 
IF /I '%do_futurize%' NEQ 'n' (
    call futurize -0 -u -w src tests
)

echo ISORT: clean imports
echo ====================
call isort --verbose --check-only --diff --recursive src tests setup.py
echo ====================
set /p do_isort=apply modifications [y]/n? 
IF /I '%do_isort%' NEQ 'n' (
    call isort --verbose --recursive src tests
)

echo YAPF: format code
echo =================
call yapf -vv -d -r src tests setup.py
echo ====================
set /p do_yapf=apply modifications [y]/n? 
IF /I %do_yapf% NEQ 'n' (
    call yapf -i -r src tests
)

exit /b
