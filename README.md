# LinkedIn company url with employee count using selenium
---
## Required python(version >3.7)
---
#### playwright installation follow this link [playwright](https://playwright.dev/python/docs/intro)
### Run locally
1. Clone this repo.
2. Go to project in terminal   
3. Create virtual environment by running following command ( Note: if pipenv is not there the install it using ```pip install pipenv```)   
``` pipenv shell ```   
4. Run the followiing command to active virtual environment   
``` pipenv install ```
5. You need to add your linked in credential in base64 encode inside .env file as below  
```
LINKED_IN_EMAIL_ID=your email id in base64 format 
LINKED_IN_PASSWORD= your password in base64 format
```

5. Execute the following command to run uvicorn
``` uvicorn main:app --reload ```
6. You can now visitfastapi docs  for api text from [backend](http://127.0.0.1:8000/docs)
