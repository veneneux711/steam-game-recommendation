#!/usr/bin/env python3
"""
Automated Test Script for Steam ML Recommendation System
This script automates the testing process for the first 15 users in synthetic_data
"""

import os
import shutil
import subprocess
import time
import json
import pandas as pd
from pathlib import Path

def copy_user_data(user_id, source_dir, knn_target_dir, cb_target_dir, user_data_target_dir):
    """
    Copy user data files to respective folders
    - CSV files (fav_games.csv, your_games.csv) to KNN_model folder
    - JSON file (cb_user_ratings.json) to user_data folder
    """
    print(f"\n=== Processing User {user_id} ===")
    
    # Source paths - need to find the correct user directory format
    # The directories are named like "user_01_Random_Player", "user_02_RPG_Fan", etc.
    user_dir_patterns = [
        f"user_{user_id:02d}_Random_Player",
        f"user_{user_id:02d}_RPG_Fan",
        f"user_{user_id:02d}_FPS_Fan",
        f"user_{user_id:02d}_Indie_Cozy",
        f"user_{user_id:02d}_Strategy_Fan",
        f"user_{user_id:02d}_Action_Adventure"
    ]
    
    user_source_dir = None
    for pattern in user_dir_patterns:
        test_dir = os.path.join(source_dir, pattern)
        if os.path.exists(test_dir):
            user_source_dir = test_dir
            break
    
    if user_source_dir is None:
        print(f"User directory not found for user {user_id}")
        return False
    
    # Copy CSV files to KNN_model folder
    csv_files = ["fav_games.csv", "your_games.csv"]
    for csv_file in csv_files:
        source_file = os.path.join(user_source_dir, csv_file)
        target_file = os.path.join(knn_target_dir, csv_file)
        
        if os.path.exists(source_file):
            shutil.copy2(source_file, target_file)
            print(f"[INFO] Copied {csv_file} to KNN_model folder")
        else:
            print(f"[WARNING] {csv_file} not found in user directory")
    
    # Copy JSON file to user_data folder
    json_file = "cb_user_ratings.json"
    source_json = os.path.join(user_source_dir, json_file)
    target_json = os.path.join(user_data_target_dir, json_file)
    
    if os.path.exists(source_json):
        shutil.copy2(source_json, target_json)
        print(f"[INFO] Copied {json_file} to user_data folder")
    else:
        print(f"[WARNING] {json_file} not found in user directory")
    
    return True

def run_knn_model():
    """Run KNN model and get recommendations"""
    print("\n=== Running KNN Model ===")
    
    try:
        # Run the KNN batch file
        result = subprocess.run(
            ["run_KNN.bat"],
            cwd=".",
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        print("KNN Model Output:")
        print(result.stdout)
        if result.stderr:
            print("KNN Model Errors:")
            print(result.stderr)
        
        # Check if recommendations were generated
        knn_recommendations = os.path.join("KNN_model", "rcm_games.csv")
        if os.path.exists(knn_recommendations):
            print("[SUCCESS] KNN recommendations generated successfully")
            return True
        else:
            print("[ERROR] KNN recommendations not found")
            return False
            
    except subprocess.TimeoutExpired:
        print("[ERROR] KNN model execution timed out")
        return False
    except Exception as e:
        print(f"[ERROR] Error running KNN model: {e}")
        return False

def run_cb_model():
    """Run CB model, train it, and get recommendations"""
    print("\n=== Running CB Model ===")
    
    try:
        # First, train the model
        print("Training CB model...")
        
        # We need to simulate the button clicks for training and getting recommendations
        # Since this is a GUI application, we'll use a different approach
        
        # Import and use the CB model functions directly
        import sys
        sys.path.append("CB_model")
        from ContentBased_commands import train_model, get_recommendations
        
        # Train the model
        cb_dir = os.path.join(os.getcwd(), "CB_model")
        train_thread = train_model(cb_dir)
        train_thread.join()  # Wait for training to complete
        
        # Get recommendations
        print("Getting CB recommendations...")
        get_recommendations(cb_dir)
        
        # Check if recommendations were generated
        cb_recommendations = os.path.join("CB_model", "cb_recommendations.csv")
        if os.path.exists(cb_recommendations):
            print("[SUCCESS] CB recommendations generated successfully")
            return True
        else:
            print("[ERROR] CB recommendations not found")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error running CB model: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_hybrid_model():
    """Run Hybrid model and save results"""
    print("\n=== Running Hybrid Model ===")
    
    try:
        # Run the hybrid batch file
        result = subprocess.run(
            ["run_Hybrid.bat"],
            cwd=".",
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        print("Hybrid Model Output:")
        print(result.stdout)
        if result.stderr:
            print("Hybrid Model Errors:")
            print(result.stderr)
        
        # Check if hybrid results were generated
        hybrid_results = os.path.join("results", "hybrid_ranking.csv")
        if os.path.exists(hybrid_results):
            print("[SUCCESS] Hybrid recommendations generated successfully")
            return True
        else:
            print("[ERROR] Hybrid recommendations not found")
            return False
            
    except subprocess.TimeoutExpired:
        print("[ERROR] Hybrid model execution timed out")
        return False
    except Exception as e:
        print(f"[ERROR] Error running Hybrid model: {str(e)}")
        return False

def save_results(user_id, results_dir):
    """Save all three results for the current user"""
    print(f"\n=== Saving Results for User {user_id} ===")
    
    # Create user-specific results directory
    user_results_dir = os.path.join(results_dir, f"user_{user_id:02d}")
    os.makedirs(user_results_dir, exist_ok=True)
    
    # Copy KNN results
    knn_source = os.path.join("KNN_model", "rcm_games.csv")
    knn_target = os.path.join(user_results_dir, "knn_recommendations.csv")
    
    if os.path.exists(knn_source):
        shutil.copy2(knn_source, knn_target)
        print(f"[SUCCESS] Saved KNN results to {knn_target}")
    else:
        print("[ERROR] KNN results not found")
    
    # Copy CB results
    cb_source = os.path.join("CB_model", "cb_recommendations.csv")
    cb_target = os.path.join(user_results_dir, "cb_recommendations.csv")
    
    if os.path.exists(cb_source):
        shutil.copy2(cb_source, cb_target)
        print(f"[SUCCESS] Saved CB results to {cb_target}")
    else:
        print("[ERROR] CB results not found")
    
    # Copy Hybrid results
    hybrid_source = os.path.join("results", "hybrid_ranking.csv")
    hybrid_target = os.path.join(user_results_dir, "hybrid_recommendations.csv")
    
    if os.path.exists(hybrid_source):
        shutil.copy2(hybrid_source, hybrid_target)
        print(f"[SUCCESS] Saved Hybrid results to {hybrid_target}")
    else:
        print("[ERROR] Hybrid results not found")

def main():
    """Main function to run the automated test"""
    print("=" * 80)
    print("AUTOMATED TEST SCRIPT FOR STEAM ML RECOMMENDATION SYSTEM")
    print("=" * 80)
    
    # Define directories
    synthetic_data_dir = os.path.join(os.getcwd(), "synthetic_data")
    knn_model_dir = os.path.join(os.getcwd(), "KNN_model")
    user_data_dir = os.path.join(os.getcwd(), "user_data")
    results_dir = os.path.join(os.getcwd(), "test_results")
    
    # Create results directory
    os.makedirs(results_dir, exist_ok=True)
    
    # Process first 15 users
    for user_id in range(1, 16):
        print(f"\n{'='*60}")
        print(f"PROCESSING USER {user_id:02d}")
        print(f"{'='*60}")
        
        # Step 1: Copy user data
        if not copy_user_data(user_id, synthetic_data_dir, knn_model_dir, None, user_data_dir):
            print(f"[ERROR] Failed to copy data for user {user_id}")
            continue
        
        # Step 2: Run KNN model
        if not run_knn_model():
            print(f"[ERROR] KNN model failed for user {user_id}")
            continue
        
        # Step 3: Run CB model
        if not run_cb_model():
            print(f"[ERROR] CB model failed for user {user_id}")
            continue
        
        # Step 4: Run Hybrid model
        if not run_hybrid_model():
            print(f"[ERROR] Hybrid model failed for user {user_id}")
            continue
        
        # Step 5: Save all results
        save_results(user_id, results_dir)
        
        print(f"\n[SUCCESS] COMPLETED USER {user_id:02d}")
        
        # Small delay between users to avoid resource issues
        time.sleep(2)
    
    print("\n" + "=" * 80)
    print("AUTOMATED TEST COMPLETED")
    print("=" * 80)
    print(f"Results saved in: {results_dir}")
    print("You can now use these results for your report.")

if __name__ == "__main__":
    main()