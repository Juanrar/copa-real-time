@ECHO OFF
REM Script .bat para ejecutar dos archivos Python en terminales separadas

SET "TITLE1=Cliente 1"
SET "TITLE2=Cliente 2"
SET TARGET_URL=https://machuca.com.ar:4000/reset

REM Ruta al intérprete de Python (generalmente solo 'python' si está en el PATH)
SET PYTHON_EXE="D:\Users\ezele\anaconda3\envs\sim_undav\python.exe"

REM curl %TARGET_URL% -k

REM Ruta a tu primer script de Python
SET SCRIPT1_PATH="client.py"

REM Ruta a tu segundo script de Python
SET SCRIPT2_PATH="client2.py"

ECHO Iniciando el primer script de Python en una nueva terminal...
START "%TITLE1%" %PYTHON_EXE% %SCRIPT1_PATH%

ECHO Iniciando el segundo script de Python en una nueva terminal...
START "%TITLE2%" %PYTHON_EXE% %SCRIPT2_PATH%

ECHO Ambos scripts se han iniciado en terminales separadas.