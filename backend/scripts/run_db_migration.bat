@echo off
echo Running database migration script to add session_id to feedback table...
cd ..
python scripts/add_session_id_to_feedback.py
if %ERRORLEVEL% EQU 0 (
    echo Migration completed successfully!
) else (
    echo Migration failed with error code %ERRORLEVEL%
    echo Please check the logs for details.
)
pause
