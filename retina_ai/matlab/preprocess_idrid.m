%% IDRiD Fundus Preprocessing Pipeline for MATLAB
% Problem Statement ID: 26038 - Explainable AI for Diabetic Retinopathy
% MathWorks / Smart India Hackathon (SHS 2026)
%
% This script demonstrates standard ophthalmic fundus image preprocessing:
% 1. Retinal circular mask / Field-of-View (FOV) extraction
% 2. Green-channel extraction (highest retinal lesion contrast)
% 3. Contrast-Limited Adaptive Histogram Equalization (CLAHE)
% 4. Ben Graham's local color subtraction for illumination normalization

function [enhancedImg, fovMask] = preprocess_idrid(inputImagePath)
    if nargin < 1
        disp('Usage: [enhancedImg, fovMask] = preprocess_idrid(inputImagePath)');
        return;
    end

    % 1. Read input RGB fundus image
    rawImg = imread(inputImagePath);
    rawImg = im2double(rawImg);

    % 2. Extract Field of View (FOV) mask
    grayImg = rgb2gray(rawImg);
    fovMask = grayImg > 0.05;
    fovMask = imclose(fovMask, strel('disk', 15));
    fovMask = imfill(fovMask, 'holes');

    % 3. Extract green channel for microaneurysm & hemorrhage enhancement
    greenChannel = rawImg(:, :, 2);
    enhancedGreen = adapthisteq(greenChannel, 'ClipLimit', 0.02, 'Distribution', 'rayleigh');

    % 4. Ben Graham's method: scale and subtract local Gaussian blur
    blurred = imgaussfilt(rawImg, 10);
    enhancedImg = 4 * rawImg - 4 * blurred + 0.5;
    enhancedImg = max(min(enhancedImg, 1.0), 0.0);

    % Apply circular FOV mask
    for c = 1:3
        channel = enhancedImg(:, :, c);
        channel(~fovMask) = 0;
        enhancedImg(:, :, c) = channel;
    end

    fprintf('Successfully preprocessed fundus image: %s\n', inputImagePath);
end
