
import requests

def gerar_texto_gemini(prompt, api_key):
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}
    data = {"contents":[{"parts":[{"text": prompt}]}]}
    response = requests.post(url, headers=headers, params=params, json=data, timeout=60)

    if response.status_code != 200:
        raise Exception(f"Erro Gemini {response.status_code}: {response.text}")

    result = response.json()
    return result["candidates"][0]["content"]["parts"][0]["text"]
