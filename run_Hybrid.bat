@echo off
echo ========================================
echo Hybrid Recommendation System
echo ========================================
echo.
echo This script combines recommendations from:
echo - KNN_model/rcm_games.csv (or recommendations.csv)
echo - CB_model/cb_recommendations.csv
echo.
echo Make sure you have run both KNN and CB models first!
echo.
pause
cd Hybrid_model
python run_hybrid.py
cd ..
pause