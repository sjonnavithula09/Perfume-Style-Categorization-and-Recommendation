# Perfume Style Categorization and Recommendation

## Project Description and Overview
Perfume Season and Gender Recommendation System is a lightweight, interpretable framework designed to recommend perfumes based on season (Summer, Fall, Winter) and gender (Female, Male, Unisex).  
Most publicly available fragrance datasets lack contextual attributes such as season or audience. This project bridges that gap by applying natural language processing (NLP) and rule-based inference to extract meaningful insights from textual fragrance descriptions.

The system integrates:
- Data ingestion and preprocessing  
- TF–IDF–based text feature extraction  
- Lexicon-driven inference for season and gender prediction  
- Weighted scoring and ranking of perfumes  
- A real-time Streamlit interface for user interaction and visualization

This implementation emphasizes interpretability, transparency, and reproducibility, enabling users to explore recommendations in an accessible and explainable manner.

---

## Repository Structure
```text
Perfume-Style-Categorization-and-Recommendation/
│
├── data/                               # Cleaned and processed data
│   ├── clean_perfume_data.csv
│   └── final_perfume_data.csv
│
├── notebooks/                          # Jupyter notebooks for data prep and modeling
│   ├── 01_data_cleaning.ipynb
│   └── 02_perfume_recommender.ipynb
│
├── results/                            # Generated datasets, scores, and logs
│   ├── enriched_perfume_data.csv
│   ├── season_gender_keyword_scores.csv
│   └── feedback_log.csv                # Stored user feedback from the interface
│
├── streamlit.py                        # Main Streamlit interface file
├── Interface Video.mp3                 # Demo video walkthrough of the UI
│
└── README.md                           # Project documentation
                         
```
## Instructions for Running the Model and Launching the Interface
1. Clone the Repository
   ```sh
   git clone https://github.com/sjonnavithula09/Perfume-Style-Categorization-and-Recommendation.git
   cd Perfume-Style-Categorization-and-Recommendation
   ```
2. Launch the Streamlit Interface
   From the project root directory, execute:
   ```sh
   streamlit run streamlit.py
   ```
4. Using the Interface

- Select one Season (Summer, Fall, Winter).

- Select one Gender (Female, Male, Unisex).

- Adjust the Top-k slider (5–24) to control the number of recommendations.

- The results will display perfume name, brand, image, and primary notes in ranked order.

 ## Results

- Seasonal inference accuracy: approximately 85%

- Gender classification precision: approximately 90%

- Average Top-10 recommendation score: 0.82

- Distribution analysis confirms semantic consistency across inferred categories.

## Known Issues

- Some perfumes contain minimal or ambiguous note descriptions, leading to uncertain classifications.

- A few image URLs may not render due to broken external links.

- Minor layout inconsistencies may occur on different screen resolutions or browsers.

## Author and Contact Information

Srinija Jonnavithula
Master’s in Applied Data Science
University of Florida, Gainesville, USA

Email: sjonnavithula09@ufl.edu

GitHub: https://github.com/sjonnavithula09
