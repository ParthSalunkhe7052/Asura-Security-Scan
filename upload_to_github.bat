@echo off
echo ========================================
echo    Uploading ASURA to GitHub
echo ========================================
echo.

echo Step 1: Configuring git...
git config user.email parth.ajit7052@gmail.com
git config user.name ParthSalunkhe7052
echo Done!

echo.
echo Step 2: Adding files...
git add .
if errorlevel 1 (
    echo ERROR: Failed to add files
    pause
    exit /b 1
)
echo Done!

echo.
echo Step 3: Committing...
git commit -m "Initial commit: ASURA v0.3.0"
if errorlevel 1 (
    echo ERROR: Failed to commit
    pause
    exit /b 1
)
echo Done!

echo.
echo Step 4: Adding remote...
git remote add origin https://github.com/ParthSalunkhe7052/Asura-Security-Scan.git
if errorlevel 1 (
    echo WARNING: Remote might already exist, continuing...
)
echo Done!

echo.
echo Step 5: Renaming branch to main...
git branch -M main
echo Done!

echo.
echo Step 6: Pushing to GitHub...
echo You may be prompted for GitHub credentials...
git push -u origin main
if errorlevel 1 (
    echo ERROR: Failed to push to GitHub
    echo.
    echo Please check:
    echo 1. You have access to the repository
    echo 2. Repository exists on GitHub
    echo 3. You are logged in to GitHub
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Upload Complete! 🎉
echo ========================================
echo.
echo Your project is now live at:
echo https://github.com/ParthSalunkhe7052/Asura-Security-Scan
echo.
echo Next steps:
echo 1. Visit the repository
echo 2. Create a release (v0.3.0)
echo 3. Add topics: security, python, react
echo 4. Share with the world!
echo.
pause
