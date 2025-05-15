@echo off
echo Running database migrations...

REM Change to project root directory if needed
cd /d %~dp0\..

REM Load environment variables from .env file
echo Loading environment variables from .env file...
FOR /F "tokens=*" %%A IN (.env) DO (
    SET %%A
)

REM Create the database if it doesn't exist
echo Creating database if it doesn't exist...
mysql -u%DB_USER% -p%DB_PASSWORD% -e "CREATE DATABASE IF NOT EXISTS %DB_NAME%;"

REM Run the SQL migration scripts
echo Running SQL migration scripts...
mysql -u%DB_USER% -p%DB_PASSWORD% %DB_NAME% < scripts\migrations\create_tables.sql

echo Database migration completed successfully!
pause
