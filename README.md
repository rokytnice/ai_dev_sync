# AI Agents 
## Goal: ai agents acts file based 

## Overview
This repository is designed for managing files, constructing API prompts, and interacting with the Gemini language model to generate or manipulate content based on specified patterns and requirements. Key functionalities include:

- **API Client**: Handles communication with the Gemini API for generating content based on prompts.
- **File Management**: Facilitates reading, writing, and managing file content, including Java files and configuration files.
- **Prompt Processor**: Constructs prompts by aggregating content from specified files or directories.
- **Response Handler**: Processes API responses to extract and update Java files.

---

## Project Structure

### Key Components

1. **APIClient**
   - Manages API interactions.
   - Provides methods to send prompts and display progress.
   
2. **FileManager**
   - Handles file search, read, write, and diff logging.
   - Ensures directories are created when writing files.

3. **PromptProcessor**
   - Constructs prompts from specified file paths and patterns.
   - Aggregates file content for API requests.

4. **ResponseHandler**
   - Processes API responses to extract Java code blocks.
   - Updates files with extracted content.

### Supporting Files
- `app.log`: Logs application activities.
- `.env`: Stores the `GEMINI_API_KEY` (not included in the repository for security reasons).

---

## Prerequisites

- **Python 3.8+**
- Required Libraries:
  - `os`
  - `json`
  - `logging`
  - `requests`
  - `difflib`
  - `itertools`
  - `sys`
  - `time`
  - `pathlib`
  - `typing`
  - `threading`

Install dependencies using:
```bash
pip install -r requirements.txt
```

---

## Usage

### Environment Setup
1. Set the `GEMINI_API_KEY` as an environment variable:
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

2. Define the base directory where files are located in the script.

### Running the Application
Execute the main script:
```bash
python main.py
```

### Example Prompt
The example provided builds a security concept based on BSI Grundschutz, evaluates files in the directory, and processes the API response to update Java files.

### Logging
Logs are available in the `app.log` file and the console. To modify the log level, adjust the `logging.basicConfig` configuration.

---

## Features

1. **Dynamic Prompt Generation**
   - Aggregates file content based on patterns and constructs a detailed prompt for the API.

2. **API Communication**
   - Interacts with Gemini API to generate meaningful responses.
   - Displays progress during API requests.

3. **File Handling**
   - Reads, writes, and updates files while logging differences.
   - Ensures file structure integrity during write operations.

4. **Java File Parsing**
   - Extracts Java code blocks from API responses.
   - Identifies package names and class names to update files appropriately.

---

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Commit changes and submit a pull request.

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

## Acknowledgments
- Built with inspiration from the Gemini API documentation and Python's rich library ecosystem.

