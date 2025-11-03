@echo off
echo Cleaning up and pushing updates to GitHub...
echo.

git add .
git commit -m "Clean up documentation and add screenshots"
git push origin main

echo.
echo Done!
pause
