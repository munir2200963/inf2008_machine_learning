# Overview

This is our **INF2008 Machine Learning** project, proudly created by **Team 19 P1** consisting of:

- NG WEI SHEN, JACKSON
- MUNIR RUDY HERMAN
- NURTIARA TANIA RAHIM
- NICHOLAS PHOON KAI JIN
- JOLIN TAN

In this project, we are tackling a **Speaker Verification** task, where we determine whether a given audio sample belongs to a specific speaker. We use a **binary classifier** to accomplish this task. 

The benchmark we are comparing against is based on **Prof. Xiao Xiao’s paper**, which reported an **Equal Error Rate (EER) of 4.59%** on their dataset, achieved using the state-of-the-art **ECAPA-TDNN** deep learning model.

Our team utilized three feature engineering methods:
1. **Product and Difference between embeddings**
2. **Manhattan distance between embeddings**
3. **Clustering with HDBSCAN**

We tested three different models:
- **Logistic Regression**
- **XGBoost**
- **Support Vector Machine (SVM)**

Among these, **SVM** achieved the best **EER of 3.53%**, successfully outperforming the benchmark.

Additionally, we developed a **demo** to provide a clearer understanding of our task and its implementation.

# Project Structure

This repository contains the necessary files and directories for the `inf2008_machine_learning` project. Below is the directory tree with explanations for each component.

```
inf2008_machine_learning/
├── demo/                           # Contains the code for both the frontend and backend of the demo
├── extraction_models/              # Contains Jupyter notebooks that were used to use the model and extract embeddings from the wav file
│
├── test_set/                       # Dataset used for testing the model (Same test set as benchmark for fair comparison)
│   ├── data/                        # Raw test data (Speaker embeddings, combined speaker embeddings and trial embeddings)
│   ├── feature_vector/              # Extracted feature vectors for test data
│
├── training_set/                    # Dataset used for training the model (Distinct from test set to prevent data leakage)
│   ├── data/                         
│   ├── feature_vector/              
│
├── validation_set/                  # Dataset used for hyperparameter tuning.
│   ├── data/                        
│   ├── feature_vector/              
│
├── feature_engineering.ipynb        # Jupyter notebook for feature extraction and preprocessing
├── model_training_and_eval.ipynb    # Jupyter notebook for training and evaluating the model
├── utils.py                         # Utility functions used in both notebooks above.
```

# Setting Up Demo

Follow these steps to set up and run the demo:

### 1. Install Required Packages
Run the following command to install all dependencies from the `requirements.txt` file:
```sh
pip install -r requirements.txt
```

### 2. Install `ffmpeg`
Navigate to the backend directory and install `ffmpeg`:
```sh
cd demo/src/backend
sudo apt-get update
sudo apt-get install ffmpeg
```

### 3. Install the TTS Package
Install the TTS package directly from GitHub:
```sh
pip install git+https://github.com/munir2200963/TTS.git
```

### If Step 3 Fails, Follow These Steps:
#### 3a) Clone the TTS Repository
```sh
git clone https://github.com/munir2200963/TTS.git
```

For some reason, the TTS repository is nested within another TTS folder. Follow these steps to fix it:
- **Drag the nested TTS folder out** and rename it to `TTS1`.
- Delete the old `TTS` folder.
- Rename `TTS1` back to `TTS`.

### 4. Install Additional Dependencies
Install the necessary libraries:
```sh
sudo apt-get install -y espeak libsndfile1
```

### 5. Download TTS Model
Download the pre-trained TTS model:
```sh
wget https://coqui.gateway.scarf.sh/v0.7.0_models/tts_models--en--blizzard2013--capacitron-t2-c50.zip
```

### 6. Unzip the Model
Extract the contents of the downloaded `.zip` file:
```sh
unzip '*.zip'
```

### 7. Downgrade Dependencies (If Required)
You might need to downgrade `torchaudio` and `torch` to fix the weight loading issue. Run the following commands:
```sh
pip install torchaudio==2.5.0
pip install torch==2.5.0
```

If the above doesn’t work, you can modify the `TTS/utils/io.py` file:
- Go to **Line 54** and change:
```python
return torch.load(f, map_location=map_location, **kwargs)
```
To:
```python
return torch.load(f, map_location=map_location, weights_only=False, **kwargs)
```

### 8. Start the Backend Server
Run the backend server:
```sh
python3 server.py
```

### 9. Start the Frontend
In a **new terminal**, navigate back to the `demo` directory and run:
```sh
cd demo
npm install
npm start
```

# Presentation Video

You can watch the presentation video here:

[![Watch the Presentation Video](https://img.youtube.com/vi/bt7mSbaJRyk/0.jpg)](https://www.youtube.com/watch?v=bt7mSbaJRyk)

# Who to Contact

For any inquiries or further information, please reach out to:

**Munir**  
Email: [2200963@sit.singaporetech.edu.sg](mailto:2200963@sit.singaporetech.edu.sg)