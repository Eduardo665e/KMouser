@echo off
title KMouser
chcp 65001 >nul

:MENU

cls

echo.
echo ========================================
echo              KMouser
echo ========================================
echo.
echo   [1] Iniciar KMouser
echo   [2] Calibrar sistema
echo   [3] Testar cursor
echo   [4] Sair
echo.
echo ========================================
echo.

choice /c 1234 /n /m "Escolha uma opcao: "

if errorlevel 4 goto EXIT
if errorlevel 3 goto TEST
if errorlevel 2 goto CALIBRATION
if errorlevel 1 goto MAIN


:MAIN

cls

echo.
echo ========================================
echo          Iniciando KMouser...
echo ========================================
echo.

python main.py

echo.
echo ========================================
echo          KMouser encerrado
echo ========================================
echo.

pause
goto MENU


:CALIBRATION

cls

echo.
echo ========================================
echo        Calibracao do KMouser
echo ========================================
echo.

python calibration.py

echo.
echo ========================================
echo       Calibracao encerrada
echo ========================================
echo.

pause
goto MENU


:TEST

cls

echo.
echo ========================================
echo          TESTE do KMouser
echo ========================================
echo.

python cursor_test.py

echo.
echo ========================================
echo          TESTE encerrado
echo ========================================
echo.

pause
goto MENU


:EXIT

cls

echo.
echo ========================================
echo             KMouser
echo ========================================
echo.
echo          Encerrando...
echo.

timeout /t 2 >nul

exit