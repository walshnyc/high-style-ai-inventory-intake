# High Style AI – Inventory Intake Task 2.7: Feedback Retry Loop

This version changes feedback from a post-save note into an editing loop.

## New workflow

1. Generate Draft Item Record
2. Review the AI output
3. Add feedback
4. Click `Try Again With Feedback`
5. AI revises the draft
6. Repeat if needed
7. Click `Approve & Save to Google Sheet`
8. Click `Submit Another Entry`

## It keeps

- HEIC / HEIF support
- photo uploader reset fix
- Cloudinary thumbnail upload
- Google Sheet save
- Learning_Log tracking

## Launch

```bash
cd ~/Downloads/High_Style_AI_Inventory_Intake_Task2_7_Feedback_Retry_Loop
pip3 install -r requirements.txt
export OPENAI_API_KEY="your_openai_key"
export CLOUDINARY_CLOUD_NAME="your_cloud_name"
export CLOUDINARY_API_KEY="your_cloudinary_api_key"
export CLOUDINARY_API_SECRET="your_cloudinary_api_secret"
streamlit run app.py
```
