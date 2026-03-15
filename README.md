# 🚀 Project Overview

This project contains a directory structure with Python scripts and data related to various fields. Below is an overview of each directory.

## 📂 Directory Structure

### 🎮 make_game
Contains scripts and resources related to game development. You can create various games using scripts such as `galaga.py`, `invader.py`, `othello.py`, and `quiz.py`.

### 🤖 openai_test
Contains scripts for testing OpenAI functionality. Includes demos for JSON formatting (`openai_json_format.py`), translation features (`openai_translator.py`), and paper review (`paper_review.py`).

### 🧠 RL_code
Contains code related to reinforcement learning. You can implement reinforcement learning algorithms using `RLgym.py` and `RLPolicyGradient.py`. Includes saved policy network checkpoints and demo videos in the `video` directory.

### 📊 robot_graph
Contains scripts and data related to robot graphs. Includes scripts for graph visualization (`dependency_visualization.svg`), data transformation (`rdf2neo4j.py`), and cypher queries (`cypher_queries.txt`).

### 📄 pdf2text
Contains scripts for extracting text from PDF files. Includes `extract_pdf_text.py` for converting PDFs to text.

### 🔍 gemini_embedding2_test
Contains scripts for exploring multimodal embeddings and comparing various image/PDF search techniques.
- `embedding_test.py`: Script to test **Gemini Embedding 2**'s multimodal capabilities, mapping both images and text into the same vector space to compute cosine similarities. Also demonstrates secure API key management using `.env`.
- `extract_with_embedding.py`: Uses **Gemini Embedding 2** to search and extract specific PDF pages based on abstract "meaning" or "vibe" queries. Not suitable for exact pixel-perfect matches (e.g., small logos).
- `extract_pdf_pages.py`: Uses **OpenCV Template Matching** for finding exact pixel matches of an image inside PDFs. Highly sensitive to scale and rotation.
- `extract_pdf_pages_sift.py`: Uses **OpenCV SIFT Feature Matching**. The most robust, accurate, and fast method for finding specific geometric shapes or logos inside a PDF document, as it is invariant to scale and rotation.

## 📝 Root Scripts

- `ner_test.py`: Script for testing Named Entity Recognition (NER) functionality.

## 🛠️ Usage

Each directory contains specific tools and scripts that can be used according to their respective documentation.

## 📝 Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements.

## 📜 License

This project is available for internal use and testing purposes.
