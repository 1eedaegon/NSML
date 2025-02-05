# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 23:59:42 2018

@author: modes
"""
import os
import glob
import librosa
import numpy as np

"""
행,열 축을 변환하여 특성값을 추출하는 함수
stft(Short-time Fourier transform) :복소수 값을 갖는 행렬을 반환
mfcc(Mel-frequency cepstral coefficients), 
chroma_stft(chromagram from a waveform or power spectrogram), 
melspectrogram(Mel-scaled power spectrogram), 
spectral_contrast(spectral contrast), 
tonnetz(tonal centroid features) 
"""
def extract_feature(file_name):
    X, sample_rate = librosa.load(file_name) #부동 소수점 시계열로 로드, sample_rate:자동 리샘플링(default sr=22050) 
    stft = np.abs(librosa.stft(X))  #stft를 절대값으로 변환
    mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T,axis=0) #오디오 신호를 mfcc로 바꿈
    chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T,axis=0) # stft에서 chromagram 계산
    mel = np.mean(librosa.feature.melspectrogram(X, sr=sample_rate).T,axis=0) #melspectrogram
    contrast = np.mean(librosa.feature.spectral_contrast(S=stft, sr=sample_rate).T,axis=0) # spectral_contrast
    tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(X), sr=sample_rate).T,axis=0) #tonnetz
    return mfccs,chroma,mel,contrast,tonnetz

#hstack feature matrix : 추출한 값을 열을 기준으로 스택
def parse_audio_files(filenames):
    rows = len(filenames)
    features = np.zeros((rows,193))
    i = 0
    for f_names in filenames:
        mfccs, chroma, mel, contrast, tonnetz = extract_feature(f_names)
        features[i] = np.hstack([mfccs, chroma, mel, contrast, tonnetz])
        i += 1
    return features    

#file_list 생성
file = "C:/data/sound/audio_train/*.wav"
train_list=glob.glob(file)

file = "c:/data/sound/audio_test/*.wav"
test_list=glob.glob(file)

#extrect audio features : 함수 실행
feature_train = parse_audio_files(train_list)
feature_test = parse_audio_files(test_list)