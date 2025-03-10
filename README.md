# songseeker-hitster-playlists-generator

A tool to help generating CSV files containing Youtube links to the Hitster playing cards

I used "Le Chat Pro" AI from Mistral, to help me scripting this tool.

Basically it's a tool made to generate Youtube URL, Youtube title and Hashed Info for the CSV used by songseeker (for Hitster Game) from an incomplete CSV with at least Card#, Artist, Title, and Year.

## Build

```bash
docker build -t songseeker-hitster-playlists-generator .
```

## Usage

First create a temporary folder where you'll put the pre-complete CSV named `file.csv` (you need at least in the CSV file the columns Card#, Artist, Title and Year, you can find and example `file-example.csv`)

```bash
docker run --rm -it -v <your_temporary_folder>:/tmp/ -e YOUTUBE_API_KEY=<YOUR_YOUTUBE_API_KEY> songseeker-hitster-playlists-generator
```
