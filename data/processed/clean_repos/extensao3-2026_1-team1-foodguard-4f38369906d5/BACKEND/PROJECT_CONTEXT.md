# FoodGuard: Project Context

## Project Overview

[cite_start]FoodGuard is a web platform developed to identify allergenic components in food products, aiming to prevent adverse reactions in users[cite: 26]. [cite_start]The tool provides an agile and intuitive solution for interpreting food labels by cross-referencing nutritional data with a user's medical history (anamnesis) provided during registration[cite: 27].

## Technical Architecture

The application is built using a modern stack consisting of React for the frontend and Django for the backend. The core functionality relies on two main artificial intelligence integrations:

- [cite_start]**Computer Vision:** The system uses a Yolov8n model integrated with the ONNX Runtime-web library to process images and extract data from product barcodes[cite: 28].
- [cite_start]**Natural Language Processing (NLP):** The system utilizes the Gemini LLM to analyze text descriptions, cross-referencing food data with the user's anamnesis to provide personalized safety verifications[cite: 29].

## Core Mechanics

The primary interaction occurs through an AI-powered chat interface. [cite_start]Users can either type text queries about a specific food or upload an image of a product's barcode[cite: 29, 96, 107]. [cite_start]The system then queries an external food API to retrieve ingredients and potential allergens based on the barcode[cite: 112]. [cite_start]Finally, the LLM processes this external data against the user's private anamnesis to generate a customized, safe consumption recommendation[cite: 101, 102, 113].
