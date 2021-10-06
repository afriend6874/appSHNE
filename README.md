# appSHNE: The Application of Representation Learning for Semantic-Associated Heterogeneous Networks in Creating Android App Embedding Layers

This is the DSC 180 capstone project created by Alexander Friend, Braden Riggs, and Raya Kavosh. In this project we explore the implementation of both structured and unstructured app features in the creation of representative embedding layers. This  multi-faceted approach, at scale, offers researchers greater insight into the inner working of the app with deployment that ranges from malware detection to similarity search and link prediction. This work was based upon the heterogenous network learning methods for written text documents put forth in the paper *[SHNE: Representation Learning for Semantic-Associated Heterogeneous Networks](https://doi.org/10.1145/3289600.3291001)*, written by Chuxu Zhang, Ananthram Swami, and Nitesh V. Chawla.

Included in this repo is the source code for our project. More information is available in our [paper](https://briggs599.github.io/), as well as a [video](https://youtu.be/juyl_2602Mc) presenting our project and results.

## Usage

### ApkTool
This project requires docompiled Android app APK to Smali code. This can be done by using [ApkTool](https://ibotpeaches.github.io/Apktool/). For more information on Andorid apps and Smali code read through these [slides](http://www.syssec-project.eu/m/page-media/158/syssec-summer-school-Android-Code-Injection.pdf).

### Docker
A Docker image to run this project on the UCSD DSMLP servers is available [here](https://hub.docker.com/repository/docker/apfriend/dsc180-shne-env) and can be pulled with the command:

    docker push apfriend/dsc180-shne-env:latest

### Running the project

This code can be run from the command line by running:

    python run.py [OPTIONS]

Valid options are:

    -test,"-Test", -t       Run on test set instead of full set of Android apps
    -silent                 Hide outputs from command line
    --save-out", -log       Keep a log of command line outputs in file saved in configured 
    -time                   Keep track of how long to run and output time to complete when finished running
    -eda                    Run EDA section only
    --force-single          Force to run on single process
    --force-multi           Force to run useing multi-processing
    --show-params           Print out parameters passed in command line

The paths to malicious and benign test app decompile apks should be set in `mal_fp_test` and `ben_fp_test`, respectively, in the configuration file `config/params.json`. The paths to malicious and benign training app decompile apks should be set in `mal_fp` and `ben_fp`, respectively, in the configuration file `config/params.json`. 

## Update History

### 10.5.2021 updates - Alex
- Updated Dockerfile as it was changed during merge
- Updated README.md file


### 3.8.2021 updates - Alex
- wrote EDA notebook that is callable from command line
    - Run EDA with the following command line parameter: `-eda`
    - EDA can be run with the following parameters: `time` and `limit`
        - `python run.py -eda -time` will run the EDA and print the time to run it on completion
- Cleaned old code and adding documentation
- To do: 
    - Clean up parameters in `config/params.json` and delete unused parameters
    - Remove unused methods
    - update dockerfile with `nbconvert` and `pandoc` to run `EDA.ipynb` from command line
    - Run EDA on 1000 apps

### 3.5.2021 updates - Alex
- added argument `-log` for the `<redirect_std_out>` (save console output to log file) parameter 
- Moved SHNE_code to `src` directory

### 3.2.2021 updates - Alex

#### `run.py` has been updated to include more command line arguments
- `-t`, `-test`, `-Test`: Run on test set 
- `-node2vec`, `-n2v`: Run with node2vec instead of word2vec
- `--skip-embeddings`: Skip the word embeddings stage 
- `--skip-shne`: Skip SHNE model creation final step
- `-p`, `-parse`: Only create node dictionaries `dict_A.json`, `dict_B.json`, `dict_P.json`, `dict_I.json`, `api_calls.json`, and `naming_key.json`
- `-o`, `-overwrite`: Overwrite previous node dictionaries created when parsing
- `--save-out`: Save console output to file 
- `-time`: time how long to run `main.py`

#### Updated params config file. All parameters used are now found in `config/params.json`.
- All outputs will be saved under the values for `<out_path>` and `<test_out_path>`
    - Subdirectories to save configured in respective dictionary. 
        - For instance word2vec embeddings will be saved under the path `<save_dir>` in the `<word2vec-params>` dictionary int `config/params.json`
- All filenames parameterizable 
    